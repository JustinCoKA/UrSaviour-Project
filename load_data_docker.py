#!/usr/bin/env python3
"""
Docker-compatible Foundational Dataset Loader
Load foundational_dataset_v1.csv data into the database via Docker container
"""

import sys
import os
from pathlib import Path

def main():
    """Load foundational data using Docker container"""
    
    print("🚀 Starting Foundational Dataset Loader via Docker...")
    
    # Check if we're in the right directory
    if not Path("docker-compose.prod.yml").exists():
        print("❌ docker-compose.prod.yml not found. Please run from project root.")
        sys.exit(1)
    
    if not Path("data/foundational_dataset_v1.csv").exists():
        print("❌ foundational_dataset_v1.csv not found in data/ directory.")
        sys.exit(1)
    
    print("📋 This script will:")
    print("   1. Execute data loading inside the API Docker container")
    print("   2. Load 400 product-store price combinations")
    print("   3. Update products, stores, and storeOfferings tables")
    print("")
    
    confirm = input("Do you want to continue? (y/N): ")
    if confirm.lower() != 'y':
        print("❌ Cancelled by user.")
        sys.exit(0)
    
    # Create the Python script content for execution inside Docker
    docker_script = '''
import csv
import sys
from sqlalchemy import MetaData, Table, insert, delete, select, text
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from app.db.session import engine

def load_foundational_data():
    """Load foundational_dataset_v1.csv data into the database"""
    
    # Reflect database tables
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    # Required tables
    products_table = Table("products", metadata, autoload_with=engine)
    stores_table = Table("stores", metadata, autoload_with=engine) 
    store_offerings_table = Table("storeOfferings", metadata, autoload_with=engine)
    categories_table = Table("productCategories", metadata, autoload_with=engine)
    
    # CSV file path
    csv_path = "/data/foundational_dataset_v1.csv"
    
    if not Path(csv_path).exists():
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
            
            print("\\n🎉 Data loading completed!")
            print(f"   📊 Products: {len(products_data)} items")
            print(f"   🏪 Stores: {len(stores_data)} items") 
            print(f"   💰 Price info: {len(offerings_data)} items")
            print(f"\\n✅ Total {len(offerings_data)} product-store price data records are now ready!")
            
            return True
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error occurred during data loading: {e}")
            return False

if __name__ == "__main__":
    print("🚀 Starting Foundational Dataset Loader...")
    success = load_foundational_data()
    
    if success:
        print("\\n✅ All tasks completed successfully!")
        print("   The backend API can now provide 400 product-store price data records.")
    else:
        print("\\n❌ Task failed. Please check the logs.")
        sys.exit(1)
'''
    
    # Write the script to a temporary file
    script_path = Path("temp_load_data.py")
    with open(script_path, 'w') as f:
        f.write(docker_script)
    
    print("📦 Executing data loading inside Docker container...")
    
    # Execute the script inside the Docker container
    import subprocess
    
    try:
        result = subprocess.run([
            'docker-compose', '-f', 'docker-compose.prod.yml', 
            'exec', '-T', 'api', 
            'python', '/app/temp_load_data.py'
        ], capture_output=True, text=True, cwd='.')
        
        print("📤 Docker execution output:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Docker execution errors:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("\n✅ Data loading completed successfully!")
        else:
            print(f"\n❌ Data loading failed with exit code: {result.returncode}")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker execution failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ docker-compose command not found. Please ensure Docker Compose is installed.")
        return False
    finally:
        # Clean up temporary script
        if script_path.exists():
            script_path.unlink()
    
    # Copy the script into the container for execution
    print("📋 Copying script into Docker container...")
    subprocess.run([
        'docker', 'cp', 
        str(script_path), 
        'ursaviour-api-1:/app/temp_load_data.py'
    ], check=False)
    
    return True

if __name__ == "__main__":
    main()