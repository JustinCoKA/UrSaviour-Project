#!/usr/bin/env python3
"""
UrSaviour API Test Script
EC2에서 실행하여 API 응답을 직접 테스트합니다.
"""

import requests
import json
import sys
from datetime import datetime

def test_api_endpoints():
    """API 엔드포인트 테스트"""
    
    print("🔍 UrSaviour API Diagnosis")
    print("=" * 40)
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # API 베이스 URL들
    api_bases = [
        "http://localhost:8000",  # Docker 내부
        "http://backend:8000",    # Docker 컨테이너명
        "http://127.0.0.1:8000",  # 로컬
    ]
    
    endpoints_to_test = [
        "/api/health",
        "/api/v1/products/health", 
        "/api/v1/products/?limit=3",
        "/api/v1/products/debug/counts"
    ]
    
    successful_base = None
    
    # API 베이스 URL 찾기
    for base_url in api_bases:
        try:
            print(f"🔍 Testing base URL: {base_url}")
            response = requests.get(f"{base_url}/api/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ Working API base: {base_url}")
                successful_base = base_url
                break
        except Exception as e:
            print(f"❌ Failed {base_url}: {str(e)}")
    
    if not successful_base:
        print("❌ No working API base URL found!")
        print("\n💡 Troubleshooting steps:")
        print("1. Check if backend container is running: docker ps")
        print("2. Check backend logs: docker-compose -f docker-compose.prod.yml logs backend")
        print("3. Try manual curl: curl http://localhost:8000/api/health")
        return
    
    print()
    
    # 각 엔드포인트 테스트
    for endpoint in endpoints_to_test:
        print(f"🔍 Testing: {endpoint}")
        print("-" * 40)
        
        try:
            url = f"{successful_base}{endpoint}"
            response = requests.get(url, timeout=10)
            
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print("Response JSON:")
                    print(json.dumps(data, indent=2, default=str))
                    
                    # 특별 분석: products 엔드포인트
                    if "products" in endpoint and isinstance(data, dict):
                        if "products" in data and isinstance(data["products"], list):
                            products = data["products"]
                            print(f"\n📊 Analysis: {len(products)} products found")
                            
                            if products:
                                first_product = products[0]
                                print("First product structure:")
                                print(f"- productId: {first_product.get('productId')}")
                                print(f"- productName: {first_product.get('productName')}")
                                print(f"- categoryName: {first_product.get('categoryName')}")
                                print(f"- stores count: {len(first_product.get('stores', []))}")
                                
                                if first_product.get('stores'):
                                    first_store = first_product['stores'][0]
                                    print("First store structure:")
                                    print(f"  - store_name: {first_store.get('store_name')}")
                                    print(f"  - final_price: {first_store.get('final_price')}")
                                    print(f"  - original_price: {first_store.get('original_price')}")
                        else:
                            print("⚠️  'products' key missing or not an array!")
                    
                except ValueError:
                    print("Response (non-JSON):")
                    print(response.text[:500])
            else:
                print(f"Error response: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
        
        print("\n" + "="*50 + "\n")
    
    print("✅ API diagnosis completed!")

if __name__ == "__main__":
    test_api_endpoints()