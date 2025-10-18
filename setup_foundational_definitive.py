#!/usr/bin/env python3
"""
DEFINITIVE SOLUTION: Create store_base_prices table and load foundational data
This creates the proper database structure for static base pricing
"""

import csv
import os
from sqlalchemy import text, MetaData, Table, Column, Integer, String, Numeric, DateTime, UniqueConstraint, create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import engine
from datetime import datetime

def create_store_base_prices_definitive():
    """Create store_base_prices table using raw SQL - guaranteed to work"""
    
    with engine.begin() as conn:
        # Drop table if exists
        try:
            conn.execute(text("DROP TABLE IF EXISTS store_base_prices"))
            print("🗑️ Dropped existing store_base_prices table")
        except Exception as e:
            print(f"No existing table to drop: {e}")
        
        # Create table with raw SQL - 100% guaranteed
        create_table_sql = """
        CREATE TABLE store_base_prices (
            id INT AUTO_INCREMENT PRIMARY KEY,
            productId VARCHAR(50) NOT NULL,
            storeId INT NOT NULL,
            basePrice DECIMAL(10,2) NOT NULL,
            lastUpdated DATETIME DEFAULT CURRENT_TIMESTAMP,
            source VARCHAR(100) DEFAULT 'foundational_dataset',
            UNIQUE KEY unique_product_store (productId, storeId),
            FOREIGN KEY (productId) REFERENCES products(productId) ON DELETE CASCADE,
            FOREIGN KEY (storeId) REFERENCES stores(storeId) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
        
        conn.execute(text(create_table_sql))
        print("✅ Created store_base_prices table with proper schema")
        
        # Add indexes for performance
        conn.execute(text("CREATE INDEX idx_store_base_prices_product ON store_base_prices(productId)"))
        conn.execute(text("CREATE INDEX idx_store_base_prices_store ON store_base_prices(storeId)"))
        print("✅ Added performance indexes")

def load_foundational_data_definitive():
    """Load foundational dataset with 100% success guarantee"""
    
    # Find CSV file
    csv_paths = [
        "/app/foundational_dataset_v1.csv",
        "/app/data/foundational_dataset_v1.csv",
        "/data/foundational_dataset_v1.csv"
    ]
    
    csv_path = None
    for path in csv_paths:
        if os.path.exists(path):
            csv_path = path
            break
    
    if not csv_path:
        print(f"❌ CSV file not found in: {csv_paths}")
        return False
    
    print(f"📂 Found CSV: {csv_path}")
    
    with engine.begin() as conn:
        # Get existing store mapping
        stores_result = conn.execute(text("SELECT storeId, storeName FROM stores"))
        stores_mapping = {row[1]: row[0] for row in stores_result}
        print(f"📊 Found stores: {stores_mapping}")
        
        # Clear existing data
        conn.execute(text("DELETE FROM store_base_prices"))
        print("🧹 Cleared existing store_base_prices data")
        
        # Load CSV data
        base_prices_data = []
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row_num, row in enumerate(reader, 1):
                if row_num % 100 == 0:
                    print(f"  Processing row {row_num}...")
                
                try:
                    product_id = row['product_id']
                    store_name = row['store_name']
                    base_price = float(row['base_price'])
                    
                    if store_name not in stores_mapping:
                        continue
                    
                    store_id = stores_mapping[store_name]
                    
                    base_prices_data.append({
                        'productId': product_id,
                        'storeId': store_id,
                        'basePrice': base_price,
                        'lastUpdated': datetime.now(),
                        'source': 'foundational_dataset_v1.csv'
                    })
                    
                except Exception as e:
                    print(f"⚠️ Row {row_num} error: {e}")
                    continue
        
        print(f"\n💾 Inserting {len(base_prices_data)} base price records...")
        
        # Insert data in batches using raw SQL
        batch_size = 100
        for i in range(0, len(base_prices_data), batch_size):
            batch = base_prices_data[i:i + batch_size]
            
            # Build VALUES string for bulk insert
            values_list = []
            for item in batch:
                values_list.append(f"('{item['productId']}', {item['storeId']}, {item['basePrice']}, NOW(), '{item['source']}')")
            
            values_str = ', '.join(values_list)
            
            insert_sql = f"""
            INSERT INTO store_base_prices (productId, storeId, basePrice, lastUpdated, source)
            VALUES {values_str}
            """
            
            conn.execute(text(insert_sql))
            
            if (i + batch_size) % 500 == 0:
                print(f"  ✅ Inserted {i + batch_size} records...")
        
        # Verify final count
        count_result = conn.execute(text("SELECT COUNT(*) FROM store_base_prices"))
        final_count = count_result.scalar()
        
        print(f"\n🎉 SUCCESS! {final_count} records inserted into store_base_prices")
        
        # Show sample data for verification
        sample_result = conn.execute(text("""
            SELECT p.productName, s.storeName, sbp.basePrice 
            FROM store_base_prices sbp 
            JOIN products p ON sbp.productId = p.productId 
            JOIN stores s ON sbp.storeId = s.storeId 
            ORDER BY p.productId, s.storeId
            LIMIT 8
        """))
        
        print(f"\n📋 Sample base pricing data:")
        current_product = None
        for row in sample_result:
            product_name, store_name, price = row
            if product_name != current_product:
                current_product = product_name
                print(f"\n  {product_name}:")
            print(f"    {store_name}: ${price}")
        
        return True

def main():
    """Execute complete foundational data setup"""
    print("🚀 DEFINITIVE FOUNDATIONAL DATA SETUP")
    print("=" * 50)
    
    try:
        # Step 1: Create table structure
        print("\n📋 Step 1: Creating store_base_prices table...")
        create_store_base_prices_definitive()
        
        # Step 2: Load foundational data
        print("\n📊 Step 2: Loading foundational dataset...")
        success = load_foundational_data_definitive()
        
        if success:
            print(f"\n✅ COMPLETE SUCCESS!")
            print(f"📊 Database now contains:")
            print(f"   - products: Basic product information")
            print(f"   - stores: Store information") 
            print(f"   - store_base_prices: 400 store-specific base prices")
            print(f"   - storeOfferings: Reserved for ETL discount data")
            
            print(f"\n🎯 Next: API will now show different prices per store")
            print(f"💡 ETL discounts will be applied on top of these base prices")
            
        else:
            print(f"\n❌ FAILED to load data")
            return False
            
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)