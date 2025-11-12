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
        
        # Get available columns dynamically
        available_cols = {col.name for col in ETLJobs.columns}
        logger.info(f"Available columns in etlJobs table: {available_cols}")
        
        # Build query with only available columns
        select_cols = []
        col_mapping = {
            'jobId': 'jobId',
            'jobNumber': 'jobNumber',
            'jobType': 'jobType',
            'sourceFile': 'sourceFile',
            'sourceIdentifier': 'sourceIdentifier',
            'startTime': 'startTime',
            'endTime': 'endTime',
            'overallStatus': 'overallStatus',
            'totalItemExtracted': 'totalItemExtracted',
            'totalItemLoaded': 'totalItemLoaded',
            'totalItemFailed': 'totalItemFailed',
            'errorLog': 'errorLog'
        }
        
        for col_name in col_mapping.keys():
            if col_name in available_cols:
                select_cols.append(ETLJobs.c[col_name])
        
        query = select(*select_cols).order_by(ETLJobs.c.startTime.desc()).limit(100)
        result = db.execute(query).fetchall()
        
        # Convert to list of dicts
        jobs = []
        for row in result:
            job = {}
            for col_name, json_name in col_mapping.items():
                if col_name in available_cols:
                    value = getattr(row, col_name, None)
                    # Convert datetime to ISO format
                    if value and col_name in ['startTime', 'endTime']:
                        job[json_name] = value.isoformat()
                    else:
                        job[json_name] = value
            jobs.append(job)
        
        return jobs
        
    except Exception as e:
        logger.error(f"Error fetching ETL jobs: {str(e)}")
        return {"error": str(e), "message": "Failed to fetch ETL jobs"}
