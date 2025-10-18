#!/usr/bin/env python3
"""
Load foundational dataset - FINAL FIXED VERSION
Correct SQLAlchemy imports for production environment
"""

import csv
import os
from sqlalchemy import MetaData, Table, insert, delete, Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.types import Numeric
from sqlalchemy.orm import sessionmaker
from app.db.session import engine
from datetime import datetime

def create_store_base_prices_table():
    """Create store_base_prices table with correct SQLAlchemy syntax"""
    
    metadata = MetaData()
    
    try:
        # Try to reflect existing table
        metadata.reflect(bind=engine)
        if 'store_base_prices' in metadata.tables:
            print("✅ store_base_prices table already exists")
            return metadata.tables['store_base_prices']
    except Exception as e:
        print(f"Reflecting metadata: {e}")
    
    # Create new table with correct types
    store_base_prices = Table('store_base_prices', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('productId', String(50), nullable=False),
        Column('storeId', Integer, nullable=False),  
        Column('basePrice', Numeric(10, 2), nullable=False),  # Use Numeric instead of Decimal
        Column('lastUpdated', DateTime, default=datetime.utcnow),
        Column('source', String(100), default='foundational_dataset'),
        UniqueConstraint('productId', 'storeId', name='unique_product_store_base_price')
    )
    
    try:
        metadata.create_all(engine)
        print("✅ Created store_base_prices table")
    except Exception as e:
        print(f"Error creating table: {e}")
        # Try to reflect again in case table was created by another process
        try:
            metadata.reflect(bind=engine)
            if 'store_base_prices' in metadata.tables:
                print("✅ store_base_prices table found after reflection")
                return metadata.tables['store_base_prices']
        except:
            pass
        raise e
    
    return store_base_prices

def load_foundational_data_final():
    """Load foundational dataset with store-specific pricing"""
    
    # Get existing tables
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    products_table = metadata.tables.get("products")
    stores_table = metadata.tables.get("stores") 
    categories_table = metadata.tables.get("productCategories")
    
    if not all([products_table, stores_table, categories_table]):
        print("❌ Required tables not found")
        print(f"Available tables: {list(metadata.tables.keys())}")
        return False
    
    # Create store_base_prices table
    try:
        store_base_prices_table = create_store_base_prices_table()
    except Exception as e:
        print(f"❌ Failed to create store_base_prices table: {e}")
        return False
    
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
    
    Session = sessionmaker(bind=engine)
    
    with Session() as session:
        try:
            print("🧹 Clearing existing store_base_prices data...")
            
            # Only clear store_base_prices, keep existing products/stores
            session.execute(delete(store_base_prices_table))
            session.commit()
            
            print("📂 Reading CSV and building store-specific prices...")
            
            base_prices_data = []
            stores_mapping = {}
            
            # Get existing stores
            stores_query = session.execute(stores_table.select())
            for store in stores_query:
                stores_mapping[store.storeName] = store.storeId
            
            print(f"Found existing stores: {list(stores_mapping.keys())}")
            
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
                            print(f"⚠️ Unknown store: {store_name}")
                            continue
                        
                        store_id = stores_mapping[store_name]
                        
                        base_prices_data.append({
                            'productId': product_id,
                            'storeId': store_id,
                            'basePrice': base_price,
                            'lastUpdated': datetime.utcnow(),
                            'source': 'foundational_dataset_v1.csv'
                        })
                        
                    except Exception as e:
                        print(f"⚠️ Error processing row {row_num}: {e}")
                        continue
            
            print(f"\n💾 Inserting {len(base_prices_data)} store base prices...")
            
            if base_prices_data:
                # Insert in batches for better performance
                batch_size = 100
                for i in range(0, len(base_prices_data), batch_size):
                    batch = base_prices_data[i:i+batch_size]
                    session.execute(insert(store_base_prices_table), batch)
                    if i % 500 == 0:
                        print(f"  Inserted {i + len(batch)} records...")
                
                session.commit()
                print(f"✅ {len(base_prices_data)} store base prices saved")
            
            # Verify results
            count_query = session.execute(f"SELECT COUNT(*) FROM store_base_prices").scalar()
            print(f"\n🔍 Verification: {count_query} records in store_base_prices table")
            
            # Show sample data
            sample_query = session.execute("""
                SELECT p.productId, p.productName, s.storeName, sbp.basePrice 
                FROM store_base_prices sbp 
                JOIN products p ON sbp.productId = p.productId 
                JOIN stores s ON sbp.storeId = s.storeId 
                LIMIT 8
            """).fetchall()
            
            print(f"\n📋 Sample store-specific pricing:")
            current_product = None
            for row in sample_query:
                if row[0] != current_product:
                    current_product = row[0]
                    print(f"\n  {row[1]} ({row[0]}):")
                print(f"    {row[2]}: ${row[3]}")
            
            return True
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error during data loading: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("🚀 Loading foundational dataset with store-specific base pricing...")
    print("🎯 Goal: Create 400 records (100 products × 4 stores) with different prices per store")
    
    success = load_foundational_data_final()
    
    if success:
        print("\n✅ SUCCESS! Store-specific base pricing loaded.")
        print("\n🔍 Next steps:")
        print("1. Check API: curl http://localhost:8000/api/v1/products/debug/counts")
        print("2. Verify pricing: curl http://localhost:8000/api/v1/products/ | jq '.products[0].stores'")
        print("3. You should see different prices per store now!")
    else:
        print("\n❌ FAILED to load store-specific pricing.")
        exit(1)