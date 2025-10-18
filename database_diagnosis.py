#!/usr/bin/env python3
"""
UrSaviour Database Diagnosis Script
EC2에서 실행하여 데이터베이스 상태를 진단합니다.
"""

import os
import sys
from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.orm import sessionmaker
import json
from datetime import datetime

def get_database_connection():
    """데이터베이스 연결 설정"""
    
    # 환경변수에서 데이터베이스 정보 가져오기 (Docker 환경)
    database_configs = [
        {
            'name': 'Docker Environment Variables',
            'url': f"mysql+pymysql://{os.getenv('MYSQL_USER', 'root')}:{os.getenv('MYSQL_PASSWORD', 'password')}@{os.getenv('MYSQL_HOST', 'mysql')}:{os.getenv('MYSQL_PORT', '3306')}/{os.getenv('MYSQL_DATABASE', 'ursaviour')}"
        },
        {
            'name': 'Local MySQL',
            'url': "mysql+pymysql://root:password@localhost:3306/ursaviour"
        },
        {
            'name': 'RDS MySQL (if using AWS RDS)',
            'url': "mysql+pymysql://admin:password@ursaviour-db.amazonaws.com:3306/ursaviour"
        }
    ]
    
    for config in database_configs:
        try:
            print(f"🔍 Trying connection: {config['name']}")
            engine = create_engine(config['url'])
            # Test connection
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            print(f"✅ Successfully connected using: {config['name']}")
            return engine
        except Exception as e:
            print(f"❌ Failed to connect using {config['name']}: {str(e)}")
            continue
    
    return None

def diagnose_database():
    """데이터베이스 진단 실행"""
    
    print("🔍 UrSaviour Database Diagnosis")
    print("=" * 50)
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # 데이터베이스 연결
    engine = get_database_connection()
    if not engine:
        print("❌ Could not connect to any database configuration")
        print("\n💡 Manual connection options:")
        print("1. Check Docker containers: docker-compose -f docker-compose.prod.yml ps")
        print("2. Check MySQL logs: docker-compose -f docker-compose.prod.yml logs mysql")
        print("3. Try manual connection: docker exec -it <mysql_container> mysql -u root -p")
        return
    
    try:
        with engine.connect() as conn:
            print("📊 Database Tables Analysis")
            print("-" * 30)
            
            # 테이블 존재 확인
            tables_check = [
                "products",
                "stores", 
                "store_base_prices",
                "storeOfferings"
            ]
            
            existing_tables = []
            for table_name in tables_check:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) as count FROM {table_name}"))
                    count = result.fetchone()[0]
                    existing_tables.append(table_name)
                    print(f"✅ {table_name}: {count} records")
                except Exception as e:
                    print(f"❌ {table_name}: Table not found or error - {str(e)}")
            
            print()
            
            # 샘플 데이터 확인
            if "products" in existing_tables:
                print("📋 Sample Products Data")
                print("-" * 20)
                result = conn.execute(text("SELECT productId, productName, categoryName, basePrice FROM products LIMIT 5"))
                for row in result:
                    print(f"ID: {row[0]}, Name: {row[1]}, Category: {row[2]}, Price: {row[3]}")
                print()
            
            if "stores" in existing_tables:
                print("🏪 Stores Data")
                print("-" * 15)
                result = conn.execute(text("SELECT storeId, storeName FROM stores"))
                for row in result:
                    print(f"Store {row[0]}: {row[1]}")
                print()
            
            if "store_base_prices" in existing_tables:
                print("💰 Store Base Prices Sample")
                print("-" * 25)
                result = conn.execute(text("SELECT productId, storeId, basePrice FROM store_base_prices LIMIT 10"))
                for row in result:
                    print(f"Product {row[0]} at Store {row[1]}: ${row[2]}")
                print()
            
            # API 테스트 데이터 생성
            print("🔍 API Response Simulation")
            print("-" * 25)
            
            # 실제 API와 같은 쿼리 실행
            if all(table in existing_tables for table in ["products", "stores", "store_base_prices"]):
                query = text("""
                    SELECT 
                        p.productId, p.productName, p.categoryName, p.description, p.defaultImageUrl, p.basePrice,
                        s.storeId, s.storeName, sbp.basePrice as store_base_price
                    FROM products p
                    CROSS JOIN stores s
                    LEFT JOIN store_base_prices sbp ON p.productId = sbp.productId AND s.storeId = sbp.storeId
                    WHERE p.productId IN (SELECT productId FROM products LIMIT 2)
                    ORDER BY p.productId, s.storeId
                """)
                
                result = conn.execute(query)
                api_data = {}
                
                for row in result:
                    product_id = row[0]
                    if product_id not in api_data:
                        api_data[product_id] = {
                            'productId': row[0],
                            'productName': row[1],
                            'categoryName': row[2],
                            'description': row[3],
                            'defaultImageUrl': row[4],
                            'basePrice': float(row[5]),
                            'stores': []
                        }
                    
                    api_data[product_id]['stores'].append({
                        'store_id': row[6],
                        'store_name': row[7],
                        'final_price': float(row[8]) if row[8] else float(row[5]),
                        'original_price': float(row[8]) if row[8] else float(row[5])
                    })
                
                print("Sample API Response Structure:")
                for product in list(api_data.values())[:1]:  # Show first product
                    print(json.dumps(product, indent=2))
            
            print("\n✅ Database diagnosis completed successfully!")
            
    except Exception as e:
        print(f"❌ Error during diagnosis: {str(e)}")
    finally:
        engine.dispose()

if __name__ == "__main__":
    diagnose_database()