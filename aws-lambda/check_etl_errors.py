#!/usr/bin/env python3
"""
Check ETL job logs to see detailed error messages
"""

import pymysql
import os

# Database configuration
DB_CONFIG = {
    'host': 'ursaviour-db.cp4emoqegwfy.ap-southeast-2.rds.amazonaws.com',
    'port': 3306,
    'user': 'admin',
    'password': 'Ursaviour2025',
    'database': 'ursaviourDb'
}

def check_etl_logs():
    """Check ETL job logs for error details"""
    try:
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("="*80)
        print("  ETL JOB LOGS - DETAILED ERROR MESSAGES")
        print("="*80)
        
        with connection.cursor() as cursor:
            # Get failed jobs
            cursor.execute("""
                SELECT jobId, sourceIdentifier, startTime, overallStatus
                FROM etlJobs
                WHERE overallStatus = 'failed'
                ORDER BY startTime DESC
                LIMIT 10
            """)
            failed_jobs = cursor.fetchall()
            
            print(f"\nFound {len(failed_jobs)} failed jobs\n")
            
            for job in failed_jobs:
                print(f"\n{'='*80}")
                print(f"Job ID: {job['jobId']}")
                print(f"Source: {job['sourceIdentifier']}")
                print(f"Time: {job['startTime']}")
                print(f"Status: {job['overallStatus']}")
                print(f"\nError Logs:")
                print("-"*80)
                
                # Get logs for this job
                cursor.execute("""
                    SELECT timestamp, stage, status, message
                    FROM etlJobLogs
                    WHERE jobId = %s
                    ORDER BY timestamp
                """, (job['jobId'],))
                logs = cursor.fetchall()
                
                if logs:
                    for log in logs:
                        print(f"[{log['timestamp']}] [{log['stage']}] [{log['status']}]")
                        print(f"  {log['message']}")
                else:
                    print("  No detailed logs found")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_etl_logs()
