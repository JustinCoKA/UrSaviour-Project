#!/usr/bin/env python3
"""
Load foundational dataset with separate base pricing structure
foundational_dataset_v1.csv → store_base_prices table (매장별 기본가격)
"""

import csv
from sqlalchemy import MetaData, Table, insert, delete, create_table, Column, Integer, String, Decimal, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import sessionmaker
from app.db.session import engine
from datetime import datetime

def create_store_base_prices_table():
    """Create store_base_prices table if it doesn't exist"""
    
    metadata = MetaData()
    
    try:
        # Try to reflect existing table
        metadata.reflect(bind=engine)
        if 'store_base_prices' in metadata.tables:
            print("✅ store_base_prices table already exists")
            return metadata.tables['store_base_prices']
    except:
        pass
    
    # Create new table
    store_base_prices = Table('store_base_prices', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('productId', String(50), nullable=False),
        Column('storeId', Integer, nullable=False),  
        Column('basePrice', Decimal(10, 2), nullable=False),
        Column('lastUpdated', DateTime, default=datetime.utcnow),
        Column('source', String(100), default='foundational_dataset'),
        UniqueConstraint('productId', 'storeId', name='unique_product_store_base_price')
    )
    
    metadata.create_all(engine)
    print("✅ Created store_base_prices table")
    
    return store_base_prices

def load_foundational_data_v2():
    """Load foundational dataset into proper table structure"""
    
    # Create/get tables
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    products_table = metadata.tables.get("products")
    stores_table = metadata.tables.get("stores") 
    categories_table = metadata.tables.get("productCategories")
    
    # Create store_base_prices table
    store_base_prices_table = create_store_base_prices_table()
    
    if not all([products_table, stores_table, categories_table]):
        print("❌ Required tables not found")
        return False
    
    # CSV file path
    csv_path = "/app/foundational_dataset_v1.csv"
    
    Session = sessionmaker(bind=engine)
    
    with Session() as session:
        try:
            print("🧹 Cleaning existing foundational data...")
            
            # Clear existing foundational data
            session.execute(delete(store_base_prices_table))
            session.execute(delete(products_table))  
            session.execute(delete(stores_table))
            session.execute(delete(categories_table))
            session.commit()
            
            print("📂 Reading foundational CSV...")
            
            products_data = {}
            stores_data = {}
            categories_data = {}
            base_prices_data = []
            
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        product_id = row['product_id']
                        store_name = row['store_name']  
                        category_name = row['category_name']
                        base_price = float(row['base_price'])
                        
                        # Collect unique products (without price info)
                        if product_id not in products_data:
                            category_id = abs(hash(category_name)) % 1000
                            
                            products_data[product_id] = {
                                'productId': product_id,
                                'categoryId': category_id,
                                'productName': row['product_name'],
                                'categoryName': category_name,
                                'description': row['description'],
                                'basePrice': base_price,  # 첫 번째 가격을 기본으로
                                'defaultImageUrl': row['default_image_url'],
                                'lastUpdatedAt': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                            }
                            
                            # Collect unique categories
                            if category_name not in categories_data:
                                categories_data[category_name] = {
                                    'categoryId': category_id,
                                    'categoryName': category_name,
                                    'description': f"Standard {category_name} category"
                                }
                        
                        # Collect unique stores
                        if store_name not in stores_data:
                            store_id = len(stores_data) + 1
                            stores_data[store_name] = {
                                'storeId': store_id,
                                'storeName': store_name
                            }
                        
                        # Collect base prices per store per product
                        base_prices_data.append({
                            'productId': product_id,
                            'storeId': stores_data[store_name]['storeId'],
                            'basePrice': base_price,
                            'lastUpdated': datetime.utcnow(),
                            'source': 'foundational_dataset_v1.csv'
                        })
                        
                    except Exception as e:
                        print(f"⚠️ Error processing row {row_num}: {e}")
                        continue
            
            print("💾 Saving to database...")
            
            # Insert foundational data
            if categories_data:
                session.execute(insert(categories_table), list(categories_data.values()))
                print(f"✅ {len(categories_data)} categories saved")
            
            if stores_data:
                session.execute(insert(stores_table), list(stores_data.values()))
                print(f"✅ {len(stores_data)} stores saved")
            
            if products_data:
                session.execute(insert(products_table), list(products_data.values()))
                print(f"✅ {len(products_data)} products saved")
            
            if base_prices_data:
                session.execute(insert(store_base_prices_table), base_prices_data)
                print(f"✅ {len(base_prices_data)} store base prices saved")
            
            session.commit()
            
            print("\n🎉 Foundational data loading completed!")
            print(f"   📊 Products: {len(products_data)}")
            print(f"   🏪 Stores: {len(stores_data)}") 
            print(f"   💰 Store base prices: {len(base_prices_data)}")
            print(f"   📁 Categories: {len(categories_data)}")
            
            return True
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error during foundational data loading: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("🚀 Loading foundational dataset with new structure...")
    success = load_foundational_data_v2()
    
    if success:
        print("\n✅ Success! Database now contains:")
        print("   - products: Basic product information")  
        print("   - store_base_prices: Store-specific base pricing")
        print("   - storeOfferings: Reserved for ETL discount data")
    else:
        print("\n❌ Failed to load foundational data.")
        exit(1)