#!/usr/bin/env python3
"""
Quick data loader for EC2 - run this inside the Docker container
This script specifically handles the store offerings that are missing
"""

import csv
import os
from sqlalchemy import MetaData, Table, insert, delete, select
from app.db.session import engine

def fix_store_offerings():
    """Load missing store offerings from CSV"""
    
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    store_offerings_table = metadata.tables.get("storeOfferings")
    if not store_offerings_table:
        print("❌ storeOfferings table not found")
        return False
    
    # Check if CSV exists in container
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
        print(f"❌ CSV not found. Checked: {csv_paths}")
        return False
        
    print(f"📂 Using CSV: {csv_path}")
    
    # Store name to ID mapping
    store_mapping = {
        "Justin Groceries": 1,
        "Mio Mart": 2, 
        "Austin Fresh": 3,
        "Aadarsh Deals": 4
    }
    
    offerings_data = []
    
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            store_name = row['store_name']
            if store_name in store_mapping:
                offerings_data.append({
                    'productId': row['product_id'],
                    'storeId': store_mapping[store_name],
                    'price': float(row['base_price']),
                    'basePrice': float(row['base_price']),
                    'offerDetails': 'Regular Price',
                    'week': 1,
                    'lastUpdated': '2024-01-01 00:00:00'
                })
    
    if not offerings_data:
        print("❌ No valid data found in CSV")
        return False
    
    # Clear existing offerings and insert new ones
    with engine.begin() as conn:
        # Clear existing
        conn.execute(delete(store_offerings_table))
        
        # Insert new offerings
        conn.execute(insert(store_offerings_table), offerings_data)
        
        print(f"✅ Inserted {len(offerings_data)} store offerings")
        
        # Verify count
        count = conn.execute(select(store_offerings_table.c.productId).distinct()).rowcount
        print(f"📊 Unique products with pricing: {count}")
        
    return True

if __name__ == "__main__":
    print("🚀 Fixing store offerings...")
    success = fix_store_offerings()
    print("✅ Done!" if success else "❌ Failed!")