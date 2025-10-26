#!/usr/bin/env python3
"""
Check recent ETL jobs (including successful ones)
"""

import pymysql

DB_CONFIG = {
    'host': 'ursaviour-db.cp4emoqegwfy.ap-southeast-2.rds.amazonaws.com',
    'port': 3306,
    'user': 'admin',
    'password': 'Ursaviour2025',
    'database': 'ursaviourDb'
}

connection = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)

with connection.cursor() as cursor:
    print("="*80)
    print("  RECENT ETL JOBS (Last 10)")
    print("="*80)
    
    cursor.execute("""
        SELECT jobId, sourceIdentifier, startTime, endTime,
               overallStatus, totalItemExtracted, totalItemLoaded
        FROM etlJobs
        ORDER BY startTime DESC
        LIMIT 10
    """)
    jobs = cursor.fetchall()
    
    for job in jobs:
        status_icon = "✅" if job['overallStatus'] == 'success' else "❌"
        print(f"\n{status_icon} {job['overallStatus'].upper()}")
        print(f"   Job: {job['jobId']}")
        print(f"   File: {job['sourceIdentifier']}")
        print(f"   Time: {job['startTime']}")
        print(f"   Extracted: {job['totalItemExtracted']} | Loaded: {job['totalItemLoaded']}")

connection.close()
