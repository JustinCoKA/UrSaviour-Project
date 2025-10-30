"""
AWS Lambda Function: ETL Processor
Downloads discount pamphlets from S3, extracts data, and updates the database.

Features:
1. Download PDF/CSV files from S3
2. Extract data based on file type
3. Transform and normalize data
4. Delete existing storeOfferings table data
5. Replace with new discount data
6. Log execution results and send notifications
"""

import json
import boto3
import os
import tempfile
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import pymysql
import io
import csv
import re

# PDF processing library (requires Lambda Layer)
try:
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
    print(f"PyMuPDF successfully imported! Version: {fitz.version}")
except ImportError as e:
    PDF_AVAILABLE = False
    print(f"PyMuPDF import failed: {e}")
    logging.warning("PyMuPDF not available - PDF processing disabled")

# Logging configuration
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
s3_client = boto3.client('s3')
sns_client = boto3.client('sns')

# Environment variables
DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME', 'ursaviourDb')  # Default to correct DB name
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    ETL processor main handler with database testing capability
    """
    try:
        logger.info(f"ETL Processor started with event: {json.dumps(event)}")
        
        # Database test mode
        if event.get('test_database'):
            logger.info("Running in database test mode")
            return test_database_connection(event)
        
        # Validate environment variables
        validate_environment()
        
        # Extract input parameters - Support new payload format
        if 'bucket_name' in event and 'object_key' in event:
            # New format
            bucket = event['bucket_name']
            key = event['object_key']
            file_type = 'csv' if key.lower().endswith('.csv') else 'pdf'
            trigger_time = datetime.now().isoformat()
        else:
            # Existing format
            bucket = event['bucket']
            key = event['key']
            file_type = event['file_type']
            trigger_time = event.get('trigger_time')
        
        logger.info(f"Processing file: s3://{bucket}/{key} (type: {file_type})")
        
        # Execute ETL pipeline
        result = execute_etl_pipeline(bucket, key, file_type, trigger_time)
        
        # Send success notification
        send_success_notification(key, result)
        
        return {
            'statusCode': 200,
            'body': {
                'success': True,
                'file': key,
                'result': result
            }
        }
        
    except Exception as e:
        logger.error(f"ETL processing failed: {str(e)}")
        
        # Send failure notification
        send_error_notification(event.get('key', event.get('object_key', 'unknown')), str(e))
        
        return {
            'statusCode': 500,
            'body': {
                'success': False,
                'error': str(e)
            }
        }

def test_database_connection(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Test database connection and check current status
    """
    try:
        logger.info("Testing database connection...")
        
        # Check environment variables
        db_config = {
            'host': DB_HOST,
            'user': DB_USER,
            'password': DB_PASSWORD,
            'database': DB_NAME
        }
        
        logger.info(f"DB Config: host={DB_HOST}, user={DB_USER}, database={DB_NAME}")
        
        # Database connection
        connection = get_db_connection()
        
        result = {
            'database_test': 'SUCCESS',
            'timestamp': datetime.now().isoformat(),
            'tables': {}
        }
        
        with connection.cursor() as cursor:
            # Check status of each table
            tables = ['storeOfferings', 'etljob', 'etljoblog']
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                result['tables'][table] = {'count': count}
                
                # Recent record samples
                if table == 'etljob' and count > 0:
                    cursor.execute("SELECT jobNumber, timestamp, overallStatus, totalItemExtracted, totalItemLoaded FROM etljob ORDER BY timestamp DESC LIMIT 3")
                    recent_jobs = cursor.fetchall()
                    result['tables'][table]['recent_jobs'] = [
                        {
                            'jobNumber': job[0],
                            'timestamp': str(job[1]),
                            'status': job[2],
                            'extracted': job[3],
                            'loaded': job[4]
                        } for job in recent_jobs
                    ]
                
                elif table == 'storeOfferings' and count > 0:
                    cursor.execute("SELECT storeName, productName, originalPrice, discountedPrice FROM storeOfferings LIMIT 5")
                    sample_offerings = cursor.fetchall()
                    result['tables'][table]['samples'] = [
                        {
                            'store': offering[0],
                            'product': offering[1],
                            'original': str(offering[2]),
                            'discounted': str(offering[3])
                        } for offering in sample_offerings
                    ]
        
        connection.close()
        
        logger.info("Database connection test successful")
        
        # Also run test for actual ETL execution
        if event.get('object_key'):
            logger.info("Running ETL test with provided file...")
            
            bucket = event['bucket_name']
            key = event['object_key']
            file_type = 'csv' if key.lower().endswith('.csv') else 'pdf'
            
            # Execute ETL pipeline
            etl_result = execute_etl_pipeline(bucket, key, file_type, datetime.now().isoformat())
            result['etl_test'] = etl_result
        
        return {
            'statusCode': 200,
            'body': result
        }
        
    except Exception as e:
        logger.error(f"Database test failed: {str(e)}")
        return {
            'statusCode': 500,
            'body': {
                'database_test': 'FAILED',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
        }

def execute_etl_pipeline(bucket: str, key: str, file_type: str, trigger_time: str) -> Dict[str, Any]:
    """
    Execute ETL pipeline
    """
    start_time = datetime.utcnow()
    job_id = None
    
    try:
        # Log ETL job start
        job_id = log_etl_job_start(key, file_type, start_time)
        log_etl_message(job_id, "INFO", f"ETL pipeline started for file: {key}")
        
        # 1. Extract: Download file from S3 and extract data
        logger.info("Step 1: Extracting data from file")
        log_etl_message(job_id, "INFO", "Step 1: Extracting data from file")
        
        extracted_data = extract_data_from_s3(bucket, key, file_type)
        
        if not extracted_data:
            raise ValueError("No data extracted from file")
        
        logger.info(f"Extracted {len(extracted_data)} records")
        log_etl_message(job_id, "INFO", f"Extracted {len(extracted_data)} records")
        
        # 2. Transform: Data transformation and normalization
        logger.info("Step 2: Transforming data")
        log_etl_message(job_id, "INFO", "Step 2: Transforming data")
        
        transformed_data = transform_discount_data(extracted_data)
        
        if not transformed_data:
            raise ValueError("No valid data after transformation")
        
        logger.info(f"Transformed to {len(transformed_data)} valid records")
        log_etl_message(job_id, "INFO", f"Transformed to {len(transformed_data)} valid records")
        
        # 3. Load: Update database
        logger.info("Step 3: Loading data to database")
        log_etl_message(job_id, "INFO", "Step 3: Loading data to database")
        
        db_result = load_data_to_database(transformed_data)
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        result = {
            'records_extracted': len(extracted_data),
            'records_transformed': len(transformed_data),
            'records_loaded': db_result['records_inserted'],
            'processing_time_seconds': processing_time,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'database_operations': db_result
        }
        
        # Log ETL job completion
        log_etl_job_complete(job_id, end_time, "success", len(extracted_data), len(transformed_data))
        log_etl_message(job_id, "INFO", f"ETL pipeline completed successfully. Loaded {db_result['records_inserted']} records")
        
        logger.info(f"ETL pipeline completed successfully: {result}")
        return result
        
    except Exception as e:
        # Log ETL job failure
        end_time = datetime.utcnow()
        if job_id:
            log_etl_job_complete(job_id, end_time, "failed", 0, 0)
            log_etl_message(job_id, "ERROR", f"ETL pipeline failed: {str(e)}")
        raise

def extract_data_from_s3(bucket: str, key: str, file_type: str) -> List[Dict[str, Any]]:
    """
    Download file from S3 and extract data
    """
    try:
        # Download file from S3
        with tempfile.NamedTemporaryFile() as temp_file:
            s3_client.download_file(bucket, key, temp_file.name)
            
            if file_type == 'pdf':
                return extract_from_pdf(temp_file.name)
            elif file_type == 'csv':
                return extract_from_csv(temp_file.name)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
                
    except Exception as e:
        logger.error(f"Error extracting data from S3: {str(e)}")
        raise

def extract_from_pdf(file_path: str) -> List[Dict[str, Any]]:
    """
    Extract discount information from PDF file
    """
    if not PDF_AVAILABLE:
        raise ValueError("PDF processing unavailable - PyMuPDF not installed")
    
    try:
        doc = fitz.open(file_path)
        full_text = ""
        
        logger.info(f"PDF opened successfully. Total pages: {len(doc)}")
        
        for page in doc:
            page_text = page.get_text("text")
            logger.info(f"DEBUG: Page {page.number} text length: {len(page_text)} chars")
            logger.info(f"DEBUG: Page {page.number} first 200 chars: {repr(page_text[:200])}")
            full_text += page_text
        
        doc.close()
        logger.info(f"Successfully extracted text from PDF. Total text length: {len(full_text)} chars")
        logger.info(f"DEBUG: Full text first 500 chars: {repr(full_text[:500])}")
        
        # Parse discount information from PDF text
        parsed_data = parse_discount_text(full_text)
        logger.info(f"DEBUG: Parsed {len(parsed_data)} records from PDF text")
        return parsed_data
        
    except Exception as e:
        logger.error(f"Error extracting from PDF: {str(e)}")
        raise

def extract_from_csv(file_path: str) -> List[Dict[str, Any]]:
    """
    Extract discount information from CSV file
    """
    try:
        data = []
        with open(file_path, 'r', encoding='utf-8') as file:
            # Handle BOM
            content = file.read()
            if content.startswith('\ufeff'):
                content = content[1:]
            
            csv_reader = csv.DictReader(io.StringIO(content))
            
            for row in csv_reader:
                # Normalize field names (remove BOM)
                normalized_row = {}
                for key, value in row.items():
                    clean_key = key.strip().replace('\ufeff', '')
                    normalized_row[clean_key] = value.strip() if value else ''
                
                if normalized_row:
                    data.append(normalized_row)
        
        logger.info(f"Successfully extracted {len(data)} records from CSV")
        return data
        
    except Exception as e:
        logger.error(f"Error extracting from CSV: {str(e)}")
        raise

def parse_discount_text(text: str) -> List[Dict[str, Any]]:
    """
    Parse discount information from PDF text
    UrSaviour Weekly Specials format parser.
    Format: Product Name | Store | Original Price | Discount Type | Final Price
    """
    logger.info(f"Parsing PDF text: {text[:200]}...")  # Log first 200 characters only
    
    # Skip PDF headers and extract data section only
    lines = text.split('\n')
    data_lines = []
    
    # Skip headers and find actual data
    header_passed = False
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Skip header lines ("Product Name", "Store", etc.)
        if any(header in line for header in ["Product Name", "Store", "Original Price", "Discount Type", "Final Price", "UrSaviour Weekly"]):
            header_passed = True
            continue
        # After headers are passed and this is actual data line
        if header_passed and '$' in line:
            data_lines.append(line)
    
    logger.info(f"Found {len(data_lines)} potential data lines")
    
    # Improved regex: product name, store name, original price($), discount type, discounted price($)
    # Example: "Donut Justin Groceries $5.87 Half Price $2.94"
    pattern = re.compile(r"^(.+?)\s+(.+?)\s+\$(\d+\.\d{2})\s+(.+?)\s+\$(\d+\.\d{2})$")
    matches = []
    
    for line in data_lines:
        match = pattern.match(line.strip())
        if match:
            matches.append(match.groups())
        else:
            logger.warning(f"Could not parse line: {line}")
    
    logger.info(f"Successfully parsed {len(matches)} items")
    
    parsed_data = []
    for match in matches:
        try:
            parsed_data.append({
                "productName": match[0].strip(),
                "storeName": match[1].strip(),
                "basePrice": float(match[2]),
                "offerDetails": match[3].strip(),
                "price": float(match[4])
            })
        except (ValueError, IndexError) as e:
            logger.warning(f"Error parsing line: {match}, error: {str(e)}")
            continue
    
    return parsed_data

def transform_discount_data(raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transform raw data to database format
    """
    transformed = []
    
    for item in raw_data:
        try:
            # Unify CSV and PDF data structure
            if 'productName' in item:
                # PDF format
                transformed_item = {
                    'productName': clean_text(item['productName']),
                    'storeName': clean_text(item['storeName']),
                    'basePrice': float(item['basePrice']),
                    'price': float(item['price']),
                    'offerDetails': clean_text(item['offerDetails'])
                }
            else:
                # CSV format (requires field mapping)
                transformed_item = map_csv_fields(item)
            
            # Validate data
            if validate_discount_record(transformed_item):
                transformed.append(transformed_item)
            else:
                logger.warning(f"Invalid record skipped: {transformed_item}")
                
        except Exception as e:
            logger.warning(f"Error transforming record: {item}, error: {str(e)}")
            continue
    
    return transformed

def map_csv_fields(csv_row: Dict[str, str]) -> Dict[str, Any]:
    """
    Map CSV fields to standard format
    Supports both snake_case (product_name) and camelCase (productName) formats
    """
    # CSV field mapping - maps source CSV field names to standard field names
    field_mapping = {
        # Support both formats
        'store_name': 'storeName',
        'storeName': 'storeName',
        'product_name': 'productName',
        'productName': 'productName',
        'final_price': 'price',
        'price': 'price',
        'base_price': 'basePrice',
        'basePrice': 'basePrice',
        'discount_type': 'offerDetails',
        'offerDetails': 'offerDetails',
        'offer_details': 'offerDetails'
    }
    
    mapped = {}
    for csv_field, standard_field in field_mapping.items():
        if csv_field in csv_row and csv_row[csv_field]:
            value = csv_row[csv_field]
            if standard_field in ['basePrice', 'price']:
                # Handle price fields - extract numeric value
                try:
                    value = float(re.sub(r'[^\d.]', '', str(value)))
                except (ValueError, AttributeError):
                    logger.warning(f"Could not parse price value: {value}")
                    continue
            elif standard_field in ['storeName', 'productName', 'offerDetails']:
                # Clean text fields
                value = clean_text(str(value))
            
            # Only add if we haven't already mapped this standard field
            if standard_field not in mapped:
                mapped[standard_field] = value
    
    return mapped

def clean_text(text: str) -> str:
    """
    Clean text content
    """
    if not text:
        return ""
    
    # Remove extra whitespace and special characters
    cleaned = re.sub(r'\s+', ' ', str(text).strip())
    # Remove BOM and other unwanted characters
    cleaned = cleaned.replace('\ufeff', '').replace('\x00', '')
    
    return cleaned

def validate_discount_record(record: Dict[str, Any]) -> bool:
    """
    Validate discount record
    """
    required_fields = ['productName', 'storeName', 'price', 'basePrice']
    
    # Check required fields exist
    for field in required_fields:
        if field not in record or not record[field]:
            return False
    
    # Check price values are valid
    try:
        price = float(record['price'])
        base_price = float(record['basePrice'])
        
        if price <= 0 or base_price <= 0:
            return False
        if price > base_price:  # Discount price should be lower
            logger.warning(f"Price higher than base price: {record}")
    except (ValueError, TypeError):
        return False
    
    return True

def load_data_to_database(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Load data to database
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        logger.info("Connected to database")
        
        # 1. Get existing data mapping
        cursor.execute("SELECT productId, productName FROM products")
        product_map = {p['productName']: p['productId'] for p in cursor.fetchall()}
        
        cursor.execute("SELECT storeId, storeName FROM stores")
        store_map = {s['storeName']: s['storeId'] for s in cursor.fetchall()}
        
        # 2. Add new products/stores
        new_products = 0
        new_stores = 0
        
        for item in data:
            if item['productName'] not in product_map:
                cursor.execute("INSERT INTO products (productName) VALUES (%s)", (item['productName'],))
                product_map[item['productName']] = cursor.lastrowid
                new_products += 1
                logger.info(f"New product added: {item['productName']}")
            
            if item['storeName'] not in store_map:
                cursor.execute("INSERT INTO stores (storeName) VALUES (%s)", (item['storeName'],))
                store_map[item['storeName']] = cursor.lastrowid
                new_stores += 1
                logger.info(f"New store added: {item['storeName']}")
        
        # 3. Delete existing storeOfferings
        cursor.execute("DELETE FROM storeOfferings")
        deleted_count = cursor.rowcount
        logger.info(f"Deleted {deleted_count} existing store offerings")
        
        # 4. Insert new discount data
        offerings_to_insert = []
        for item in data:
            product_id = product_map.get(item['productName'])
            store_id = store_map.get(item['storeName'])
            
            if product_id and store_id:
                offerings_to_insert.append((
                    product_id,
                    store_id,
                    item['price'],
                    item['basePrice'],
                    item.get('offerDetails', '')
                ))
        
        sql = """
            INSERT INTO storeOfferings (productId, storeId, price, basePrice, offerDetails)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.executemany(sql, offerings_to_insert)
        inserted_count = cursor.rowcount
        
        # Commit transaction
        conn.commit()
        
        result = {
            'records_deleted': deleted_count,
            'records_inserted': inserted_count,
            'new_products': new_products,
            'new_stores': new_stores,
            'total_products': len(product_map),
            'total_stores': len(store_map)
        }
        
        logger.info(f"Database update completed: {result}")
        return result
        
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database operation failed: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

def send_success_notification(file_key: str, result: Dict[str, Any]):
    """
    Send success notification
    """
    if not SNS_TOPIC_ARN:
        return
    
    try:
        message = f"""
✅ UrSaviour ETL Processing Successful

📄 Processed File: {file_key}
⏱️ Processing Time: {result.get('processing_time_seconds', 0):.2f} seconds

📊 Processing Results:
  • Extracted Records: {result.get('records_extracted', 0)}
  • Transformed Records: {result.get('records_transformed', 0)}
  • DB Saved Records: {result.get('records_loaded', 0)}

🏪 Database Updates:
  • Existing Offers Deleted: {result.get('database_operations', {}).get('records_deleted', 0)}
  • New Offers Added: {result.get('database_operations', {}).get('records_inserted', 0)}
  • New Products: {result.get('database_operations', {}).get('new_products', 0)}
  • New Stores: {result.get('database_operations', {}).get('new_stores', 0)}

🕐 Completion Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
        """
        
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject='✅ UrSaviour ETL Processing Successful',
            Message=message
        )
        
    except Exception as e:
        logger.error(f"Error sending success notification: {str(e)}")

def send_error_notification(file_key: str, error_message: str):
    """
    Send error notification
    """
    if not SNS_TOPIC_ARN:
        return
    
    try:
        message = f"""
❌ UrSaviour ETL Processing Failed

📄 Failed File: {file_key}
🚨 Error: {error_message}
🕐 Failure Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

💡 Resolution Steps:
1. Check file format is correct
2. Verify database connection
3. Check Lambda function logs
4. Manually re-run ETL if needed

🔍 Check CloudWatch logs for detailed information.
        """
        
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject='❌ UrSaviour ETL Processing Failed',
            Message=message
        )
        
    except Exception as e:
        logger.error(f"Error sending error notification: {str(e)}")

def validate_environment():
    """
    Validate required environment variables
    """
    required_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {missing_vars}")
    
    logger.info("Environment validation passed")

# ETL job logging functions

def log_etl_job_start(source_file: str, file_type: str, start_time: datetime) -> str:
    """
    Log ETL job start to etlJobs table
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Generate UUID
        job_id = f"{int(start_time.timestamp() * 1000)}-{hash(source_file) % 10000:04d}"
        
        # Insert start record to etlJobs table
        cursor.execute("""
            INSERT INTO etlJobs (jobId, sourceIdentifier, startTime, overallStatus, totalItemExtracted, totalItemLoaded)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (job_id, source_file, start_time, 'running', 0, 0))
        
        conn.commit()
        conn.close()
        
        logger.info(f"ETL job started with ID: {job_id}")
        return job_id
        
    except Exception as e:
        logger.error(f"Failed to log ETL job start: {str(e)}")
        return f"fallback-{int(start_time.timestamp())}"

def log_etl_job_complete(job_id: str, end_time: datetime, status: str, items_extracted: int, items_loaded: int):
    """
    Log ETL job completion to etlJobs table
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update etlJobs table
        cursor.execute("""
            UPDATE etlJobs 
            SET endTime = %s, overallStatus = %s, totalItemExtracted = %s, totalItemLoaded = %s
            WHERE jobId = %s
        """, (end_time, status, items_extracted, items_loaded, job_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"ETL job {job_id} completed with status: {status}")
        
    except Exception as e:
        logger.error(f"Failed to log ETL job completion: {str(e)}")

def log_etl_message(job_id: str, level: str, message: str):
    """
    Log ETL execution message to etlJobLogs table
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Map level to stage and status
        stage_mapping = {
            'INFO': ('processing', 'success'),
            'ERROR': ('processing', 'failed'),
            'WARNING': ('processing', 'warning')
        }
        
        stage, status = stage_mapping.get(level, ('processing', 'info'))
        
        # Insert log to etlJobLogs table
        cursor.execute("""
            INSERT INTO etlJobLogs (jobId, timestamp, stage, status, message)
            VALUES (%s, %s, %s, %s, %s)
        """, (job_id, datetime.utcnow(), stage, status, message))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        logger.error(f"Failed to log ETL message: {str(e)}")

def get_db_connection():
    """
    Create database connection
    """
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=10
    )

# Initialize environment validation
try:
    validate_environment()
except Exception as e:
    logger.error(f"Environment validation failed: {str(e)}")
    raise