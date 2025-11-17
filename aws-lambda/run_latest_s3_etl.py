"""Local runner: find the latest CSV in an S3 bucket and run the ETL processor locally.

Usage:
  python run_latest_s3_etl.py --bucket <bucket-name> [--prefix <prefix>] [--db-host HOST --db-user USER --db-pass PASS --db-name NAME]

Notes:
  - This script requires AWS credentials available to boto3 (env / ~/.aws/).
  - You must provide DB env vars (DB_HOST, DB_USER, DB_PASSWORD, DB_NAME) either via CLI flags or environment.
  - The script imports `etl_processor_lambda` which validates env variables at import time, so ensure DB vars are set before running.
"""
import argparse
import os
import sys
import tempfile
import boto3
from datetime import timezone
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


ALLOWED_PATTERNS = ['week_special', 'discount', 'pamphlet']


def find_latest_csv(s3_client, bucket: str, prefix: str = None):
    paginator = s3_client.get_paginator('list_objects_v2')
    kwargs = {'Bucket': bucket}
    if prefix:
        kwargs['Prefix'] = prefix

    latest = None

    for page in paginator.paginate(**kwargs):
        for obj in page.get('Contents', []):
            key = obj['Key']
            if not key.lower().endswith('.csv'):
                continue
            # filename patterns filter
            if not any(pat in key.lower() for pat in ALLOWED_PATTERNS):
                continue

            if not latest or obj['LastModified'] > latest['LastModified']:
                latest = obj

    return latest


def download_to_temp(s3_client, bucket: str, key: str):
    tf = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(key)[1])
    logger.info(f"Downloading s3://{bucket}/{key} -> {tf.name}")
    s3_client.download_file(bucket, key, tf.name)
    return tf.name


def ensure_db_env(args):
    # Set DB env vars from CLI args if provided
    if args.db_host:
        os.environ['DB_HOST'] = args.db_host
    if args.db_user:
        os.environ['DB_USER'] = args.db_user
    if args.db_pass:
        os.environ['DB_PASSWORD'] = args.db_pass
    if args.db_name:
        os.environ['DB_NAME'] = args.db_name

    missing = [v for v in ('DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME') if not os.environ.get(v)]
    if missing:
        logger.error(f"Missing DB environment variables: {missing}. Provide via CLI or environment.")
        sys.exit(2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bucket', required=True)
    parser.add_argument('--prefix', required=False)
    parser.add_argument('--db-host')
    parser.add_argument('--db-user')
    parser.add_argument('--db-pass')
    parser.add_argument('--db-name')
    parser.add_argument('--dry-run', action='store_true')

    args = parser.parse_args()

    ensure_db_env(args)

    # Create S3 client
    try:
        s3_client = boto3.client('s3')
    except Exception as e:
        logger.error(f"Failed to create S3 client: {e}")
        sys.exit(1)

    latest = find_latest_csv(s3_client, args.bucket, args.prefix)
    if not latest:
        logger.info("No matching CSV objects found in S3 bucket")
        sys.exit(0)

    key = latest['Key']
    logger.info(f"Latest CSV in bucket {args.bucket}: {key} (LastModified={latest['LastModified']})")

    if args.dry_run:
        logger.info("Dry run mode, exiting before download/invoke")
        sys.exit(0)

    # Download file
    tmp_path = download_to_temp(s3_client, args.bucket, key)

    # Import ETL processor and invoke lambda_handler with test event
    # Note: etl_processor_lambda validates env at import time, so DB envs must be set before import
    try:
        import etl_processor_lambda as etl
    except Exception as e:
        logger.error(f"Failed to import etl_processor_lambda: {e}")
        logger.error("Make sure DB env variables are set (DB_HOST, DB_USER, DB_PASSWORD, DB_NAME) before running")
        sys.exit(1)

    event = {
        'bucket_name': args.bucket,
        'object_key': key,
        'test_mode': True
    }

    logger.info("Invoking ETL processor.lambda_handler in-process")
    try:
        response = etl.lambda_handler(event, None)
        logger.info(f"ETL response: {response}")
    except Exception as e:
        logger.error(f"ETL processing failed: {e}")
        raise


if __name__ == '__main__':
    main()
