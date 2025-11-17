#!/usr/bin/env python3
"""
Test Discount Data Connection
- Connects to AWS RDS
- Adds sample discount data
- Tests API response format
"""

import pymysql
import json
from datetime import datetime

# Database connection settings (from .env)
DB_CONFIG = {
    'host': 'ursaviour-db.cp4emoqegwfy.ap-southeast-2.rds.amazonaws.com',
    'port': 3306,
    'user': 'admin',
    'password': 'Ursaviour2025',
    'database': 'ursaviourDb',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def connect_db():
    """Connect to AWS RDS database"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        print("✅ Successfully connected to AWS RDS!")
        return connection
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

def add_stores(connection):
    """Add sample stores if not exist"""
    stores_data = [
        (1, 'Coles', 'Sydney CBD', '{"phone": "1300-635-035", "website": "https://www.coles.com.au"}'),
        (2, 'Woolworths', 'Sydney CBD', '{"phone": "1300-767-969", "website": "https://www.woolworths.com.au"}'),
        (3, 'ALDI', 'Sydney CBD', '{"phone": "1300-425-34", "website": "https://www.aldi.com.au"}')
    ]
    
    with connection.cursor() as cursor:
        for store in stores_data:
            sql = """
                INSERT IGNORE INTO stores (storeId, storeName, location, contactInfo)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, store)
        connection.commit()
        print(f"✅ Added {len(stores_data)} stores")

def add_base_prices(connection):
    """Add base prices for products"""
    base_prices = [
        (1, 'P0001', 7.50, '2025-01-01'),  # Coles
        (2, 'P0001', 7.99, '2025-01-01'),  # Woolworths
        (3, 'P0001', 6.50, '2025-01-01'),  # ALDI
    ]
    
    with connection.cursor() as cursor:
        for price in base_prices:
            sql = """
                INSERT INTO store_base_prices (storeId, productId, basePrice, effectiveDate)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    basePrice = VALUES(basePrice),
                    effectiveDate = VALUES(effectiveDate)
            """
            cursor.execute(sql, price)
        connection.commit()
        print(f"✅ Added {len(base_prices)} base prices")

def add_discount_offerings(connection):
    """Add discount offerings"""
    offerings = [
        (1, 'P0001', 5.25, '30% OFF - Buy 2 Get 1 Free', 'WEEK45_2025'),
        (2, 'P0001', 5.99, '25% OFF - Special Weekend Deal', 'WEEK45_2025'),
        (3, 'P0001', 5.20, '20% OFF - Member Exclusive', 'WEEK45_2025'),
        # Additional products
        (1, 'P0002', 0.79, 'Fresh Pick - 20% OFF', 'WEEK45_2025'),
        (2, 'P0002', 0.69, 'Super Fresh - 30% OFF', 'WEEK45_2025'),
        (3, 'P0002', 0.75, 'Daily Special', 'WEEK45_2025'),
        (1, 'P0003', 0.75, 'Half Price Sale', 'WEEK45_2025'),
        (2, 'P0003', 0.79, '20% OFF', 'WEEK45_2025'),
    ]
    
    with connection.cursor() as cursor:
        for offering in offerings:
            sql = """
                INSERT INTO storeOfferings (storeId, productId, price, offerDetails, batch_id, loaded_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
                ON DUPLICATE KEY UPDATE
                    price = VALUES(price),
                    offerDetails = VALUES(offerDetails),
                    loaded_at = NOW()
            """
            cursor.execute(sql, offering)
        connection.commit()
        print(f"✅ Added {len(offerings)} discount offerings")

def verify_discounts(connection):
    """Verify discount data"""
    sql = """
        SELECT 
            s.storeName,
            p.productName,
            p.basePrice as originalPrice,
            sbp.basePrice as storeBasePrice,
            so.price as discountPrice,
            ROUND(((COALESCE(sbp.basePrice, p.basePrice) - so.price) / COALESCE(sbp.basePrice, p.basePrice) * 100), 2) as discountPercent,
            so.offerDetails,
            so.loaded_at
        FROM storeOfferings so
        JOIN stores s ON so.storeId = s.storeId
        JOIN products p ON so.productId = p.productId
        LEFT JOIN store_base_prices sbp ON so.storeId = sbp.storeId AND so.productId = sbp.productId
        WHERE so.productId = 'P0001'
        ORDER BY so.price ASC
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql)
        results = cursor.fetchall()
        
        print("\n" + "="*80)
        print("📊 DISCOUNT DATA FOR P0001 (Mineral Water)")
        print("="*80)
        
        for row in results:
            print(f"""
Store: {row['storeName']}
Product: {row['productName']}
Original Price: ${row['storeBasePrice']:.2f}
Discount Price: ${row['discountPrice']:.2f}
Discount: {row['discountPercent']:.0f}% OFF
Offer Details: {row['offerDetails']}
Loaded At: {row['loaded_at']}
Savings: ${row['storeBasePrice'] - row['discountPrice']:.2f}
{'-'*80}
            """)
        
        return results

def test_api_format(connection):
    """Test API response format"""
    sql = """
        SELECT 
            p.productId,
            p.productName,
            p.categoryName,
            p.description,
            p.basePrice,
            p.defaultImageUrl
        FROM products p
        WHERE p.productId = 'P0001'
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql)
        product = cursor.fetchone()
        
        # Get store offerings
        sql_offerings = """
            SELECT 
                s.storeId,
                s.storeName,
                so.price,
                COALESCE(sbp.basePrice, p.basePrice) as originalPrice,
                so.offerDetails,
                ROUND(COALESCE(sbp.basePrice, p.basePrice) - so.price, 2) as savings,
                CONCAT(
                    ROUND(((COALESCE(sbp.basePrice, p.basePrice) - so.price) / COALESCE(sbp.basePrice, p.basePrice) * 100), 0),
                    '% OFF'
                ) as discount
            FROM storeOfferings so
            JOIN stores s ON so.storeId = s.storeId
            JOIN products p ON so.productId = p.productId
            LEFT JOIN store_base_prices sbp ON so.storeId = sbp.storeId AND so.productId = sbp.productId
            WHERE so.productId = 'P0001'
            ORDER BY so.price ASC
        """
        
        cursor.execute(sql_offerings)
        stores = cursor.fetchall()
        
        # Build API response format
        api_response = {
            'productId': product['productId'],
            'productName': product['productName'],
            'categoryName': product['categoryName'],
            'description': product['description'],
            'basePrice': float(product['basePrice']),
            'defaultImageUrl': product['defaultImageUrl'],
            'stores': [
                {
                    'storeId': store['storeId'],
                    'storeName': store['storeName'],
                    'price': float(store['price']),
                    'originalPrice': float(store['originalPrice']),
                    'discount': store['discount'],
                    'offerDetails': store['offerDetails'],
                    'savings': float(store['savings'])
                }
                for store in stores
            ]
        }
        
        print("\n" + "="*80)
        print("🔌 API RESPONSE FORMAT (JSON)")
        print("="*80)
        print(json.dumps(api_response, indent=2, ensure_ascii=False))
        print("="*80 + "\n")
        
        return api_response

def main():
    """Main execution"""
    print("🚀 Starting Discount Data Test...\n")
    
    # Connect to database
    connection = connect_db()
    if not connection:
        return
    
    try:
        # Add test data
        print("\n📝 Adding test data...")
        add_stores(connection)
        add_base_prices(connection)
        add_discount_offerings(connection)
        
        # Verify data
        print("\n🔍 Verifying discount data...")
        verify_discounts(connection)
        
        # Test API format
        print("\n🧪 Testing API response format...")
        test_api_format(connection)
        
        print("\n✅ All tests completed successfully!")
        print("\n💡 Next steps:")
        print("   1. Open http://localhost:3001/products.html")
        print("   2. Search for 'Mineral Water' or 'P0001'")
        print("   3. Check if discount prices appear correctly")
        print("   4. Verify store comparison shows all 3 stores\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        connection.close()
        print("🔒 Database connection closed")

if __name__ == "__main__":
    main()
