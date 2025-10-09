# backend/app/services/etl_service.py
# Service: S3 -> CSV -> DB upsert for products / categories / stores / storeOfferings

import io, csv, re
from typing import Iterable, Dict, Optional, List
import boto3
from sqlalchemy import MetaData, Table, select, update, insert, text, delete
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import SessionLocal, engine
import uuid

# --- S3 helpers ---
def _s3():
    # Use env/IAM credentials
    return boto3.client("s3", region_name=settings.AWS_REGION)

def list_csv_keys(prefix: str) -> List[Dict]:
    # List *.csv under prefix (non-recursive)
    s3 = _s3()
    token = None
    out: List[Dict] = []
    while True:
        params = {"Bucket": settings.S3_BUCKET_NAME, "Prefix": prefix}
        if token:
            params["ContinuationToken"] = token
        resp = s3.list_objects_v2(**params)
        for o in resp.get("Contents", []):
            if o["Key"].lower().endswith(".csv"):
                out.append({"Key": o["Key"], "LastModified": o["LastModified"]})
        if not resp.get("IsTruncated"):
            break
        token = resp.get("NextContinuationToken")
    return out

def fetch_csv_rows(key: str) -> Iterable[Dict[str, str]]:
    # Stream CSV from S3 as Dict rows
    s3 = _s3()
    obj = s3.get_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
    text = io.TextIOWrapper(obj["Body"], encoding="utf-8")
    return csv.DictReader(text)

# --- CSV mappers ---
BOM_KEY = "\ufeffproduct_id"

def extract_week_from_key(key: str) -> Optional[int]:
    # e.g., data/no.41week_special.csv -> 41
    m = re.search(r"no\.(\d+)week", key)
    return int(m.group(1)) if m else None

def _f(v: Optional[str]) -> float:
    try:
        return float((v or "").strip())
    except Exception:
        return 0.0

def _rate(base: float, final: float, dtype: Optional[str]) -> float:
    # Prefer computed rate; fall back to parsing discount_type
    if base > 0 and final > 0:
        return round((base - final) / base, 4)
    s = (dtype or "").lower()
    m = re.search(r"(\d+)\s*%+", s)
    if m:
        return round(int(m.group(1)) / 100.0, 4)
    if "half" in s:
        return 0.5
    return 0.0

def map_row(row: Dict[str, str]) -> Dict:
    """Normalize S3 CSV row into fields matching our camelCase schema."""
    pid  = row.get(BOM_KEY) or row.get("product_id") or row.get("id")
    store_name = row.get("store_name") or "Default Store"

    base_price = _f(row.get("base_price"))
    final_price = _f(row.get("final_price"))
    discount_type = (row.get("discount_type") or "").strip()

    # if final not given, compute from discount_type
    rate = _rate(base_price, final_price, discount_type)
    price = final_price if final_price > 0 else round(base_price * (1 - rate), 2)

    return {
        # keys align with DB columns we will write to storeOfferings
        "productId": pid,
        "storeName": store_name,
        "basePrice": base_price,
        "price": price,
        "offerDetails": discount_type,  # e.g., "30% OFF", "Half Price"
        "rate": rate,
    }


# --- DB reflections (use existing tables as-is) ---
metadata = MetaData()
Products       = Table("products",           metadata, autoload_with=engine)
ProductCats    = Table("productCategories",  metadata, autoload_with=engine)
Stores         = Table("stores",             metadata, autoload_with=engine)
StoreOfferings = Table("storeOfferings",     metadata, autoload_with=engine)
ETLJobLogs     = Table("etlJobLogs",         metadata, autoload_with=engine)
ETLJobs        = Table("etlJobs",            metadata, autoload_with=engine)

def _col(t: Table, name: str):
    return getattr(t.c, name, None)


def _find_col_name(t: Table, candidates: List[str]):
    """Return the first matching column object from candidates or None."""
    for name in candidates:
        c = getattr(t.c, name, None)
        if c is not None:
            return c
    return None


def _existing_vals(t: Table, vals: Dict) -> Dict:
    """Filter a dict of values to only columns that exist on the reflected table.

    This prevents INSERT/UPDATE attempts against non-existent columns when the
    source data uses different naming conventions.
    """
    out: Dict = {}
    for k, v in vals.items():
        if _col(t, k) is not None:
            out[k] = v
    return out

# --- Upserts ---

def _normalize_store_name(name: str) -> str:
    """Return normalized key for dedup (lowercase, strip all spaces)."""
    return re.sub(r"\s+", "", name or "").lower()

def upsert_category(db: Session, name: Optional[str]) -> Optional[int]:
    """Insert or return existing categoryId by categoryName."""
    if not name:
        return None

    id_col = _col(ProductCats, "categoryId") or _find_col_name(ProductCats, ["id", "category_id"])
    name_col = _col(ProductCats, "categoryName") or _find_col_name(ProductCats, ["name", "category"])

    if not id_col or not name_col:
        raise RuntimeError("productCategories table missing categoryId/categoryName columns")

    q = db.execute(select(id_col).where(name_col == name)).scalar()
    if q:
        return q

    vals = _existing_vals(ProductCats, {"categoryName": name})
    r = db.execute(insert(ProductCats).values(vals))
    return r.inserted_primary_key[0]

def upsert_product(db: Session, d: Dict) -> int:
    """Insert/update product by SKU."""
    id_col  = _col(Products, "productId")
    sku_col = _col(Products, "sku")
    name_col= _col(Products, "productName")
    desc_col= _col(Products, "description")
    img_col = _col(Products, "imageUrl")
    brand_col=_col(Products, "brand")
    cat_fk  = _col(Products, "categoryId")

    if id_col is None or sku_col is None:
        raise RuntimeError("products table missing productId/sku columns")

    q = db.execute(select(id_col).where(sku_col == d["sku"])).scalar()
    cat_id = upsert_category(db, d.get("category"))

    vals = _existing_vals(Products, {
        "sku": d["sku"],
        "productName": d["name"],
        "description": d.get("description", ""),
        "imageUrl": d.get("image_url", ""),
        "brand": None,
        "categoryId": cat_id,
        # include basePrice if products table supports it so frontend can read canonical price
        "basePrice": d.get("basePrice")
    })

    if q:
        db.execute(update(Products).where(id_col == q).values(vals))
        return q
    r = db.execute(insert(Products).values(vals))
    return r.inserted_primary_key[0]

def upsert_store(db: Session, store_name: str) -> int:
    """Insert or reuse storeId by normalized name (dedup spaces/case)."""
    norm = _normalize_store_name(store_name)

    # find existing by normalized comparison in SQL (LOWER(REPLACE(...)))
    sql = """
        SELECT storeId, storeName
        FROM stores
        WHERE LOWER(REPLACE(storeName,' ',''))
              = :norm
        LIMIT 1
    """
    row = db.execute(text(sql), {"norm": norm}).first()
    if row:
        return row.storeId

    # insert new store with the original display name
    r = db.execute(insert(Stores).values({"storeName": store_name}))
    return r.inserted_primary_key[0]

def upsert_offering(db: Session, d: Dict, store_id: int) -> int:
    """Upsert storeOfferings by (productId, storeId)."""
    t = StoreOfferings
    id_col  = _col(t, "offeringId")
    pid_col = _col(t, "productId")
    sid_col = _col(t, "storeId")
    p_col   = _col(t, "price")
    b_col   = _col(t, "basePrice")
    o_col   = _col(t, "offerDetails")

    # Columns are SQLAlchemy Column objects; test for None explicitly to avoid
    # SQLAlchemy's clause truthiness TypeError when using bool() on column objects.
    if any(col is None for col in (pid_col, sid_col, p_col, b_col, o_col)):
        raise RuntimeError("storeOfferings must have productId, storeId, price, basePrice, offerDetails")

    cond = (pid_col == d["productId"]) & (sid_col == store_id)
    existing_id = db.execute(select(id_col).where(cond)).scalar() if id_col is not None else None

    vals = {
        "productId": d["productId"],
        "storeId":   store_id,
        "price":     d["price"],
        "basePrice": d.get("basePrice"),
        "offerDetails": d.get("offerDetails"),
    }

    if existing_id is not None:
        db.execute(update(t).where(id_col == existing_id).values(vals))
        return existing_id
    r = db.execute(insert(t).values(vals))
    return r.inserted_primary_key[0]

def log(db: Session, key: str, status: str, message: str = "", job_id: Optional[int] = None):
    # Build payload only with columns that exist on the ETLJobLogs table
    payload: Dict = {}
    # timestamp column commonly exists and may be NOT NULL
    if _col(ETLJobLogs, "timestamp") is not None:
        from datetime import datetime

        payload["timestamp"] = datetime.utcnow()
    # stage column exists in schema (e.g., 'file'|'job')
    if _col(ETLJobLogs, "stage") is not None:
        payload["stage"] = "file"
    # include jobId if present
    if job_id is not None and _col(ETLJobLogs, "jobId") is not None:
        payload["jobId"] = job_id
    # status/message
    if _col(ETLJobLogs, "status") is not None:
        payload["status"] = status
    if _col(ETLJobLogs, "message") is not None:
        payload["message"] = message
    # optional source-like column if table has it (e.g., source_key, sourceIdentifier)
    source_col = None
    for c in ETLJobLogs.columns:
        n = c.name.lower()
        if "source" in n or "identifier" in n or "key" in n:
            source_col = c.name
            break
    if source_col is not None:
        payload[source_col] = key

    ins = {k: v for k, v in payload.items() if _col(ETLJobLogs, k) is not None}
    if ins:
        db.execute(insert(ETLJobLogs).values(ins))


# --- Public entrypoint ---
def run_full_etl(prefix: str) -> Dict:
    processed = 0
    keys = sorted(list_csv_keys(prefix), key=lambda x: x["LastModified"])
    with SessionLocal() as db:
        # Create a top-level ETL job record so logs can reference its jobId (FK)
        job_id = None
        try:
            # Build a minimal job payload based on ETLJobs columns to satisfy NOT NULL constraints
            job_vals: Dict = {}
            for col in ETLJobs.columns:
                # skip auto-increment PK if present
                if col.primary_key:
                    # If the PK is a string-like column (VARCHAR) and not autoincrementing,
                    # generate a UUID to use as the jobId to satisfy NOT NULL PK constraint.
                    if col.name == 'jobId' and getattr(col.type, 'length', None) is not None:
                        # generate uuid string
                        job_vals[col.name] = str(uuid.uuid4())
                        continue
                    continue
                # if column is nullable or has a default we can skip explicit value
                if col.nullable:
                    continue
                # Provide reasonable defaults for common column names
                name = col.name.lower()
                if "status" in name:
                    job_vals[col.name] = "running"
                elif "source" in name or "key" in name:
                    job_vals[col.name] = prefix
                elif "created" in name or "start" in name or "time" in name:
                    from datetime import datetime
                    # Set startTime for the job explicitly
                    job_vals[col.name] = datetime.utcnow()
                else:
                    # Fallback on SQLAlchemy type hints: use 0 for ints, '' for text, utcnow for datetimes
                    col_type = getattr(col.type, "__class__", None)
                    tname = getattr(col.type, "__class__", type(col.type)).__name__.lower()
                    if "int" in tname or "numeric" in tname or "integer" in tname:
                        job_vals[col.name] = 0
                    elif "date" in tname or "time" in tname:
                        from datetime import datetime

                        job_vals[col.name] = datetime.utcnow()
                    else:
                        job_vals[col.name] = ""

            r_job = db.execute(insert(ETLJobs).values(job_vals))
            # Persist immediately so FK constraints on logs can reference it
            db.commit()
            job_id = r_job.inserted_primary_key[0] if r_job.inserted_primary_key else None
        except Exception:
            # If we cannot create a job record, proceed without job_id (logging will skip jobId)
            db.rollback()
            job_id = None
        try:
            # Clear previous offerings so each ETL run replaces the storeOfferings with the latest discounted items only
            try:
                if StoreOfferings is not None:
                    db.execute(delete(StoreOfferings))
                    db.commit()
            except Exception:
                db.rollback()

            total_extracted = 0
            total_loaded = 0

            for o in keys:
                key = o["Key"]
                file_count = 0
                file_failed = 0
                try:
                    for row in fetch_csv_rows(key):
                        try:
                            d = map_row(row)
                            # Only consider rows with a positive discount rate
                            if d.get("rate", 0.0) <= 0.0:
                                # skip non-discounted items
                                continue
                            sid = upsert_store(db, d["storeName"])
                            # upsert product (may create product record and persist basePrice)
                            upsert_product(db, {**d, "sku": d.get("productId"), "name": d.get("productId")})
                            upsert_offering(db, d, sid)
                            file_count += 1
                            total_loaded += 1
                        except Exception:
                            # per-row failure should not stop the file; record and continue
                            file_failed += 1
                    total_extracted += file_count
                    log(db, key, "success", f"rows={file_count}, failed={file_failed}", job_id=job_id)
                    db.commit()
                except Exception as e:
                    db.rollback()
                    log(db, key, "failed", str(e), job_id=job_id)
                    # propagate so outer try can mark job failure
                    raise

            # If we reach here, update the job row with overallStatus and totals if columns exist
            if job_id is not None:
                upd: Dict = {}
                from datetime import datetime
                if _col(ETLJobs, "overallStatus") is not None:
                    upd["overallStatus"] = "success"
                if _col(ETLJobs, "totalItemExtracted") is not None:
                    upd["totalItemExtracted"] = total_extracted
                if _col(ETLJobs, "totalItemLoaded") is not None:
                    upd["totalItemLoaded"] = total_loaded
                if _col(ETLJobs, "endTime") is not None:
                    upd["endTime"] = datetime.utcnow()
                if upd:
                    db.execute(update(ETLJobs).where(ETLJobs.c.jobId == job_id).values(upd))
                    db.commit()
        except Exception:
            # mark job failed
            try:
                if job_id is not None and _col(ETLJobs, "overallStatus") is not None:
                    db.execute(update(ETLJobs).where(ETLJobs.c.jobId == job_id).values({"overallStatus": "failed"}))
                    db.commit()
            except Exception:
                db.rollback()
            raise

        return {"processed": processed}
