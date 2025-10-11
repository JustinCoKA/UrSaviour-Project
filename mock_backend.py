#!/usr/bin/env python3
"""
Simple mock backend server to test frontend API integration
"""
import json
import http.server
import socketserver
from urllib.parse import parse_qs, urlparse

class MockAPIHandler(http.server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', 'http://localhost:3001')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Origin')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/v1/products/products':
            # Mock products response
            mock_products = [
                {
                    "id": "P0001",
                    "name": "Mock Mineral Water",
                    "category": "Beverages",
                    "description": "Mock product from test server",
                    "image": "/images/p/P0001.jpg",
                    "stores": [
                        {"brand": "Mock Store A", "price": 5.99, "original_price": None},
                        {"brand": "Mock Store B", "price": 3.99, "original_price": 7.99},
                        {"brand": "Mock Store C", "price": 6.49, "original_price": None},
                        {"brand": "Mock Store D", "price": 5.79, "original_price": None}
                    ],
                    "special": {"type": "Half Price", "store": "Mock Store B"}
                },
                {
                    "id": "P0002", 
                    "name": "Mock Bread",
                    "category": "Bakery",
                    "description": "Test bread from mock server",
                    "image": "/images/p/P0002.jpg",
                    "stores": [
                        {"brand": "Mock Store A", "price": 2.99, "original_price": None},
                        {"brand": "Mock Store B", "price": 2.85, "original_price": None},
                        {"brand": "Mock Store C", "price": 1.99, "original_price": 3.99},
                        {"brand": "Mock Store D", "price": 3.15, "original_price": None}
                    ],
                    "special": {"type": "50% OFF", "store": "Mock Store C"}
                }
            ]
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', 'http://localhost:3001')
            self.send_header('Access-Control-Allow-Credentials', 'true')
            self.end_headers()
            
            response_data = json.dumps(mock_products)
            self.wfile.write(response_data.encode('utf-8'))
            print(f"✓ Served mock products response ({len(mock_products)} products)")
            
        elif parsed_path.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', 'http://localhost:3001')
            self.end_headers()
            self.wfile.write(b'{"status": "ok", "server": "mock"}')
            
        else:
            self.send_response(404)
            self.send_header('Access-Control-Allow-Origin', 'http://localhost:3001')
            self.end_headers()
            self.wfile.write(b'{"error": "Not Found"}')

if __name__ == '__main__':
    PORT = 8000
    with socketserver.TCPServer(("", PORT), MockAPIHandler) as httpd:
        print(f"🚀 Mock API server running on http://localhost:{PORT}")
        print(f"📡 CORS enabled for http://localhost:3001")
        print(f"🔗 Test endpoint: http://localhost:{PORT}/api/v1/products/products")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n✋ Mock server stopped")