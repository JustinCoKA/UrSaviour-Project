# aws_connector.py
import boto3
import os
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
from typing import List

load_dotenv()

# Defaults - adjust as needed in .env
AWS_BUCKET = os.getenv("AWS_BUCKET", "ursaviour-data-group03-20250608")
DATA_DIR = "data"


def get_s3_client():
    """Return a boto3 S3 client using env vars (keeps a single place to change auth)."""
    return boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION", "ap-southeast-2"),
    )


def list_s3_data_keys(prefix: str | None = None) -> List[str]:
    """List CSV and PDF keys in the configured S3 bucket.

    Returns a list of object keys (strings).
    """
    s3 = get_s3_client()
    kwargs = {"Bucket": AWS_BUCKET}
    if prefix:
        kwargs["Prefix"] = prefix

    keys: List[str] = []
    try:
        resp = s3.list_objects_v2(**kwargs)
        for obj in resp.get("Contents", []) or []:
            key = obj.get("Key", "")
            if key.lower().endswith(".csv") or key.lower().endswith(".pdf"):
                keys.append(key)
    except NoCredentialsError:
        print("❌ AWS credentials not found. Please check your .env file.")
    return keys


def stream_s3_object_bytes(key: str) -> bytes:
    """Return the object body as bytes for the given S3 key.

    This reads the entire object into memory; for very large files consider
    streaming in chunks or processing line-by-line for CSVs.
    """
    s3 = get_s3_client()
    resp = s3.get_object(Bucket=AWS_BUCKET, Key=key)
    body = resp["Body"]
    return body.read()


def download_from_s3():
    """Legacy helper that downloads objects to `data/` directory (kept for compatibility).

    Prefer using `list_s3_data_keys` + `stream_s3_object_bytes` to avoid local files.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    s3 = get_s3_client()

    try:
        response = s3.list_objects_v2(Bucket=AWS_BUCKET)
        for obj in response.get("Contents", []):
            key = obj["Key"]
            if key.endswith(".csv") or key.endswith(".pdf"):
                local_path = os.path.join(DATA_DIR, os.path.basename(key))
                s3.download_file(AWS_BUCKET, key, local_path)
                print(f"✅ Downloaded: {key}")
    except NoCredentialsError:
        print("❌ AWS credentials not found. Please check your .env file.")
