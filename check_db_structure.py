#!/usr/bin/env python3
"""Check AWS RDS database structure"""
from sqlalchemy import create_engine, text, inspect
import sys

# Database connection
DATABASE_URL = "mysql+pymysql://admin:Ursaviour2025@ursaviour-db.cp4emoqegwfy.ap-southeast-2.rds.amazonaws.com:3306/ursaviourDb"

print("=" * 80)
print("AWS RDS MySQL Database Structure")
print("=" * 80)
print(f"Host: ursaviour-db.cp4emoqegwfy.ap-southeast-2.rds.amazonaws.com")
print(f"Database: ursaviourDb")
print("=" * 80)

try:
    engine = create_engine(DATABASE_URL, echo=False)
    
    with engine.connect() as conn:
        # Get all tables
        result = conn.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result]
        
        if not tables:
            print("\n⚠️  No tables found in database!")
            sys.exit(1)
        
        print(f"\n📊 Found {len(tables)} tables:\n")
        
        # For each table, show structure and row count
        for table in tables:
            print("-" * 80)
            print(f"📋 Table: {table}")
            print("-" * 80)
            
            # Get row count
            result = conn.execute(text(f"SELECT COUNT(*) FROM `{table}`"))
            count = result.scalar()
            print(f"   Rows: {count}")
            
            # Get table structure
            result = conn.execute(text(f"DESCRIBE `{table}`"))
            columns = result.fetchall()
            
            print(f"   Columns:")
            for col in columns:
                field, type_, null, key, default, extra = col
                key_str = f" [{key}]" if key else ""
                extra_str = f" {extra}" if extra else ""
                null_str = " NULL" if null == "YES" else " NOT NULL"
                print(f"      - {field}: {type_}{key_str}{null_str}{extra_str}")
            
            # Show sample data if available
            if count > 0:
                result = conn.execute(text(f"SELECT * FROM `{table}` LIMIT 3"))
                sample_data = result.fetchall()
                column_names = result.keys()
                
                print(f"\n   Sample data (first 3 rows):")
                for i, row in enumerate(sample_data, 1):
                    print(f"      Row {i}:")
                    for col_name, value in zip(column_names, row):
                        # Truncate long values
                        str_value = str(value)
                        if len(str_value) > 50:
                            str_value = str_value[:47] + "..."
                        print(f"         {col_name}: {str_value}")
            
            print()
        
        print("=" * 80)
        print("✅ Database structure check completed!")
        print("=" * 80)
        
except Exception as e:
    print(f"\n❌ Error connecting to database: {e}")
    sys.exit(1)
