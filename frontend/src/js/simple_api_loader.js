// Simple API loader that works (copied from test page)
async function loadProductsSimple() {
  try {
    console.log("[SIMPLE] Starting to load products...");
    console.log("[SIMPLE] API_BASE:", API_BASE);
    console.log("[SIMPLE] PRODUCTS_ENDPOINT:", PRODUCTS_ENDPOINT);
    
    const response = await fetch(PRODUCTS_ENDPOINT, {
      method: 'GET',
      mode: 'cors',
      cache: 'no-store'
    });
    
    console.log("[SIMPLE] Response status:", response.status);
    console.log("[SIMPLE] Response ok:", response.ok);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log("[SIMPLE] Received data:", data);
    
    if (data.products && Array.isArray(data.products)) {
      PRODUCTS = data.products.map(product => ({
        id: product.id || Math.random(),
        name: product.name || 'Unknown Product',
        price: parseFloat(product.price) || 0,
        description: product.description || '',
        category: product.category || 'Uncategorized',
        image_url: product.image_url || '',
        special: product.special || null,
        in_stock: product.in_stock !== false
      }));
      
      console.log("[SIMPLE] Processed products:", PRODUCTS.length);
      showBanner(`✅ Successfully loaded ${PRODUCTS.length} products from API`, 'success');
      
      isLoading = false;
      render();
      return true;
    } else {
      throw new Error('Invalid data format received from API');
    }
    
  } catch (error) {
    console.error("[SIMPLE] Error:", error);
    showBanner(`❌ API Error: ${error.message}`, 'error');
    return false;
  }
}