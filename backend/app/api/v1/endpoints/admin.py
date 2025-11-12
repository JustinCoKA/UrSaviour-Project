from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, MetaData, Table
from app.db.session import get_db, engine
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Lazily load ETL Jobs table
metadata = MetaData()
_etl_tables_loaded = False
ETLJobs = None

def _ensure_etl_tables():
    global _etl_tables_loaded, ETLJobs
    if not _etl_tables_loaded:
        ETLJobs = Table("etlJobs", metadata, autoload_with=engine)
        _etl_tables_loaded = True

@router.get("/etl-jobs", summary="Get all ETL jobs")
def get_etl_jobs(db: Session = Depends(get_db)):
    """
    Get all ETL jobs from the database
    Returns: List of ETL job records
    """
    try:
        _ensure_etl_tables()
        
        # Query all ETL jobs, ordered by most recent first
        query = select(
            ETLJobs.c.jobId,
            ETLJobs.c.jobNumber,
            ETLJobs.c.jobType,
            ETLJobs.c.sourceFile,
            ETLJobs.c.startTime,
            ETLJobs.c.endTime,
            ETLJobs.c.overallStatus,
            ETLJobs.c.totalItemProcessed,
            ETLJobs.c.totalItemLoaded,
            ETLJobs.c.totalItemFailed,
            ETLJobs.c.errorLog
        ).order_by(ETLJobs.c.startTime.desc()).limit(100)
        
        result = db.execute(query).fetchall()
        
        # Convert to list of dicts
        jobs = []
        for row in result:
            jobs.append({
                "jobId": row.jobId,
                "jobNumber": row.jobNumber,
                "jobType": row.jobType,
                "sourceFile": row.sourceFile,
                "startTime": row.startTime.isoformat() if row.startTime else None,
                "endTime": row.endTime.isoformat() if row.endTime else None,
                "overallStatus": row.overallStatus,
                "totalItemProcessed": row.totalItemProcessed,
                "totalItemLoaded": row.totalItemLoaded,
                "totalItemFailed": row.totalItemFailed,
                "errorLog": row.errorLog
            })
        
        return jobs
        
    except Exception as e:
        logger.error(f"Error fetching ETL jobs: {str(e)}")
        return {"error": str(e), "message": "Failed to fetch ETL jobs"}
