#!/usr/bin/env python3
"""
Comprehensive database status checker
Connects to database and inspects all relevant tables
"""

import pymysql
import os
from datetime import datetime

# Database configuration from environment or docker-compose defaults
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USER', 'ursaviour'),
    'password': os.environ.get('DB_PASSWORD', 'ursaviour123'),
    'database': os.environ.get('DB_NAME', 'ursaviourDb')
}

def print_section(title):
    """Print section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def check_database_status():
    """Check comprehensive database status"""
    try:
        print_section("DATABASE CONNECTION TEST")
        print(f"Attempting to connect to: {DB_CONFIG['user']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
        
        # Connect to database
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("✅ Connection successful!")
        
        with connection.cursor() as cursor:
            # Check storeOfferings table
            print_section("STORE OFFERINGS TABLE")
            cursor.execute("SELECT COUNT(*) as count FROM storeOfferings")
            count = cursor.fetchone()['count']
            print(f"Total records: {count}")
            
            if count > 0:
                print("\n📊 Sample records (first 10):")
                cursor.execute("""
                    SELECT so.offeringId, p.productName, s.storeName, 
                           so.price, so.basePrice, so.offerDetails, so.loaded_at
                    FROM storeOfferings so
                    JOIN products p ON so.productId = p.productId
                    JOIN stores s ON so.storeId = s.storeId
                    ORDER BY so.loaded_at DESC
                    LIMIT 10
                """)
                offerings = cursor.fetchall()
                for offer in offerings:
                    print(f"  • {offer['productName']} @ {offer['storeName']}")
                    print(f"    Price: ${offer['price']} (was ${offer['basePrice']}) - {offer['offerDetails']}")
                    print(f"    Loaded: {offer['loaded_at']}")
            else:
                print("⚠️  No records found in storeOfferings table")
            
            # Check products table
            print_section("PRODUCTS TABLE")
            cursor.execute("SELECT COUNT(*) as count FROM products")
            count = cursor.fetchone()['count']
            print(f"Total products: {count}")
            
            if count > 0:
                cursor.execute("SELECT productId, productName FROM products LIMIT 5")
                products = cursor.fetchall()
                print("\nSample products:")
                for p in products:
                    print(f"  • [{p['productId']}] {p['productName']}")
            
            # Check stores table
            print_section("STORES TABLE")
            cursor.execute("SELECT COUNT(*) as count FROM stores")
            count = cursor.fetchone()['count']
            print(f"Total stores: {count}")
            
            if count > 0:
                cursor.execute("SELECT storeId, storeName FROM stores LIMIT 5")
                stores = cursor.fetchall()
                print("\nSample stores:")
                for s in stores:
                    print(f"  • [{s['storeId']}] {s['storeName']}")
            
            # Check ETL job logs if table exists
            print_section("ETL JOB LOGS")
            try:
                cursor.execute("SELECT COUNT(*) as count FROM etlJobs")
                count = cursor.fetchone()['count']
                print(f"Total ETL jobs: {count}")
                
                if count > 0:
                    cursor.execute("""
                        SELECT jobId, sourceIdentifier, startTime, endTime, 
                               overallStatus, totalItemExtracted, totalItemLoaded
                        FROM etlJobs
                        ORDER BY startTime DESC
                        LIMIT 5
                    """)
                    jobs = cursor.fetchall()
                    print("\nRecent ETL jobs:")
                    for job in jobs:
                        print(f"  • Job: {job['jobId']}")
                        print(f"    Source: {job['sourceIdentifier']}")
                        print(f"    Status: {job['overallStatus']}")
                        print(f"    Extracted: {job['totalItemExtracted']}, Loaded: {job['totalItemLoaded']}")
                        print(f"    Time: {job['startTime']} -> {job['endTime']}")
            except pymysql.err.ProgrammingError:
                print("⚠️  etlJobs table does not exist")
            
            # Check table structure
            print_section("STORE OFFERINGS TABLE STRUCTURE")
            cursor.execute("DESCRIBE storeOfferings")
            columns = cursor.fetchall()
            print("\nColumn definitions:")
            for col in columns:
                print(f"  • {col['Field']}: {col['Type']} {col['Null']} {col['Key']} {col['Default']}")
        
        connection.close()
        
        print_section("SUMMARY")
        print("✅ Database is accessible and has proper structure")
        print(f"🕐 Check completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except pymysql.err.OperationalError as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Troubleshooting tips:")
        print("  1. Make sure database is running (docker-compose up -d)")
        print("  2. Check connection parameters:")
        print(f"     Host: {DB_CONFIG['host']}")
        print(f"     Port: {DB_CONFIG['port']}")
        print(f"     User: {DB_CONFIG['user']}")
        print(f"     Database: {DB_CONFIG['database']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database_status()
