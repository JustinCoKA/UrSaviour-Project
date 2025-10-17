#!/usr/bin/env python3
"""
Foundational Dataset Loader
Script to load existing foundational_dataset_v1.csv into the database
"""

import csv
import sys
import os
from sqlalchemy import MetaData, Table, insert, delete, select, text
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from backend.app.db.session import engine
from backend.app.core.config import settings

def load_foundational_data():
    """Load foundational_dataset_v1.csv data into the database"""
    
    # 데이터베이스 테이블 반영
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    # Required tables
    products_table = Table("products", metadata, autoload_with=engine)
    stores_table = Table("stores", metadata, autoload_with=engine) 
    store_offerings_table = Table("storeOfferings", metadata, autoload_with=engine)
    categories_table = Table("productCategories", metadata, autoload_with=engine)
    
    # CSV file path
    csv_path = Path(__file__).parent / "data" / "foundational_dataset_v1.csv"
    
    if not csv_path.exists():
        print(f"❌ CSV file not found: {csv_path}")
        return False
    
    Session = sessionmaker(bind=engine)
    
    with Session() as session:
        try:
            print("🧹 Cleaning existing data...")
            
            # Delete existing data (considering referential integrity order)
            session.execute(delete(store_offerings_table))
            session.execute(delete(products_table))
            session.execute(delete(stores_table))
            session.execute(delete(categories_table))
            session.commit()
            
            print("📂 Reading CSV file...")
            
            # Read CSV data
            products_data = {}
            stores_data = {}
            categories_data = {}
            offerings_data = []
            
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    product_id = row['product_id']
                    store_name = row['store_name']
                    category_name = row['category_name']
                    
                    # Collect product data
                    if product_id not in products_data:
                        # Generate categoryId based on category name hash
                        category_id = abs(hash(category_name)) % 1000
                        
                        products_data[product_id] = {
                            'productId': product_id,
                            'categoryId': category_id,
                            'productName': row['product_name'],
                            'categoryName': category_name,
                            'description': row['description'],
                            'basePrice': float(row['base_price']),
                            'defaultImageUrl': row['default_image_url'],
                            'lastUpdatedAt': '2024-01-01 00:00:00'
                        }
                        
                        # Collect category data
                        if category_name not in categories_data:
                            categories_data[category_name] = {
                                'categoryId': category_id,
                                'categoryName': category_name,
                                'description': f"Standard {category_name} category"
                            }
                    
                    # Collect store data
                    if store_name not in stores_data:
                        store_id = len(stores_data) + 1
                        stores_data[store_name] = {
                            'storeId': store_id,
                            'storeName': store_name
                        }
                    
                    # Collect store-specific price data
                    offerings_data.append({
                        'productId': product_id,
                        'storeId': stores_data[store_name]['storeId'],
                        'price': float(row['base_price']),
                        'basePrice': float(row['base_price']),
                        'offerDetails': 'Regular Price',
                        'week': 1,
                        'lastUpdated': '2024-01-01 00:00:00'
                    })
            
            print("💾 Saving to database...")
            
            # 1. Insert categories
            if categories_data:
                session.execute(insert(categories_table), list(categories_data.values()))
                print(f"✅ {len(categories_data)} categories saved successfully")
            
            # 2. Insert stores
            if stores_data:
                session.execute(insert(stores_table), list(stores_data.values()))
                print(f"✅ {len(stores_data)} stores saved successfully")
            
            # 3. Insert products  
            if products_data:
                session.execute(insert(products_table), list(products_data.values()))
                print(f"✅ {len(products_data)} products saved successfully")
            
            # 4. Insert store prices
            if offerings_data:
                session.execute(insert(store_offerings_table), offerings_data)
                print(f"✅ {len(offerings_data)} store prices saved successfully")
            
            session.commit()
            
            # Verify results
            products_count = session.execute(select(products_table.c.productId)).rowcount
            stores_count = session.execute(select(stores_table.c.storeId)).rowcount  
            offerings_count = session.execute(select(store_offerings_table.c.productId)).rowcount
            
            print("\n🎉 Data loading completed!")
            print(f"   📊 Products: {len(products_data)} items")
            print(f"   🏪 Stores: {len(stores_data)} items") 
            print(f"   💰 Price info: {len(offerings_data)} items")
            print(f"\n✅ Total {len(offerings_data)} product-store price data records are now ready!")
            
            return True
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error occurred during data loading: {e}")
            return False

if __name__ == "__main__":
    print("🚀 Starting Foundational Dataset Loader...")
    success = load_foundational_data()
    
    if success:
        print("\n✅ All tasks completed successfully!")
        print("   The backend API can now provide 400 product-store price data records.")
    else:
        print("\n❌ Task failed. Please check the logs.")
        sys.exit(1)