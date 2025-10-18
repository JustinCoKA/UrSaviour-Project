/* products.js
 * - Loads products from /api/v1/products
 * - 4-col grid, open-by-default filters, collapsible sections
 * - Wide search, watchlist in localStorage
 */

// ===== Global Configuration =====
const isLocal = ["localhost", "127.0.0.1"].includes(window.location.hostname) || window.location.protocol === 'file:';

// API Base URL detection (Global scope)
let API_BASE;
if (isLocal) {
  // Local development: use explicit backend port
  API_BASE = "http://localhost:8000";
} else {
  // Production: use nginx proxy (empty string for relative paths)
  API_BASE = "";
  console.log('[DEBUG] Production mode - using nginx proxy with relative paths');
}

// API Endpoints (Global scope)
const PRODUCTS_ENDPOINT = `${API_BASE}/api/v1/products/`;

// ===== Global State Variables =====
let PRODUCTS = [];                  // populated by API
const PER_PAGE = 20;                // 4 × 5
let currentPage = 1;
let activeCategory = "all";
let activeOffer = "all";
let keyword = "";
let priceRange = null;
let isLoading = false;
let loadError = null;

// ===== Utility Functions =====
function $(id) { return document.getElementById(id); }

function escapeHTML(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function formatPrice(price) {
  const num = Number(price);
  return Number.isFinite(num) ? num.toFixed(2) : "0.00";
}

function formatTimestamp(ts) {
  if (!ts) return "";
  let d = new Date(ts);
  if (isNaN(d)) {
    const n = Number(ts);
    if (!isNaN(n)) d = new Date(n > 1e12 ? n : n * 1000);
  }
  return isNaN(d) ? "" : d.toLocaleString();
};

// ===== Data Loading =====
async function loadProducts() {
  try {
    isLoading = true; loadError = null; showLoading();
    
    // First check if backend is available (especially important for production)
    if (!isLocal) {
      console.log("[Products] Production environment - checking backend health...");
    }

    const url = PRODUCTS_ENDPOINT;
    console.log("[Products] Fetching from:", url);
    
    let res;
    try {
      res = await fetch(url, { 
        cache: 'no-store', 
        mode: 'cors',
        credentials: 'same-origin',
        headers: { 'Accept': 'application/json' }
      });
      console.log('[Products] Primary fetch result - status:', res ? res.status : 'null', 'ok:', res ? res.ok : 'n/a');
    } catch (fetchErr) {
      console.error('[Products] Primary fetch failed:', fetchErr.name, fetchErr.message);
      console.error('[Products] Fetch error object:', fetchErr);
      res = null;
    }

    // If primary failed and we are local, try 127.0.0.1 as some Docker/hosts setups prefer that
    if ((!res || !res.ok) && isLocal) {
      const altUrl = url.replace('localhost', '127.0.0.1');
      console.info('[Products] attempting fallback fetch to', altUrl);
      try {
        res = await fetch(altUrl, { cache: 'no-store', mode: 'cors' });
        if (res && res.ok) {
          console.info('[Products] fallback to 127.0.0.1 succeeded');
        } else {
          console.warn('[Products] fallback response status:', res ? res.status : 'null');
        }
      } catch (e) {
        console.warn('[Products] fallback fetch failed:', e.name, e.message);
        console.warn('[Products] Fallback error object:', e);
        res = null;
      }
    }

    if (!res) throw new Error('No response from API (network error)');
    console.log('API Response:', res.status, res.statusText);
    if (!res.ok) throw new Error(`HTTP ${res.status} ${res.statusText}`);

    let data;
    try {
      const responseData = await res.json();
      console.log('[Products] Raw API data received:', responseData);
      
      // Extract products array from API response
      if (responseData && responseData.products && Array.isArray(responseData.products)) {
        data = responseData.products;
        console.log('[Products] Extracted products array:', data.length, 'items');
      } else if (Array.isArray(responseData)) {
        // Fallback: if response is already an array
        data = responseData;
        console.log('[Products] Response is already array:', data.length, 'items');
      } else {
        throw new Error("API response missing 'products' array");
      }
      
      console.log('[Products] Data type:', typeof data, 'isArray:', Array.isArray(data), 'length:', data?.length);
      
      // Show API success in UI immediately
      showBanner(`🟢 API SUCCESS: Received ${data?.length || 0} products from backend`, 'success');
    
    console.log('[Products] Calling normalizeProducts with', data.length, 'items');
    PRODUCTS = normalizeProducts(data);
    console.log('[Products] After normalizeProducts - PRODUCTS length:', PRODUCTS.length);
    console.log('[Products] Normalized PRODUCTS sample:', PRODUCTS[0]);
    
    // Show normalization result
    showBanner(`🔧 NORMALIZED: ${PRODUCTS.length} valid products after processing`, 'info');
    
    isLoading = false;
    console.log('[Products] Calling render()');
    render();
    console.log('[Products] Render complete, showing success banner');
    // Clear any banner after successful load
    showBanner(`✅ LOADED: ${PRODUCTS.length} products from API displayed successfully`, 'success');
    
    } catch (jsonErr) {
      console.error('[Products] Failed to parse JSON or extract data:', jsonErr);
      throw new Error(`Failed to parse response: ${jsonErr.message}`);
    }
  } catch (err) {
    console.error("[Products] Failed to load products from API:", err);
    console.error("[Products] Error details - name:", err.name, "message:", err.message);
    console.log("[Products] Current isLocal value:", isLocal);
    console.log("[Products] Current hostname:", window.location.hostname);
    console.log("[Products] Current protocol:", window.location.protocol);
    
    // No fallback - just show error
    console.log("[Products] API failed - will show error message");
    
    isLoading = false;
    loadError = err.message;
    PRODUCTS = [];
    render();
    showBanner(`❌ ERROR: Cannot load products - ${err.message}`, 'error');
  }
}

function normalizeProducts(rawData) {
  console.log('[Normalize] Input data length:', rawData?.length || 0);
  console.log('[Normalize] First raw item:', rawData?.[0]);
  
  if (!Array.isArray(rawData)) {
    console.error('[Normalize] Input is not an array:', typeof rawData);
    return [];
  }

  const result = rawData.map((p, idx) => {
    console.log(`[Normalize] Processing product ${idx}:`, {
      id: p.id,
      name: p.name,
      category: p.category,
      image: p.image,
      description: p.description,
      special: p.special,
      stores_raw: p.stores
    });

    let processedStores = [];
    if (Array.isArray(p.stores)) {
      processedStores = p.stores.map(store => {
        const storeInfo = {
          brand: store.brand || "Unknown Store",
          price: Number(store.price) || 0
        };
        
        // Add original price if there's a discount
        if (store.original_price && Number(store.original_price) !== Number(store.price)) {
          storeInfo.original_price = Number(store.original_price);
        }
        
        return storeInfo;
      }).filter(store => store.price > 0);
    }
    
    console.log(`[Normalize] Product ${idx} processed stores:`, processedStores);
    
    const normalizedProduct = {
      id: p.id || cryptoRandomId(),
      name: String(p.name || "Unknown Product"),
      category: p.category || "Uncategorized",
      description: p.description || "",
      image: p.image || "",
      special: p.special || null,
      stores: processedStores
    };
    
    console.log(`[Normalize] Product ${idx} FINAL:`, {
      id: normalizedProduct.id,
      name: normalizedProduct.name,
      category: normalizedProduct.category,
      stores_count: normalizedProduct.stores.length,
      first_store: normalizedProduct.stores[0]
    });
    return normalizedProduct;
  });
  
  const filtered = result.filter(p => {
    const hasStores = p.stores.length > 0;
    if (!hasStores) console.warn('[Normalize] Filtering out product with no valid stores:', p.id, p.name);
    return hasStores;
  });
  
  console.log('[Normalize] Final result length:', filtered.length);
  return filtered;
}

function cryptoRandomId() {
  try {
    const r = crypto.getRandomValues(new Uint32Array(2));
    return `G_${r[0].toString(16)}${r[1].toString(16)}`;
  } catch { return `G_${Math.random().toString(16).slice(2)}`; }
}

// ===== Filters & Rendering =====
function getFiltered() {
  const priceMax = priceRange ? Number(priceRange.value) : Infinity;
  return PRODUCTS.filter(p => {
    const catOk = activeCategory === "all" || p.category === activeCategory;
    const offerOk = activeOffer === "all" || (p.special && p.special.type === activeOffer);
    const kw = (keyword || "").trim().toLowerCase();
    const kwOk = !kw || p.name.toLowerCase().includes(kw) || (p.category || "").toLowerCase().includes(kw);
    
    // Safe stores access
    const stores = Array.isArray(p.stores) ? p.stores : [];
    const prices = stores.map(s => Number(s.price)).filter(price => Number.isFinite(price));
    const minPrice = prices.length > 0 ? Math.min(...prices) : Infinity;
    const priceOk = minPrice <= priceMax;
    
    return catOk && offerOk && kwOk && priceOk;
  });
}

function render() {
  const gallery = $("product-gallery");
  if (!gallery) {
    console.error("[Render] Gallery element not found");
    return;
  }

  if (isLoading) {
    gallery.innerHTML = '<div class="loading">Loading products...</div>';
    return;
  }

  if (loadError) {
    gallery.innerHTML = `
      <div class="error-state">
        <h3>Failed to load products</h3>
        <p>${escapeHTML(loadError)}</p>
        <button onclick="loadProducts()">Retry</button>
      </div>
    `;
    return;
  }

  const filtered = getFiltered();
  const totalPages = Math.ceil(filtered.length / PER_PAGE);
  if (currentPage > totalPages && totalPages > 0) currentPage = totalPages;

  const start = (currentPage - 1) * PER_PAGE;
  const pageData = filtered.slice(start, start + PER_PAGE);

  if (pageData.length === 0) {
    gallery.innerHTML = '<div class="no-results">No products found matching your criteria.</div>';
  } else {
    gallery.innerHTML = pageData.map(cardHTML).join("");
  }

  renderPagination(totalPages, filtered.length);
}

function cardHTML(item) {
  const stores = Array.isArray(item.stores) ? item.stores : [];
  if (stores.length === 0) {
    return `<div class="card error">No pricing data available for ${escapeHTML(item.name)}</div>`;
  }

  console.log('[cardHTML] Rendering product:', item.name, 'with stores:', stores);

  const storePriceRows = stores.map(store => {
    const currentPrice = formatPrice(store.price);
    const originalPrice = store.original_price ? formatPrice(store.original_price) : null;
    
    const priceRowHTML = `
      <div class="price-line">
        <span class="brand">${escapeHTML(store.brand)}</span>
        <span class="price-info">
          ${originalPrice ? `<span class="original">$${originalPrice}</span>` : ''}
          <span class="current">$${currentPrice}</span>
        </span>
      </div>
    `;
    
    console.log('[cardHTML] Store price row:', store.brand, currentPrice, originalPrice, 'HTML:', priceRowHTML);
    return priceRowHTML;
  }).join('');

  // Special offer badge
  let specialBadge = '';
  if (item.special && item.special.type) {
    specialBadge = `<div class="badge special">${escapeHTML(item.special.type)}</div>`;
  }

  const finalHTML = `
    <div class="card">
      <div class="card-header">
        <img src="${escapeHTML(item.image)}" alt="${escapeHTML(item.name)}" loading="lazy" 
             onerror="this.src='/images/placeholder.jpg'">
        ${specialBadge}
      </div>
      <div class="card-body">
        <h3>${escapeHTML(item.name)}</h3>
        <p class="category" data-category="${escapeHTML(item.category)}">${escapeHTML(item.category)}</p>
        ${item.description ? `<p class="description">${escapeHTML(item.description)}</p>` : ''}
        <div class="store-prices">
          ${storePriceRows}
        </div>
        <button class="btn-watchlist" onclick="toggleWatchlist('${item.id}')">
          Add to Watchlist
        </button>
      </div>
    </div>
  `;
  
  console.log('[cardHTML] Final HTML for', item.name, ':', finalHTML);
  return finalHTML;
}

function renderPagination(totalPages, totalItems) {
  const pagination = $("pagination");
  if (!pagination || totalPages <= 1) {
    if (pagination) pagination.innerHTML = '';
    return;
  }

  let html = `<div class="pagination-info">Page ${currentPage} of ${totalPages} (${totalItems} items)</div>`;
  
  if (currentPage > 1) {
    html += `<button onclick="goToPage(${currentPage - 1})">Previous</button>`;
  }
  
  for (let i = Math.max(1, currentPage - 2); i <= Math.min(totalPages, currentPage + 2); i++) {
    const activeClass = i === currentPage ? 'active' : '';
    html += `<button class="${activeClass}" onclick="goToPage(${i})">${i}</button>`;
  }
  
  if (currentPage < totalPages) {
    html += `<button onclick="goToPage(${currentPage + 1})">Next</button>`;
  }
  
  pagination.innerHTML = html;
}

function goToPage(page) {
  currentPage = page;
  render();
}

// ===== UI Utilities =====
function showLoading() {
  const gallery = $("product-gallery");
  if (gallery) {
    gallery.innerHTML = '<div class="loading">Loading products...</div>';
  }
}

function showBanner(message, type = 'info') {
  console.log(`[Banner ${type.toUpperCase()}] ${message}`);
  
  // Remove existing banner
  const existing = document.querySelector('.banner');
  if (existing) existing.remove();
  
  // Create new banner
  const banner = document.createElement('div');
  banner.className = `banner ${type}`;
  banner.innerHTML = `
    <span>${escapeHTML(message)}</span>
    <button onclick="this.parentElement.remove()">×</button>
  `;
  
  // Insert at top of page
  document.body.insertBefore(banner, document.body.firstChild);
  
  // Auto-remove after delay
  setTimeout(() => banner.remove(), type === 'error' ? 10000 : 5000);
}

// ===== Watchlist Functions =====
function getWatchlist() {
  try {
    return JSON.parse(localStorage.getItem('watchlist') || '[]');
  } catch {
    return [];
  }
}

function saveWatchlist(list) {
  try {
    localStorage.setItem('watchlist', JSON.stringify(list));
  } catch (e) {
    console.error('Failed to save watchlist:', e);
  }
}

function toggleWatchlist(productId) {
  const watchlist = getWatchlist();
  const index = watchlist.indexOf(productId);
  
  if (index > -1) {
    watchlist.splice(index, 1);
    showBanner(`Removed from watchlist`, 'info');
  } else {
    watchlist.push(productId);
    showBanner(`Added to watchlist`, 'success');
  }
  
  saveWatchlist(watchlist);
}

// ===== Event Handlers =====
function setupEventHandlers() {
  // Search input
  const searchInput = $("searchInput");
  if (searchInput) {
    searchInput.addEventListener("input", e => {
      keyword = e.target.value;
      currentPage = 1;
      render();
    });
  }

  // Price range slider
  priceRange = $("priceRange");
  if (priceRange) {
    const currentPrice = $("currentPrice");
    priceRange.addEventListener("input", e => {
      if (currentPrice) currentPrice.textContent = e.target.value;
      currentPage = 1;
      render();
    });
  }

  // Category filters
  document.querySelectorAll(".valuesButton[data-filter]").forEach(btn => {
    btn.addEventListener("click", () => {
      activeCategory = btn.dataset.filter;
      currentPage = 1;
      render();
    });
  });

  // Special offer filters
  document.querySelectorAll(".valuesButton[data-offer]").forEach(btn => {
    btn.addEventListener("click", () => {
      activeOffer = btn.dataset.offer;
      currentPage = 1;
      render();
    });
  });
}

// ===== Initialization =====
document.addEventListener("DOMContentLoaded", () => {
  console.log("[Products] DOM loaded, initializing...");
  setupEventHandlers();
  loadProducts();
});