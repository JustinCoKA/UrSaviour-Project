"""S3 CSV loader utilities.

Provides:
- load_csv_from_s3(bucket, key) -> pandas.DataFrame

Behavior:
- Uses boto3 to fetch an object from S3
- Uses pandas to parse CSV content and return a DataFrame
- Raises FileNotFoundError for a missing S3 object
"""
from typing import Any
import io

import boto3
import botocore
import pandas as pd


def load_csv_from_s3(bucket: str, key: str) -> pd.DataFrame:
    """Load a CSV file from S3 and return it as a pandas DataFrame.

    Args:
        bucket: S3 bucket name.
        key: S3 object key (path to the CSV file).

    Returns:
        pandas.DataFrame containing the CSV data.

    Raises:
        FileNotFoundError: if the S3 object does not exist.
        botocore.exceptions.BotoCoreError or botocore.exceptions.ClientError for other S3 errors.
        pandas.errors.EmptyDataError if the CSV is empty.
    """
    try:
        # Create the S3 client inside the try so credential-related errors
        # raised during client construction are caught and converted to a
        # FileNotFoundError (treated as "no product data" in callers).
        s3 = boto3.client("s3")
        obj = s3.get_object(Bucket=bucket, Key=key)
        # obj['Body'] is a StreamingBody. Read binary and pass to pandas.
        body = obj["Body"].read()
        # Use BytesIO so pandas can read from bytes
        df = pd.read_csv(io.BytesIO(body))
        return df

    except botocore.exceptions.ClientError as e:
        # When the object or bucket is missing, the error code is typically 'NoSuchKey' or 'NoSuchBucket'
        error_code = e.response.get("Error", {}).get("Code")
        if error_code in ("NoSuchKey", "NoSuchBucket", "404"):
            raise FileNotFoundError(f"S3 object s3://{bucket}/{key} not found") from e
        # Re-raise other client errors
        raise

    except (botocore.exceptions.NoCredentialsError, botocore.exceptions.PartialCredentialsError) as e:
        # Treat missing/partial credentials as "no product data found" so callers
        # that already handle missing files (FileNotFoundError) can continue.
        raise FileNotFoundError(f"S3 object s3://{bucket}/{key} not accessible due to missing AWS credentials") from e
    except botocore.exceptions.BotoCoreError:
        # Generic boto core errors (connection, other credential issues, etc.) bubble up
        raise

    except pd.errors.EmptyDataError:
        # Let caller know CSV was empty
        raise

    except Exception as e:
        # Some botocore credential problems can surface as different exception
        # types depending on environment and boto3/botocore versions. Detect
        # credential-related messages and treat them as "file not found / not
        # accessible" so callers (like the chat endpoint) can continue without
        # product data in development environments where AWS creds are partial.
        msg = str(e)
        credential_indicators = (
            "Partial credentials",
            "NoCredentialsError",
            "Unable to locate credentials",
        )
        if any(ind in msg for ind in credential_indicators):
            raise FileNotFoundError(f"S3 object s3://{bucket}/{key} not accessible due to missing AWS credentials: {msg}") from e
        # Otherwise re-raise the original exception
        raise
