"""
AWS Lambda Function: S3 Event Trigger -> Auto ETL Execution
Automatically executes ETL process when new discount pamphlets (PDF/CSV) are uploaded to S3 bucket.

Trigger Conditions:
- S3 object creation event
- File extensions: .pdf, .csv
- File name pattern: Contains week_special

Features:
1. Extract file information from S3 events
2. Validate file type (PDF/CSV)
3. Execute ETL process
4. Update database
5. Send notifications and logging
"""

import json
import boto3
import os
import urllib.parse
from typing import Dict, Any, List
import logging
from datetime import datetime

# Logging configuration
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS client initialization
s3_client = boto3.client('s3')
lambda_client = boto3.client('lambda')
sns_client = boto3.client('sns')

# Environment variables
ETL_PROCESSOR_LAMBDA_ARN = os.environ.get('ETL_PROCESSOR_LAMBDA_ARN')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')
ALLOWED_FILE_PATTERNS = ['week_special', 'discount', 'pamphlet']
ALLOWED_EXTENSIONS = ['.pdf', '.csv']

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    S3 event trigger main handler
    """
    try:
        logger.info(f"S3 event received: {json.dumps(event)}")
        
        # Process S3 event records
        processed_files = []
        errors = []
        
        for record in event.get('Records', []):
            try:
                file_info = extract_s3_file_info(record)
                
                if should_process_file(file_info):
                    logger.info(f"Processing file: {file_info['key']}")
                    
                    # Trigger ETL processor
                    etl_result = trigger_etl_processor(file_info)
                    processed_files.append({
                        'file': file_info['key'],
                        'result': etl_result
                    })
                else:
                    logger.info(f"Skipping file (conditions not met): {file_info['key']}")
            
            except Exception as e:
                error_msg = f"S3 record processing error: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        # Send summary notification
        if processed_files or errors:
            send_trigger_summary_notification(processed_files, errors)
        
        return {
            'statusCode': 200,
            'body': {
                'processed_files': len(processed_files),
                'errors': len(errors),
                'details': {
                    'files': processed_files,
                    'errors': errors
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Lambda execution failed: {str(e)}")
        return {
            'statusCode': 500,
            'body': {
                'error': str(e)
            }
        }

def extract_s3_file_info(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract file information from S3 event record
    """
    try:
        s3_info = record['s3']
        bucket = s3_info['bucket']['name']
        key = urllib.parse.unquote_plus(s3_info['object']['key'])
        size = s3_info['object']['size']
        
        # Determine file type from extension
        file_extension = os.path.splitext(key)[1].lower()
        
        if file_extension == '.pdf':
            file_type = 'pdf'
        elif file_extension == '.csv':
            file_type = 'csv'
        else:
            file_type = 'unknown'
        
        return {
            'bucket': bucket,
            'key': key,
            'size': size,
            'extension': file_extension,
            'file_type': file_type,
            'event_time': record.get('eventTime', datetime.utcnow().isoformat())
        }
        
    except KeyError as e:
        raise ValueError(f"Invalid S3 event record structure: {str(e)} missing")

def should_process_file(file_info: Dict[str, Any]) -> bool:
    """
    Determine if file should be processed by ETL
    """
    key = file_info['key'].lower()
    extension = file_info['extension']
    
    # Check file extension
    if extension not in ALLOWED_EXTENSIONS:
        logger.info(f"File extension {extension} not in allowed list: {ALLOWED_EXTENSIONS}")
        return False
    
    # Check filename pattern
    pattern_match = any(pattern in key for pattern in ALLOWED_FILE_PATTERNS)
    if not pattern_match:
        logger.info(f"Filename does not match required patterns: {ALLOWED_FILE_PATTERNS}")
        return False
    
    # Check file size (minimum 100 bytes)
    if file_info['size'] < 100:
        logger.info(f"File too small: {file_info['size']} bytes")
        return False
    
    logger.info(f"File meets all conditions for processing")
    return True

def trigger_etl_processor(file_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Trigger ETL processor Lambda function
    """
    try:
        # Prepare payload for ETL processor
        payload = {
            'bucket': file_info['bucket'],
            'key': file_info['key'],
            'file_type': file_info['file_type'],
            'trigger_time': file_info['event_time'],
            'file_size': file_info['size']
        }
        
        logger.info(f"Triggering ETL processor with payload: {payload}")
        
        # Invoke ETL processor Lambda asynchronously
        if ETL_PROCESSOR_LAMBDA_ARN:
            response = lambda_client.invoke(
                FunctionName=ETL_PROCESSOR_LAMBDA_ARN,
                InvocationType='Event',  # Asynchronous invocation
                Payload=json.dumps(payload)
            )
            
            logger.info(f"ETL processor invoked successfully. Response: {response['StatusCode']}")
            
            return {
                'status': 'triggered',
                'lambda_status_code': response['StatusCode'],
                'invocation_type': 'asynchronous'
            }
        else:
            logger.warning("ETL_PROCESSOR_LAMBDA_ARN not configured")
            return {
                'status': 'skipped',
                'reason': 'ETL processor Lambda ARN not configured'
            }
            
    except Exception as e:
        logger.error(f"ETL processor trigger failed: {str(e)}")
        raise

def send_trigger_summary_notification(processed_files: List[Dict], errors: List[str]):
    """
    Send summary notification for trigger results
    """
    if not SNS_TOPIC_ARN:
        logger.info("SNS topic not configured, skipping notification")
        return
    
    try:
        # Prepare message
        message_parts = [
            "🚀 UrSaviour ETL Trigger Summary",
            f"⏰ Trigger Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            ""
        ]
        
        if processed_files:
            message_parts.append(f"✅ Successfully Processed Files ({len(processed_files)}):")
            for file_info in processed_files:
                message_parts.append(f"  • {file_info['file']}")
            message_parts.append("")
        
        if errors:
            message_parts.append(f"❌ Errors ({len(errors)}):")
            for error in errors:
                message_parts.append(f"  • {error}")
            message_parts.append("")
        
        message_parts.append("📊 Processing Status:")
        message_parts.append(f"  • Processed Files: {len(processed_files)}")
        message_parts.append(f"  • Errors: {len(errors)}")
        
        if processed_files:
            message_parts.append("\n💡 ETL processing has started.")
            message_parts.append("Check ETL processor logs for detailed results.")
        
        message = "\n".join(message_parts)
        
        # Send notification
        subject = f"UrSaviour ETL Trigger - {len(processed_files)} Files Processed"
        
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message
        )
        
        logger.info("Trigger summary notification sent successfully")
        
    except Exception as e:
        logger.error(f"Failed to send trigger summary notification: {str(e)}")

def get_file_metadata(bucket: str, key: str) -> Dict[str, Any]:
    """
    Get additional file metadata from S3
    """
    try:
        response = s3_client.head_object(Bucket=bucket, Key=key)
        
        return {
            'last_modified': response.get('LastModified'),
            'content_type': response.get('ContentType'),
            'content_length': response.get('ContentLength'),
            'etag': response.get('ETag'),
            'metadata': response.get('Metadata', {})
        }
        
    except Exception as e:
        logger.warning(f"Cannot get metadata for {key}: {str(e)}")
        return {}

def validate_s3_object(bucket: str, key: str) -> bool:
    """
    Validate that S3 object exists and is accessible
    """
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except Exception as e:
        logger.error(f"S3 object validation failed for {bucket}/{key}: {str(e)}")
        return False

# Test and debugging utility functions

def create_test_event(bucket: str, key: str, event_name: str = "ObjectCreated:Put") -> Dict[str, Any]:
    """
    Create test S3 event for development/testing
    """
    return {
        "Records": [
            {
                "eventVersion": "2.1",
                "eventSource": "aws:s3",
                "awsRegion": "ap-southeast-2",
                "eventTime": datetime.utcnow().isoformat() + "Z",
                "eventName": event_name,
                "s3": {
                    "s3SchemaVersion": "1.0",
                    "configurationId": "etl-trigger",
                    "bucket": {
                        "name": bucket,
                        "ownerIdentity": {"principalId": "test"}
                    },
                    "object": {
                        "key": key,
                        "size": 1024,
                        "eTag": "test-etag"
                    }
                }
            }
        ]
    }

def log_environment_info():
    """
    Log current environment configuration for debugging
    """
    logger.info("Environment Configuration:")
    logger.info(f"  ETL_PROCESSOR_LAMBDA_ARN: {'Configured' if ETL_PROCESSOR_LAMBDA_ARN else 'Not configured'}")
    logger.info(f"  SNS_TOPIC_ARN: {'Configured' if SNS_TOPIC_ARN else 'Not configured'}")
    logger.info(f"  ALLOWED_FILE_PATTERNS: {ALLOWED_FILE_PATTERNS}")
    logger.info(f"  ALLOWED_EXTENSIONS: {ALLOWED_EXTENSIONS}")

# Initialize environment logging
log_environment_info()
