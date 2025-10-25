#!/usr/bin/env python3
"""
Database Status Check Script
Check current state of ETL database and tables
"""

import os
import pymysql
from datetime import datetime
import sys

def get_db_connection():
    """Create database connection"""
    # Try to get database connection info from environment or use defaults
    db_config = {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'user': os.environ.get('DB_USER', 'ursaviour'),
        'password': os.environ.get('DB_PASSWORD', 'password'),
        'database': os.environ.get('DB_NAME', 'ursaviourDb'),
        'port': int(os.environ.get('DB_PORT', 3306)),
        'cursorclass': pymysql.cursors.DictCursor,
        'connect_timeout': 10
    }
    
    print(f"Attempting to connect to database:")
    print(f"  Host: {db_config['host']}")
    print(f"  Port: {db_config['port']}")
    print(f"  Database: {db_config['database']}")
    print(f"  User: {db_config['user']}")
    print()
    
    try:
        connection = pymysql.connect(**db_config)
        print("✅ Database connection successful!")
        return connection
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return None

def check_database_status():
    """Check current database status"""
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        with connection.cursor() as cursor:
            print("=" * 60)
            print("DATABASE STATUS CHECK")
            print("=" * 60)
            print()
            
            # Check if tables exist
            tables_to_check = ['storeOfferings', 'products', 'stores', 'etlJobs', 'etlJobLogs']
            
            for table in tables_to_check:
                try:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                    result = cursor.fetchone()
                    count = result['count']
                    print(f"📊 Table '{table}': {count} records")
                    
                    # Show sample data for key tables
                    if table == 'storeOfferings' and count > 0:
                        cursor.execute("""
                            SELECT 
                                so.offeringId,
                                p.productName,
                                s.storeName,
                                so.price,
                                so.basePrice,
                                so.offerDetails
                            FROM storeOfferings so
                            JOIN products p ON so.productId = p.productId
                            JOIN stores s ON so.storeId = s.storeId
                            LIMIT 5
                        """)
                        offerings = cursor.fetchall()
                        print("   Sample offerings:")
                        for offering in offerings:
                            print(f"     • {offering['productName']} at {offering['storeName']}: ${offering['price']} (was ${offering['basePrice']}) - {offering['offerDetails']}")
                    
                    elif table == 'products' and count > 0:
                        cursor.execute("SELECT productName FROM products LIMIT 5")
                        products = cursor.fetchall()
                        print(f"   Sample products: {[p['productName'] for p in products]}")
                    
                    elif table == 'stores' and count > 0:
                        cursor.execute("SELECT storeName FROM stores LIMIT 5")
                        stores = cursor.fetchall()
                        print(f"   Sample stores: {[s['storeName'] for s in stores]}")
                    
                    elif table == 'etlJobs' and count > 0:
                        cursor.execute("""
                            SELECT jobId, sourceIdentifier, startTime, endTime, overallStatus, 
                                   totalItemExtracted, totalItemLoaded
                            FROM etlJobs 
                            ORDER BY startTime DESC 
                            LIMIT 3
                        """)
                        jobs = cursor.fetchall()
                        print("   Recent ETL jobs:")
                        for job in jobs:
                            status = job['overallStatus']
                            extracted = job['totalItemExtracted'] or 0
                            loaded = job['totalItemLoaded'] or 0
                            start_time = job['startTime']
                            print(f"     • {job['jobId']}: {status} - Extracted: {extracted}, Loaded: {loaded} ({start_time})")
                    
                except pymysql.Error as e:
                    print(f"❌ Error checking table '{table}': {str(e)}")
                
                print()
            
            # Check for recent ETL activity
            print("🔍 RECENT ETL ACTIVITY:")
            try:
                cursor.execute("""
                    SELECT COUNT(*) as job_count 
                    FROM etlJobs 
                    WHERE startTime >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                """)
                recent_jobs = cursor.fetchone()['job_count']
                print(f"   ETL jobs in last 7 days: {recent_jobs}")
                
                if recent_jobs > 0:
                    cursor.execute("""
                        SELECT jobId, sourceIdentifier, startTime, overallStatus
                        FROM etlJobs 
                        WHERE startTime >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                        ORDER BY startTime DESC
                    """)
                    jobs = cursor.fetchall()
                    for job in jobs:
                        print(f"     • {job['startTime']}: {job['sourceIdentifier']} -> {job['overallStatus']}")
                
            except pymysql.Error as e:
                print(f"   Error checking recent ETL activity: {str(e)}")
            
            print()
            
    finally:
        connection.close()

def main():
    """Main function"""
    print(f"🔍 Database Status Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check for environment variables
    env_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
    missing_vars = [var for var in env_vars if not os.environ.get(var)]
    
    if missing_vars:
        print("⚠️  Missing environment variables:")
        for var in missing_vars:
            print(f"   {var}")
        print()
        print("💡 You can set them like this:")
        print("   export DB_HOST='localhost'")
        print("   export DB_USER='ursaviour'") 
        print("   export DB_PASSWORD='your-password'")
        print("   export DB_NAME='ursaviourDb'")
        print()
        print("Using default values for missing variables...")
        print()
    
    check_database_status()

if __name__ == "__main__":
    main()