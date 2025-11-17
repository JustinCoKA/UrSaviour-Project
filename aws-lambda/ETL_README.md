# ETL module (aws-lambda)

This folder contains the ETL Lambda processor used to ingest weekly specials CSV/PDF files from S3 and update the database.

Summary of recent improvements
- Uses Australia/Sydney timezone for ETL timestamps and notifications (all timestamps formatted in local Sydney time).
- Idempotency: ETL will skip files that already have a successful job recorded in `etlJobs` (prevents duplicate processing).
- Safer DB load for `storeOfferings`: the ETL now creates a temporary swap table, inserts new rows there, and atomically renames tables to replace the live `storeOfferings` table. This avoids gaps caused by a DELETE-then-INSERT pattern.
- Category handling: CSV column `category_name` is mapped to `categoryName` and the ETL will create missing categories in `productCategories` before inserting products. Falls back to `Uncategorized` when category is not provided.

Running tests (unit)

1. Create and activate a virtualenv (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install pytest
```

2. From the repository root run:

```bash
pytest aws-lambda/tests/test_etl_unit.py -q
```

Notes
- The tests are lightweight unit tests that import the module via file-loader and monkeypatch `get_db_connection` for the idempotency check.
- For integration runs (actual ETL), ensure the DB user has privileges: CREATE, INSERT, SELECT, RENAME, DROP on `storeOfferings` and related tables.
- If you prefer to keep backups of old `storeOfferings`, modify the swap-drop behavior in `etl_processor_lambda.py`.
