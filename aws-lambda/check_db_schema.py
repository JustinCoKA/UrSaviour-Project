#!/usr/bin/env python3
"""
Database schema and table verification script
"""

import pymysql
import os

def check_database_schema():
    """Check database schema and table structure"""
    
    DB_HOST = os.getenv('DB_HOST', 'ursaviour-db.cp4emoqegwfy.ap-southeast-2.rds.amazonaws.com')
    DB_USER = os.getenv('DB_USER', 'admin')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'Ursaviour2025')
    
    try:
        print("🔌 Attempting RDS connection...")
        
        # Database connection (without specifying schema)
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=10
        )
        
        cursor = conn.cursor()
        
        # 1. Check all databases
        print("\n📊 Available databases:")
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        for db in databases:
            db_name = list(db.values())[0]
            print(f"   - {db_name}")
        
        # 2. Select ursaviourDb database
        print(f"\n🎯 Selecting 'ursaviourDb' database...")
        cursor.execute("USE ursaviourDb")
        
        # 3. Check table list
        print("\n📋 Table list:")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        if not tables:
            print("   ⚠️ No tables found.")
        else:
            for table in tables:
                table_name = list(table.values())[0]
                print(f"   ✅ {table_name}")
                
                # Check record count for each table
                try:
                    cursor.execute(f"SELECT COUNT(*) as count FROM `{table_name}`")
                    count = cursor.fetchone()['count']
                    print(f"      → {count} records")
                    
                    # If storeOfferings table, also check sample data
                    if table_name == 'storeOfferings' and count > 0:
                        cursor.execute(f"SELECT * FROM `{table_name}` LIMIT 3")
                        samples = cursor.fetchall()
                        print(f"      Sample data:")
                        for sample in samples:
                            print(f"        {sample}")
                            
                except Exception as e:
                    print(f"      ❌ Failed to check record count: {e}")
        
        # 4. Special check for ETL-related tables
        etl_tables = ['etlJobs', 'etlJobLogs', 'storeOfferings']
        print(f"\n🔄 Detailed ETL-related table check:")
        
        for table in etl_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) as count FROM `{table}`")
                count = cursor.fetchone()['count']
                print(f"   {table}: {count} records")
                
                if count > 0:
                    cursor.execute(f"SELECT * FROM `{table}` ORDER BY id DESC LIMIT 2")
                    recent = cursor.fetchall()
                    print(f"     Recent data:")
                    for row in recent:
                        print(f"       {row}")
                        
            except pymysql.Error as e:
                print(f"   {table}: ❌ Table not found or inaccessible ({e})")
        
        conn.close()
        print("\n✅ Database check completed")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 UrSaviour Database Schema Check")
    print("=" * 60)
    check_database_schema()