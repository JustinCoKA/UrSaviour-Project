#!/usr/bin/env python3
"""
Test CSV parsing with the fixed mapping
"""

import csv
import io
import re
from typing import Dict, Any

def clean_text(text: str) -> str:
    """Clean text content"""
    if not text:
        return ""
    cleaned = re.sub(r'\s+', ' ', str(text).strip())
    cleaned = cleaned.replace('\ufeff', '').replace('\x00', '')
    return cleaned

def map_csv_fields(csv_row: Dict[str, str]) -> Dict[str, Any]:
    """Map CSV fields to standard format"""
    field_mapping = {
        'store_name': 'storeName',
        'storeName': 'storeName',
        'product_name': 'productName',
        'productName': 'productName',
        'final_price': 'price',
        'price': 'price',
        'base_price': 'basePrice',
        'basePrice': 'basePrice',
        'discount_type': 'offerDetails',
        'offerDetails': 'offerDetails',
        'offer_details': 'offerDetails'
    }
    
    mapped = {}
    for csv_field, standard_field in field_mapping.items():
        if csv_field in csv_row and csv_row[csv_field]:
            value = csv_row[csv_field]
            if standard_field in ['basePrice', 'price']:
                try:
                    value = float(re.sub(r'[^\d.]', '', str(value)))
                except (ValueError, AttributeError):
                    print(f"Warning: Could not parse price value: {value}")
                    continue
            elif standard_field in ['storeName', 'productName', 'offerDetails']:
                value = clean_text(str(value))
            
            if standard_field not in mapped:
                mapped[standard_field] = value
    
    return mapped

def validate_discount_record(record: Dict[str, Any]) -> bool:
    """Validate discount record"""
    required_fields = ['productName', 'storeName', 'price', 'basePrice']
    
    for field in required_fields:
        if field not in record or not record[field]:
            return False
    
    try:
        price = float(record['price'])
        base_price = float(record['basePrice'])
        
        if price <= 0 or base_price <= 0:
            return False
        if price > base_price:
            print(f"Warning: Price higher than base price: {record}")
    except (ValueError, TypeError):
        return False
    
    return True

# Test with sample CSV data
csv_data = """product_id,product_name,category_name,description,store_name,base_price,default_image_url,discount_type,final_price
P0078,Rice,Health,Standard pack of rice,Mio Mart,8.09,/images/p/P0078.jpg,10% OFF,7.28
P0020,Yogurt Drink,Frozen,Standard pack of yogurt drink,Austin Fresh,7.46,/images/p/P0020.jpg,30% OFF,5.22
P0038,Grapes,Snacks,Standard pack of grapes,Aadarsh Deals,11.66,/images/p/P0038.jpg,Half Price,5.83"""

print("="*80)
print("Testing CSV Parsing and Validation")
print("="*80)

csv_reader = csv.DictReader(io.StringIO(csv_data))
valid_count = 0
invalid_count = 0

for row in csv_reader:
    print(f"\nRaw CSV row: {dict(row)}")
    
    mapped = map_csv_fields(row)
    print(f"Mapped: {mapped}")
    
    if validate_discount_record(mapped):
        print("✅ Valid record")
        valid_count += 1
    else:
        print("❌ Invalid record - missing fields:")
        required = ['productName', 'storeName', 'price', 'basePrice']
        for field in required:
            if field not in mapped:
                print(f"   - Missing: {field}")
        invalid_count += 1

print(f"\n{'='*80}")
print(f"Results: {valid_count} valid, {invalid_count} invalid")
print("="*80)
