#!/usr/bin/env python3
"""
Simple ETL Script for foundational dataset
This script runs inside the Docker container where SQLAlchemy is available
"""

import csv
from pathlib import Path
from sqlalchemy import MetaData, Table, insert, delete
from sqlalchemy.orm import sessionmaker
from app.db.session import engine

def load_foundational_data():
    """Load foundational_dataset_v1.csv data into the database"""
    
    # Reflect database tables
    metadata = MetaData()
    
    try:
        metadata.reflect(bind=engine)
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return False
    
    # Get tables
    products_table = metadata.tables.get("products")
    stores_table = metadata.tables.get("stores") 
    store_offerings_table = metadata.tables.get("storeOfferings")
    categories_table = metadata.tables.get("productCategories")
    
    if not all([products_table, stores_table, store_offerings_table, categories_table]):
        print("❌ Required database tables not found")
        print(f"Available tables: {list(metadata.tables.keys())}")
        return False
    
    # CSV file path - try multiple locations
    possible_paths = [
        "/data/foundational_dataset_v1.csv",
        "/app/data/foundational_dataset_v1.csv", 
        "./data/foundational_dataset_v1.csv",
        "../data/foundational_dataset_v1.csv"
    ]
    
    csv_path = None
    for path in possible_paths:
        if Path(path).exists():
            csv_path = path
            break
    
    if not csv_path:
        print(f"❌ CSV file not found in any of these locations: {possible_paths}")
        return False
    
    print(f"📂 Found CSV file: {csv_path}")
    
    Session = sessionmaker(bind=engine)
    
    with Session() as session:
        try:
            print("🧹 Cleaning existing data...")
            
            # Delete existing data (referential integrity order)
            session.execute(delete(store_offerings_table))
            session.execute(delete(products_table))  
            session.execute(delete(stores_table))
            session.execute(delete(categories_table))
            session.commit()
            
            print("📂 Reading CSV file...")
            
            products_data = {}
            stores_data = {}
            categories_data = {}
            offerings_data = []
            
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        product_id = row['product_id']
                        store_name = row['store_name']  
                        category_name = row['category_name']
                        
                        # Collect product data
                        if product_id not in products_data:
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
                        
                        # Collect store price data
                        offerings_data.append({
                            'productId': product_id,
                            'storeId': stores_data[store_name]['storeId'],
                            'price': float(row['base_price']),
                            'basePrice': float(row['base_price']),
                            'offerDetails': 'Regular Price',
                            'week': 1,
                            'lastUpdated': '2024-01-01 00:00:00'
                        })
                        
                    except Exception as e:
                        print(f"⚠️ Error processing row {row_num}: {e}")
                        continue
            
            print("💾 Saving to database...")
            
            # Insert data
            if categories_data:
                session.execute(insert(categories_table), list(categories_data.values()))
                print(f"✅ {len(categories_data)} categories saved")
            
            if stores_data:
                session.execute(insert(stores_table), list(stores_data.values()))
                print(f"✅ {len(stores_data)} stores saved")
            
            if products_data:
                session.execute(insert(products_table), list(products_data.values()))
                print(f"✅ {len(products_data)} products saved")
            
            if offerings_data:
                session.execute(insert(store_offerings_table), offerings_data)
                print(f"✅ {len(offerings_data)} store prices saved")
            
            session.commit()
            
            print("\n🎉 Data loading completed!")
            print(f"   📊 Products: {len(products_data)}")
            print(f"   🏪 Stores: {len(stores_data)}") 
            print(f"   💰 Store prices: {len(offerings_data)}")
            
            return True
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error during data loading: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("🚀 Starting foundational dataset loader...")
    success = load_foundational_data()
    
    if success:
        print("\n✅ Success! Database now contains foundational dataset.")
    else:
        print("\n❌ Failed to load data.")
        exit(1)