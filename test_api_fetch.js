// Test script to simulate frontend API fetch
const isLocal = ["localhost", "127.0.0.1"].includes("localhost") || "file:" === 'http:';
const API_BASE = isLocal ? "http://localhost:8000" : "http://localhost:8000";
const PRODUCTS_ENDPOINT = `${API_BASE}/api/v1/products/products`;

async function testFetch() {
  try {
    console.log(`[Test] Attempting fetch to: ${PRODUCTS_ENDPOINT}?limit=3`);
    console.log(`[Test] isLocal: ${isLocal}`);
    
    const url = `${PRODUCTS_ENDPOINT}?limit=3`;
    const response = await fetch(url, { 
      cache: 'no-store', 
      mode: 'cors',
      headers: {
        'Origin': 'http://localhost:3001'
      }
    });
    
    console.log(`[Test] Response status: ${response.status}`);
    console.log(`[Test] Response headers:`, Object.fromEntries(response.headers));
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log(`[Test] Success! Got ${data.length} products`);
    console.log(`[Test] First product:`, data[0]);
    
  } catch (error) {
    console.error(`[Test] Fetch failed:`, error);
    console.log(`[Test] Error name: ${error.name}`);
    console.log(`[Test] Error message: ${error.message}`);
    
    // Test if this would fall back to static
    console.log(`[Test] Would use STATIC_PRODUCTS fallback: ${isLocal}`);
  }
}

testFetch();