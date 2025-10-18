/* products.js
 * - Loads up to 100 products from /api/v1/products
 * - Falls back to STATIC_PRODUCTS if API fails (optional)
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
let PRODUCTS = [];                  // populated by API or fallback
const PER_PAGE = 20;                // 4 × 5
let currentPage = 1;
let activeCategory = "all";
let activeOffer = "all";
let keyword = "";
let isLoading = true;
let loadError = null;

// Watchlist (persisted)
let WATCHLIST = JSON.parse(localStorage.getItem("watchlist") || "[]");

// ===== Global DOM References =====
let gallery, pager, priceRange, currentPrice, searchInput;

// ===== Global Functions =====
function getFiltered() {
  const priceMax = priceRange ? Number(priceRange.value) : Infinity;
  return PRODUCTS.filter(p => {
    const catOk = activeCategory === "all" || p.category === activeCategory;
    const offerOk = activeOffer === "all" || (p.special && p.special.type === activeOffer);
    const kw = (keyword || "").trim().toLowerCase();
    const kwOk = !kw || p.name.toLowerCase().includes(kw) || (p.category || "").toLowerCase().includes(kw);
    
    // Safe array access with fallback
    const stores = Array.isArray(p.stores) ? p.stores : [];
    const prices = stores.map(s => Number(s.price)).filter(price => Number.isFinite(price));
    const minPrice = prices.length > 0 ? Math.min(...prices) : Infinity;
    const priceOk = Number.isFinite(minPrice) ? minPrice <= priceMax : true;
    
    return catOk && offerOk && kwOk && priceOk;
  });
}

function render() {
  try {
    console.log('[Render] Starting render(), PRODUCTS.length:', PRODUCTS.length);
    const data = getFiltered();
    console.log('[Render] After getFiltered(), filtered data length:', data.length);
    if (gallery) {
      const start = (currentPage - 1) * PER_PAGE;
      const end = start + PER_PAGE;
      const pageData = data.slice(start, end);
      console.log('[Render] Rendering page', currentPage, 'items', start, 'to', end, '- showing', pageData.length, 'products');
      gallery.innerHTML = pageData.map(cardHTML).join("");
      console.log('[Render] Gallery updated with', pageData.length, 'product cards');
      window.scrollTo({ top: 0, behavior: "smooth" });
    } else {
      console.warn('[Render] Gallery element not found!');
    }
    renderPager(data.length);
    console.log('[Render] Render complete');
  } catch (error) {
    console.error('[Render] Error during rendering:', error);
    if (gallery) {
      gallery.innerHTML = '<div style="padding: 20px; text-align: center; color: #666;">Error displaying products. Please refresh the page.</div>';
    }
  }
}

function cardHTML(item) {
  const liked = WATCHLIST.includes(item.id);
  const heartIcon = liked ? "❤️" : "🤍";
  
  // Safe array access with fallback
  const stores = Array.isArray(item.stores) ? item.stores : [];
  const prices = stores.map(s => Number(s.price)).filter(p => Number.isFinite(p));
  const minPrice = prices.length > 0 ? Math.min(...prices) : 0;
  
  const specialHTML = item.special ? `
    <div class="special-badge" style="
      background: #e74c3c; color: white; padding: 2px 6px; 
      border-radius: 3px; font-size: 0.8em; margin-top: 4px; display: inline-block;">
      ${item.special.type}
    </div>` : "";
  
  return `
    <div class="product-card" data-id="${item.id}" style="
      border: 1px solid #ddd; border-radius: 8px; padding: 12px; 
      background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      transition: transform 0.2s;">
      <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
        <h3 style="margin: 0; font-size: 1.1em; color: #333;">${item.name}</h3>
        <button onclick="toggleLike(${item.id})" style="
          background: none; border: none; font-size: 1.2em; 
          cursor: pointer; padding: 4px;">${heartIcon}</button>
      </div>
      <p style="color: #666; font-size: 0.9em; margin: 0 0 8px 0;">${item.category}</p>
      <div style="font-weight: bold; color: #2c3e50; font-size: 1.1em;">
        $${minPrice.toFixed(2)}
      </div>
      ${specialHTML}
    </div>`;
}

function renderPager(total) {
  if (!pager) return;
  const totalPages = Math.ceil(total / PER_PAGE);
  if (totalPages <= 1) { pager.innerHTML = ""; return; }
  
  const makeBtn = (text, onClick, opts = {}) => {
    const btn = document.createElement("button");
    btn.textContent = text;
    btn.style.cssText = `margin:0 2px; padding:4px 8px; border:1px solid #ccc; 
      background:${opts.active ? "#007bff" : opts.disabled ? "#f8f9fa" : "white"}; 
      color:${opts.active ? "white" : opts.disabled ? "#6c757d" : "#007bff"}; 
      cursor:${opts.disabled ? "not-allowed" : "pointer"};`;
    if (!opts.disabled) btn.onclick = onClick;
    pager.appendChild(btn);
  };
  
  pager.innerHTML = "";
  makeBtn("«", () => { currentPage = 1; render(); }, { disabled: currentPage === 1 });
  makeBtn("‹", () => { currentPage = Math.max(1, currentPage - 1); render(); }, { disabled: currentPage === 1 });
  
  for (let p = Math.max(1, currentPage - 2); p <= Math.min(totalPages, currentPage + 2); p++) {
    makeBtn(String(p), () => { currentPage = p; render(); }, { active: p === currentPage });
  }
  
  makeBtn("›", () => { currentPage = Math.min(totalPages, currentPage + 1); render(); }, { disabled: currentPage === totalPages });
  makeBtn("»", () => { currentPage = totalPages; render(); }, { disabled: currentPage === totalPages });
}

document.addEventListener("DOMContentLoaded", () => {
  // ===== 0) Initialize DOM References =====

  // Debug logging
  console.log("[DEBUG] Page loaded - hostname:", window.location.hostname);
  console.log("[DEBUG] isLocal:", isLocal);
  console.log("[DEBUG] API_BASE:", API_BASE);
  console.log("[DEBUG] PRODUCTS_ENDPOINT:", PRODUCTS_ENDPOINT);

  // ===== 1) Initialize DOM References =====
  gallery = document.getElementById("product-gallery");
  pager = document.getElementById("pagination");
  priceRange = document.getElementById("priceRange");
  currentPrice = document.getElementById("currentPrice");
  searchInput = document.getElementById("searchInput");

  // ===== 2) Utils =====
  function showLoading() {
    if (!gallery) return;
    gallery.innerHTML = `
      <div class="loading-state" style="
        display:flex;justify-content:center;align-items:center;
        height:200px;font-size:1.2em;color:#666;grid-column:1 / -1;">
        <div>
          <div style="margin-bottom:10px;">Loading products...</div>
          <div style="font-size:.9em;">🔄</div>
        </div>
      </div>`;
  }

  function showBanner(message, level = "warn") {
    try {
      const root = document.querySelector('.product-page') || document.body;
      let el = document.getElementById('product-api-banner');
      if (!el) {
        el = document.createElement('div');
        el.id = 'product-api-banner';
        el.style.position = 'sticky';
        el.style.top = '0';
        el.style.zIndex = '9999';
        el.style.padding = '10px 16px';
        el.style.textAlign = 'center';
        el.style.fontWeight = '600';
        el.style.fontSize = '0.95rem';
        el.style.borderBottom = '1px solid rgba(0,0,0,0.05)';
        root.insertBefore(el, root.firstChild);
      }
      if (level === 'error') {
        el.style.background = '#ffecec';
        el.style.color = '#a94442';
      } else {
        el.style.background = '#fff8e1';
        el.style.color = '#6a5800';
      }
      el.textContent = message;
    } catch (e) { /* ignore banner errors */ }
  }

  function showError(message) {
    if (!gallery) return;
    gallery.innerHTML = `
      <div class="error-state" style="
        display:flex;flex-direction:column;justify-content:center;align-items:center;
        height:200px;color:#d32f2f;background:#ffebee;border:1px solid #ffcdd2;
        border-radius:8px;padding:20px;grid-column:1 / -1;">
        <div style="font-size:1.2em;margin-bottom:10px;">❌ Failed to load products</div>
        <div style="margin-bottom:15px;text-align:center;">${message}</div>
        <button type="button" onclick="window.location.reload()" style="
          background:#d32f2f;color:#fff;border:none;padding:8px 16px;border-radius:4px;cursor:pointer;">
          Retry
        </button>
      </div>`;
  }

  const safeImg = (src, seed) =>
    `<img src="${src || ""}" alt="" loading="lazy" 
    onerror="this.onerror=null;this.src='https://picsum.photos/seed/${encodeURIComponent(seed)}/300/200';"/>`;

  const formatDate = (ts) => {
    if (!ts) return "";
    let d = new Date(ts);
    if (isNaN(d)) {
      const n = Number(ts);
      if (!isNaN(n)) d = new Date(n > 1e12 ? n : n * 1000);
    }
    return isNaN(d) ? "" : d.toLocaleString();
  };

  // ===== 3) Data =====
  const STATIC_PRODUCTS = [
  {
    "id": "P0001",
    "name": "Mineral Water",
    "category": "Frozen",
    "description": "Standard pack of mineral water",
    "image": "/images/p/P0001.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 11.94 },
      { "brand": "Mio Mart", "price": 6.00, "original_price": 11.99 },
      { "brand": "Austin Fresh", "price": 11.73 },
      { "brand": "Aadarsh Deals", "price": 11.95 }
    ],
    "special": { "type": "Half Price", "store": "Mio Mart" }
  },
  {
    "id": "P0002",
    "name": "Lettuce",
    "category": "Fruit",
    "description": "Standard pack of lettuce",
    "image": "/images/p/P0002.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 12.87 },
      { "brand": "Mio Mart", "price": 12.86 },
      { "brand": "Austin Fresh", "price": 12.53 },
      { "brand": "Aadarsh Deals", "price": 12.80 }
    ]
  },
  {
    "id": "P0003",
    "name": "Custard",
    "category": "Meat",
    "description": "Standard pack of custard",
    "image": "/images/p/P0003.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 13.31 },
      { "brand": "Mio Mart", "price": 13.39 },
      { "brand": "Austin Fresh", "price": 13.06 },
      { "brand": "Aadarsh Deals", "price": 13.27 }
    ]
  },
  {
    "id": "P0004",
    "name": "Trash Bag",
    "category": "Fruit",
    "description": "Standard pack of trash bag",
    "image": "/images/p/P0004.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 1.21, "original_price": 1.73 },
      { "brand": "Mio Mart", "price": 2.11 },
      { "brand": "Austin Fresh", "price": 1.92 },
      { "brand": "Aadarsh Deals", "price": 1.68 }
    ],
    "special": { "type": "30% OFF", "store": "Justin Groceries" }
  },
  {
    "id": "P0005",
    "name": "Ice Cream",
    "category": "Snacks",
    "description": "Standard pack of ice cream",
    "image": "/images/p/P0005.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 14.17 },
      { "brand": "Mio Mart", "price": 14.42 },
      { "brand": "Austin Fresh", "price": 14.24 },
      { "brand": "Aadarsh Deals", "price": 14.23 }
    ]
  },
  {
    "id": "P0006",
    "name": "Frozen Broccoli",
    "category": "Snacks",
    "description": "Standard pack of frozen broccoli",
    "image": "/images/p/P0006.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 8.72 },
      { "brand": "Mio Mart", "price": 8.85 },
      { "brand": "Austin Fresh", "price": 8.58 },
      { "brand": "Aadarsh Deals", "price": 8.71 }
    ]
  },
  {
    "id": "P0007",
    "name": "Bleach",
    "category": "Health",
    "description": "Standard pack of bleach",
    "image": "/images/p/P0007.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 10.31 },
      { "brand": "Mio Mart", "price": 10.38 },
      { "brand": "Austin Fresh", "price": 10.21 },
      { "brand": "Aadarsh Deals", "price": 10.29 }
    ]
  },
  {
    "id": "P0008",
    "name": "Carrot",
    "category": "Snacks",
    "description": "Standard pack of carrot",
    "image": "/images/p/P0008.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 5.87 },
      { "brand": "Mio Mart", "price": 5.92 },
      { "brand": "Austin Fresh", "price": 5.81 },
      { "brand": "Aadarsh Deals", "price": 5.86 }
    ]
  },
  {
    "id": "P0009",
    "name": "Deodorant",
    "category": "Household",
    "description": "Standard pack of deodorant",
    "image": "/images/p/P0009.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 13.31 },
      { "brand": "Mio Mart", "price": 13.38 },
      { "brand": "Austin Fresh", "price": 13.16 },
      { "brand": "Aadarsh Deals", "price": 13.27 }
    ]
  },
  {
    "id": "P0010",
    "name": "Frozen Soup",
    "category": "Household",
    "description": "Standard pack of frozen soup",
    "image": "/images/p/P0010.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 14.75 },
      { "brand": "Mio Mart", "price": 14.84 },
      { "brand": "Austin Fresh", "price": 14.63 },
      { "brand": "Aadarsh Deals", "price": 14.72 }
    ]
  },
  {
    "id": "P0011",
    "name": "Noodles",
    "category": "Pantry",
    "description": "Standard pack of noodles",
    "image": "/images/p/P0011.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 14.65 },
      { "brand": "Mio Mart", "price": 14.77 },
      { "brand": "Austin Fresh", "price": 14.54 },
      { "brand": "Aadarsh Deals", "price": 14.63 }
    ]
  },
  {
    "id": "P0012",
    "name": "Toothpaste",
    "category": "Pantry",
    "description": "Standard pack of toothpaste",
    "image": "/images/p/P0012.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 6.62 },
      { "brand": "Mio Mart", "price": 6.64 },
      { "brand": "Austin Fresh", "price": 6.51 },
      { "brand": "Aadarsh Deals", "price": 6.60 }
    ]
  },
  {
    "id": "P0013",
    "name": "Soda",
    "category": "Fruit",
    "description": "Standard pack of soda",
    "image": "/images/p/P0013.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 9.79 },
      { "brand": "Mio Mart", "price": 9.92 },
      { "brand": "Austin Fresh", "price": 9.70 },
      { "brand": "Aadarsh Deals", "price": 9.84 }
    ]
  },
  {
    "id": "P0014",
    "name": "Tuna",
    "category": "Meat",
    "description": "Standard pack of tuna",
    "image": "/images/p/P0014.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 2.91 },
      { "brand": "Mio Mart", "price": 2.93 },
      { "brand": "Austin Fresh", "price": 2.87 },
      { "brand": "Aadarsh Deals", "price": 2.93 }
    ]
  },
  {
    "id": "P0015",
    "name": "Oats",
    "category": "Beverages",
    "description": "Standard pack of oats",
    "image": "/images/p/P0015.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 2.61 },
      { "brand": "Mio Mart", "price": 2.70 },
      { "brand": "Austin Fresh", "price": 2.56 },
      { "brand": "Aadarsh Deals", "price": 2.60 }
    ]
  },
  {
    "id": "P0016",
    "name": "Pork Ribs",
    "category": "Meat",
    "description": "Standard pack of pork ribs",
    "image": "/images/p/P0016.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 7.33 },
      { "brand": "Mio Mart", "price": 7.42 },
      { "brand": "Austin Fresh", "price": 7.18 },
      { "brand": "Aadarsh Deals", "price": 7.27 }
    ]
  },
  {
    "id": "P0017",
    "name": "Rice",
    "category": "Meat",
    "description": "Standard pack of rice",
    "image": "/images/p/P0017.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 13.76 },
      { "brand": "Mio Mart", "price": 13.74 },
      { "brand": "Austin Fresh", "price": 13.70 },
      { "brand": "Aadarsh Deals", "price": 13.75 }
    ]
  },
  {
    "id": "P0018",
    "name": "Onion",
    "category": "Beverages",
    "description": "Standard pack of onion",
    "image": "/images/p/P0018.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 4.91 },
      { "brand": "Mio Mart", "price": 4.99 },
      { "brand": "Austin Fresh", "price": 4.80 },
      { "brand": "Aadarsh Deals", "price": 4.87 }
    ]
  },
  {
    "id": "P0019",
    "name": "Soy Milk",
    "category": "Dairy",
    "description": "Standard pack of soy milk",
    "image": "/images/p/P0019.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 13.34 },
      { "brand": "Mio Mart", "price": 13.32 },
      { "brand": "Austin Fresh", "price": 13.14 },
      { "brand": "Aadarsh Deals", "price": 13.28 }
    ]
  },
  {
    "id": "P0020",
    "name": "Spinach",
    "category": "Pantry",
    "description": "Standard pack of spinach",
    "image": "/images/p/P0020.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 10.53 },
      { "brand": "Mio Mart", "price": 7.37 },
      { "brand": "Austin Fresh", "price": 7.46 },
      { "brand": "Aadarsh Deals", "price": 7.62 }
    ]
  },
  {
    "id": "P0021",
    "name": "Apple",
    "category": "Fruit",
    "description": "Standard pack of apple",
    "image": "/images/p/P0021.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 4.83 },
      { "brand": "Mio Mart", "price": 4.92 },
      { "brand": "Austin Fresh", "price": 4.70 },
      { "brand": "Aadarsh Deals", "price": 4.81 }
    ]
  },
  {
    "id": "P0022",
    "name": "Orange Juice",
    "category": "Beverages",
    "description": "Standard pack of orange juice",
    "image": "/images/p/P0022.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 6.70 },
      { "brand": "Mio Mart", "price": 6.77 },
      { "brand": "Austin Fresh", "original_price": 6.75, "price": 4.72 },
      { "brand": "Aadarsh Deals", "price": 6.71 }
    ],
    "special": { "type": "30% OFF", "store": "Austin Fresh" }
  },
  {
    "id": "P0023",
    "name": "Beef Steak",
    "category": "Meat",
    "description": "Standard pack of beef steak",
    "image": "/images/p/P0023.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 17.23 },
      { "brand": "Mio Mart", "price": 17.37 },
      { "brand": "Austin Fresh", "price": 17.05 },
      { "brand": "Aadarsh Deals", "price": 17.19 }
    ]
  },
  {
    "id": "P0024",
    "name": "Cucumber",
    "category": "Vegetables",
    "description": "Standard pack of cucumber",
    "image": "/images/p/P0024.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 3.27 },
      { "brand": "Mio Mart", "price": 3.32 },
      { "brand": "Austin Fresh", "price": 3.16 },
      { "brand": "Aadarsh Deals", "price": 3.22 }
    ]
  },
  {
    "id": "P0025",
    "name": "Tomato",
    "category": "Vegetables",
    "description": "Standard pack of tomato",
    "image": "/images/p/P0025.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 3.11 },
      { "brand": "Mio Mart", "original_price": 3.20, "price": 2.24 },
      { "brand": "Austin Fresh", "price": 3.08 },
      { "brand": "Aadarsh Deals", "price": 3.15 }
    ],
    "special": { "type": "30% OFF", "store": "Mio Mart" }
  },
  {
    "id": "P0026",
    "name": "Cereal",
    "category": "Pantry",
    "description": "Standard pack of cereal",
    "image": "/images/p/P0026.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 4.71 },
      { "brand": "Mio Mart", "price": 4.76 },
      { "brand": "Austin Fresh", "price": 4.60 },
      { "brand": "Aadarsh Deals", "price": 4.68 }
    ]
  },
  {
    "id": "P0027",
    "name": "Banana",
    "category": "Fruit",
    "description": "Standard pack of banana",
    "image": "/images/p/P0027.jpg",
    "stores": [
      { "brand": "Justin Groceries", "original_price": 2.20, "price": 1.10 },
      { "brand": "Mio Mart", "price": 2.18 },
      { "brand": "Austin Fresh", "price": 2.15 },
      { "brand": "Aadarsh Deals", "price": 2.17 }
    ],
    "special": { "type": "Half Price", "store": "Justin Groceries" }
  },
  {
    "id": "P0028",
    "name": "Pasta",
    "category": "Pantry",
    "description": "Standard pack of pasta",
    "image": "/images/p/P0028.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 6.32 },
      { "brand": "Mio Mart", "price": 6.39 },
      { "brand": "Austin Fresh", "price": 6.21 },
      { "brand": "Aadarsh Deals", "price": 6.29 }
    ]
  },
  {
    "id": "P0029",
    "name": "Chicken Breast",
    "category": "Meat",
    "description": "Standard pack of chicken breast",
    "image": "/images/p/P0029.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 9.13 },
      { "brand": "Mio Mart", "price": 9.21 },
      { "brand": "Austin Fresh", "price": 9.05 },
      { "brand": "Aadarsh Deals", "price": 9.10 }
    ]
  },
  {
    "id": "P0030",
    "name": "Bread",
    "category": "Bakery",
    "description": "Wholegrain bread 700g",
    "image": "/images/p/P0030.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 3.80 },
      { "brand": "Mio Mart", "original_price": 3.90, "price": 2.73 },
      { "brand": "Austin Fresh", "price": 3.79 },
      { "brand": "Aadarsh Deals", "price": 3.82 }
    ],
    "special": { "type": "30% OFF", "store": "Mio Mart" }
  },
  {
    "id": "P0031",
    "name": "Eggs 12 pack",
    "category": "Dairy",
    "description": "Dozen eggs pack",
    "image": "/images/p/P0031.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 4.30 },
      { "brand": "Mio Mart", "price": 4.35 },
      { "brand": "Austin Fresh", "price": 4.22 },
      { "brand": "Aadarsh Deals", "price": 4.28 }
    ]
  },
  {
    "id": "P0032",
    "name": "Butter",
    "category": "Dairy",
    "description": "Standard pack of butter",
    "image": "/images/p/P0032.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 2.90 },
      { "brand": "Mio Mart", "price": 2.96 },
      { "brand": "Austin Fresh", "price": 2.83 },
      { "brand": "Aadarsh Deals", "price": 2.89 }
    ]
  },
  {
    "id": "P0033",
    "name": "Flour",
    "category": "Pantry",
    "description": "Plain flour 1kg",
    "image": "/images/p/P0033.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 2.80 },
      { "brand": "Mio Mart", "price": 2.85 },
      { "brand": "Austin Fresh", "original_price": 2.83, "price": 1.98 },
      { "brand": "Aadarsh Deals", "price": 2.79 }
    ],
    "special": { "type": "30% OFF", "store": "Austin Fresh" }
  },
  {
    "id": "P0034",
    "name": "Salt",
    "category": "Pantry",
    "description": "Table salt 1kg",
    "image": "/images/p/P0034.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 1.70 },
      { "brand": "Mio Mart", "price": 1.72 },
      { "brand": "Austin Fresh", "original_price": 1.71, "price": 1.20 },
      { "brand": "Aadarsh Deals", "price": 1.69 }
    ],
    "special": { "type": "30% OFF", "store": "Austin Fresh" }
  },
  {
    "id": "P0035",
    "name": "Chicken Thigh",
    "category": "Meat",
    "description": "Standard pack of chicken thigh",
    "image": "/images/p/P0035.jpg",
    "stores": [
      { "brand": "Justin Groceries", "original_price": 8.40, "price": 5.88 },
      { "brand": "Mio Mart", "price": 8.35 },
      { "brand": "Austin Fresh", "price": 8.30 },
      { "brand": "Aadarsh Deals", "price": 8.33 }
    ],
    "special": { "type": "30% OFF", "store": "Justin Groceries" }
  },
  {
    "id": "P0036",
    "name": "Tissue",
    "category": "Household",
    "description": "Box of tissues",
    "image": "/images/p/P0036.jpg",
    "stores": [
      { "brand": "Justin Groceries", "original_price": 2.50, "price": 1.75 },
      { "brand": "Mio Mart", "price": 2.52 },
      { "brand": "Austin Fresh", "price": 2.48 },
      { "brand": "Aadarsh Deals", "price": 2.51 }
    ],
    "special": { "type": "30% OFF", "store": "Justin Groceries" }
  },
  {
    "id": "P0037",
    "name": "Iced Tea",
    "category": "Beverages",
    "description": "Bottle of iced tea",
    "image": "/images/p/P0037.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 4.10 },
      { "brand": "Mio Mart", "original_price": 4.12, "price": 2.06 },
      { "brand": "Austin Fresh", "price": 4.09 },
      { "brand": "Aadarsh Deals", "price": 4.11 }
    ],
    "special": { "type": "Half Price", "store": "Mio Mart" }
  },
  {
    "id": "P0038",
    "name": "Toilet Paper",
    "category": "Household",
    "description": "12 pack toilet rolls",
    "image": "/images/p/P0038.jpg",
    "stores": [
      { "brand": "Justin Groceries", "original_price": 7.00, "price": 4.90 },
      { "brand": "Mio Mart", "price": 6.95 },
      { "brand": "Austin Fresh", "price": 6.92 },
      { "brand": "Aadarsh Deals", "price": 6.97 }
    ],
    "special": { "type": "30% OFF", "store": "Justin Groceries" }
  },
  {
    "id": "P0039",
    "name": "Nuts Mix",
    "category": "Snacks",
    "description": "Pack of mixed nuts",
    "image": "/images/p/P0039.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 5.50 },
      { "brand": "Mio Mart", "price": 5.57 },
      { "brand": "Austin Fresh", "original_price": 5.55, "price": 3.88 },
      { "brand": "Aadarsh Deals", "price": 5.51 }
    ],
    "special": { "type": "30% OFF", "store": "Austin Fresh" }
  },
  {
    "id": "P0040",
    "name": "Cookies",
    "category": "Snacks",
    "description": "Box of cookies",
    "image": "/images/p/P0040.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 3.90 },
      { "brand": "Mio Mart", "original_price": 3.92, "price": 1.96 },
      { "brand": "Austin Fresh", "price": 3.88 },
      { "brand": "Aadarsh Deals", "price": 3.91 }
    ],
    "special": { "type": "Half Price", "store": "Mio Mart" }
  },
  {
    "id": "P0041",
    "name": "Chocolate Biscuit",
    "category": "Snacks",
    "description": "Box of chocolate biscuits",
    "image": "/images/p/P0041.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 4.80 },
      { "brand": "Mio Mart", "original_price": 4.85, "price": 2.42 },
      { "brand": "Austin Fresh", "price": 4.79 },
      { "brand": "Aadarsh Deals", "price": 4.83 }
    ],
    "special": { "type": "Half Price", "store": "Mio Mart" }
  },
  {
    "id": "P0042",
    "name": "Soy Sauce",
    "category": "Pantry",
    "description": "Bottle of soy sauce",
    "image": "/images/p/P0042.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 3.20 },
      { "brand": "Mio Mart", "price": 3.22 },
      { "brand": "Austin Fresh", "original_price": 3.25, "price": 1.63 },
      { "brand": "Aadarsh Deals", "price": 3.18 }
    ],
    "special": { "type": "Half Price", "store": "Austin Fresh" }
  },
  {
    "id": "P0043",
    "name": "Bagel",
    "category": "Bakery",
    "description": "Pack of bagels",
    "image": "/images/p/P0043.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 3.00 },
      { "brand": "Mio Mart", "original_price": 3.05, "price": 2.13 },
      { "brand": "Austin Fresh", "price": 3.02 },
      { "brand": "Aadarsh Deals", "price": 3.01 }
    ],
    "special": { "type": "30% OFF", "store": "Mio Mart" }
  },
  {
    "id": "P0044",
    "name": "Pita Bread",
    "category": "Bakery",
    "description": "Pack of pita bread",
    "image": "/images/p/P0044.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 2.50 },
      { "brand": "Mio Mart", "price": 2.52 },
      { "brand": "Austin Fresh", "original_price": 2.55, "price": 1.28 },
      { "brand": "Aadarsh Deals", "price": 2.48 }
    ],
    "special": { "type": "Half Price", "store": "Austin Fresh" }
  },
  {
    "id": "P0045",
    "name": "Vinegar",
    "category": "Pantry",
    "description": "Bottle of vinegar",
    "image": "/images/p/P0045.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 2.10 },
      { "brand": "Mio Mart", "original_price": 2.15, "price": 1.50 },
      { "brand": "Austin Fresh", "price": 2.09 },
      { "brand": "Aadarsh Deals", "price": 2.11 }
    ],
    "special": { "type": "30% OFF", "store": "Mio Mart" }
  },
  {
    "id": "P0046",
    "name": "Canned Corn",
    "category": "Pantry",
    "description": "Can of corn kernels",
    "image": "/images/p/P0046.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 1.90 },
      { "brand": "Mio Mart", "original_price": 1.95, "price": 0.98 },
      { "brand": "Austin Fresh", "price": 1.88 },
      { "brand": "Aadarsh Deals", "price": 1.92 }
    ],
    "special": { "type": "Half Price", "store": "Mio Mart" }
  },
  {
    "id": "P0047",
    "name": "Rice Cracker",
    "category": "Snacks",
    "description": "Pack of rice crackers",
    "image": "/images/p/P0047.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 2.40 },
      { "brand": "Mio Mart", "price": 2.45 },
      { "brand": "Austin Fresh", "original_price": 2.42, "price": 1.69 },
      { "brand": "Aadarsh Deals", "price": 2.41 }
    ],
    "special": { "type": "30% OFF", "store": "Austin Fresh" }
  },
  {
    "id": "P0048",
    "name": "Fruit Smoothie",
    "category": "Beverages",
    "description": "Bottle of fruit smoothie",
    "image": "/images/p/P0048.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 4.90 },
      { "brand": "Mio Mart", "original_price": 4.95, "price": 2.48 },
      { "brand": "Austin Fresh", "price": 4.92 },
      { "brand": "Aadarsh Deals", "price": 4.89 }
    ],
    "special": { "type": "Half Price", "store": "Mio Mart" }
  },
  {
    "id": "P0049",
    "name": "Donut",
    "category": "Bakery",
    "description": "Pack of donuts",
    "image": "/images/p/P0049.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 3.50 },
      { "brand": "Mio Mart", "original_price": 3.55, "price": 2.49 },
      { "brand": "Austin Fresh", "price": 3.51 },
      { "brand": "Aadarsh Deals", "price": 3.53 }
    ],
    "special": { "type": "30% OFF", "store": "Mio Mart" }
  },
  {
    "id": "P0050",
    "name": "Yogurt Drink",
    "category": "Dairy",
    "description": "Pack of yogurt drink",
    "image": "/images/p/P0050.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 4.20 },
      { "brand": "Mio Mart", "price": 4.25 },
      { "brand": "Austin Fresh", "original_price": 4.22, "price": 2.95 },
      { "brand": "Aadarsh Deals", "price": 4.21 }
    ],
    "special": { "type": "30% OFF", "store": "Austin Fresh" }
  },
  {
    "id": "P0051",
    "name": "Lamb Leg",
    "category": "Meat",
    "description": "Pack of lamb leg",
    "image": "/images/p/P0051.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 15.00 },
      { "brand": "Mio Mart", "original_price": 15.10, "price": 7.55 },
      { "brand": "Austin Fresh", "price": 14.98 },
      { "brand": "Aadarsh Deals", "price": 15.03 }
    ],
    "special": { "type": "Half Price", "store": "Mio Mart" }
  },
  {
    "id": "P0052",
    "name": "Croissant",
    "category": "Bakery",
    "description": "Pack of croissants",
    "image": "/images/p/P0052.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 5.20 },
      { "brand": "Mio Mart", "price": 5.25 },
      { "brand": "Austin Fresh", "original_price": 5.22, "price": 3.65 },
      { "brand": "Aadarsh Deals", "price": 5.19 }
    ],
    "special": { "type": "30% OFF", "store": "Austin Fresh" }
  },
  {
    "id": "P0053",
    "name": "Cheese Block",
    "category": "Dairy",
    "description": "Block of cheese",
    "image": "/images/p/P0053.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 6.80 },
      { "brand": "Mio Mart", "price": 6.85 },
      { "brand": "Austin Fresh", "price": 6.78 },
      { "brand": "Aadarsh Deals", "price": 6.79 }
    ]
  },
  {
    "id": "P0054",
    "name": "Rice Bag 5kg",
    "category": "Pantry",
    "description": "Bag of rice 5kg",
    "image": "/images/p/P0054.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 12.50 },
      { "brand": "Mio Mart", "price": 12.55 },
      { "brand": "Austin Fresh", "price": 12.48 },
      { "brand": "Aadarsh Deals", "price": 12.51 }
    ]
  },
  {
    "id": "P0055",
    "name": "Green Beans",
    "category": "Vegetables",
    "description": "Standard pack of green beans",
    "image": "/images/p/P0055.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 3.80 },
      { "brand": "Mio Mart", "price": 3.85 },
      { "brand": "Austin Fresh", "price": 3.78 },
      { "brand": "Aadarsh Deals", "price": 3.82 }
    ]
  },
  {
    "id": "P0056",
    "name": "Fish Fillet",
    "category": "Meat",
    "description": "Pack of fish fillet",
    "image": "/images/p/P0056.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 9.90 },
      { "brand": "Mio Mart", "price": 9.95 },
      { "brand": "Austin Fresh", "price": 9.87 },
      { "brand": "Aadarsh Deals", "price": 9.91 }
    ]
  },
  {
    "id": "P0057",
    "name": "Yogurt Tub",
    "category": "Dairy",
    "description": "Tub of yogurt",
    "image": "/images/p/P0057.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 3.70 },
      { "brand": "Mio Mart", "price": 3.75 },
      { "brand": "Austin Fresh", "price": 3.68 },
      { "brand": "Aadarsh Deals", "price": 3.71 }
    ]
  },
  {
    "id": "P0058",
    "name": "Frozen Pizza",
    "category": "Frozen",
    "description": "Pack of frozen pizza",
    "image": "/images/p/P0058.jpg",
    "stores": [
      { "brand": "Justin Groceries", "original_price": 6.00, "price": 4.20 },
      { "brand": "Mio Mart", "price": 5.95 },
      { "brand": "Austin Fresh", "price": 5.92 },
      { "brand": "Aadarsh Deals", "price": 5.97 }
    ],
    "special": { "type": "30% OFF", "store": "Justin Groceries" }
  },
  {
    "id": "P0059",
    "name": "Coffee",
    "category": "Beverages",
    "description": "Jar of coffee",
    "image": "/images/p/P0059.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 8.70 },
      { "brand": "Mio Mart", "price": 8.75 },
      { "brand": "Austin Fresh", "price": 8.68 },
      { "brand": "Aadarsh Deals", "price": 8.72 }
    ]
  },
  {
    "id": "P0060",
    "name": "Green Tea",
    "category": "Beverages",
    "description": "Box of green tea bags",
    "image": "/images/p/P0060.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 2.90 },
      { "brand": "Mio Mart", "price": 2.92 },
      { "brand": "Austin Fresh", "price": 2.88 },
      { "brand": "Aadarsh Deals", "price": 2.91 }
    ]
  },
    {
    "id": "P0061",
    "name": "Strawberry Jam",
    "category": "Pantry",
    "description": "Jar of strawberry jam",
    "image": "/images/p/P0061.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 3.40 },
      { "brand": "Mio Mart", "price": 3.45 },
      { "brand": "Austin Fresh", "price": 3.37 },
      { "brand": "Aadarsh Deals", "price": 3.39 }
    ]
  },
  {
    "id": "P0062",
    "name": "Peanut Butter",
    "category": "Pantry",
    "description": "Jar of peanut butter",
    "image": "/images/p/P0062.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 4.80 },
      { "brand": "Mio Mart", "price": 4.85 },
      { "brand": "Austin Fresh", "price": 4.78 },
      { "brand": "Aadarsh Deals", "price": 4.81 }
    ]
  },
  {
    "id": "P0063",
    "name": "Jam Donut",
    "category": "Bakery",
    "description": "Pack of jam donuts",
    "image": "/images/p/P0063.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 3.20 },
      { "brand": "Mio Mart", "price": 3.25 },
      { "brand": "Austin Fresh", "price": 3.18 },
      { "brand": "Aadarsh Deals", "price": 3.22 }
    ]
  },
  {
    "id": "P0064",
    "name": "Granola",
    "category": "Pantry",
    "description": "Pack of granola cereal",
    "image": "/images/p/P0064.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 5.10 },
      { "brand": "Mio Mart", "price": 5.15 },
      { "brand": "Austin Fresh", "price": 5.07 },
      { "brand": "Aadarsh Deals", "price": 5.12 }
    ]
  },
  {
    "id": "P0065",
    "name": "Tomato Sauce",
    "category": "Pantry",
    "description": "Bottle of tomato sauce",
    "image": "/images/p/P0065.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 2.50 },
      { "brand": "Mio Mart", "price": 2.55 },
      { "brand": "Austin Fresh", "price": 2.47 },
      { "brand": "Aadarsh Deals", "price": 2.51 }
    ]
  },
  {
    "id": "P0066",
    "name": "Olive Oil",
    "category": "Pantry",
    "description": "Bottle of olive oil",
    "image": "/images/p/P0066.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 7.90 },
      { "brand": "Mio Mart", "price": 7.95 },
      { "brand": "Austin Fresh", "price": 7.87 },
      { "brand": "Aadarsh Deals", "price": 7.91 }
    ]
  },
  {
    "id": "P0067",
    "name": "Honey",
    "category": "Pantry",
    "description": "Jar of honey",
    "image": "/images/p/P0067.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 6.40 },
      { "brand": "Mio Mart", "price": 6.45 },
      { "brand": "Austin Fresh", "price": 6.38 },
      { "brand": "Aadarsh Deals", "price": 6.42 }
    ]
  },
  {
    "id": "P0068",
    "name": "Mustard",
    "category": "Pantry",
    "description": "Jar of mustard",
    "image": "/images/p/P0068.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 2.80 },
      { "brand": "Mio Mart", "price": 2.85 },
      { "brand": "Austin Fresh", "price": 2.77 },
      { "brand": "Aadarsh Deals", "price": 2.82 }
    ]
  },
  {
    "id": "P0069",
    "name": "Mayonnaise",
    "category": "Pantry",
    "description": "Jar of mayonnaise",
    "image": "/images/p/P0069.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 3.30 },
      { "brand": "Mio Mart", "price": 3.35 },
      { "brand": "Austin Fresh", "price": 3.27 },
      { "brand": "Aadarsh Deals", "price": 3.31 }
    ]
  },
  {
    "id": "P0070",
    "name": "Ketchup",
    "category": "Pantry",
    "description": "Bottle of ketchup",
    "image": "/images/p/P0070.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 2.70 },
      { "brand": "Mio Mart", "price": 2.75 },
      { "brand": "Austin Fresh", "price": 2.67 },
      { "brand": "Aadarsh Deals", "price": 2.71 }
    ]
  },
  {
    "id": "P0071",
    "name": "Spaghetti",
    "category": "Pantry",
    "description": "Pack of spaghetti",
    "image": "/images/p/P0071.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 1.90 },
      { "brand": "Mio Mart", "price": 1.95 },
      { "brand": "Austin Fresh", "price": 1.87 },
      { "brand": "Aadarsh Deals", "price": 1.91 }
    ]
  },
  {
    "id": "P0072",
    "name": "Sugar",
    "category": "Pantry",
    "description": "Pack of white sugar",
    "image": "/images/p/P0072.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 2.60 },
      { "brand": "Mio Mart", "price": 2.65 },
      { "brand": "Austin Fresh", "price": 2.58 },
      { "brand": "Aadarsh Deals", "price": 2.62 }
    ]
  },
  {
    "id": "P0073",
    "name": "Brown Sugar",
    "category": "Pantry",
    "description": "Pack of brown sugar",
    "image": "/images/p/P0073.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 2.70 },
      { "brand": "Mio Mart", "price": 2.75 },
      { "brand": "Austin Fresh", "price": 2.67 },
      { "brand": "Aadarsh Deals", "price": 2.71 }
    ]
  },
  {
    "id": "P0074",
    "name": "Rice Vinegar",
    "category": "Pantry",
    "description": "Bottle of rice vinegar",
    "image": "/images/p/P0074.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 2.90 },
      { "brand": "Mio Mart", "price": 2.95 },
      { "brand": "Austin Fresh", "price": 2.88 },
      { "brand": "Aadarsh Deals", "price": 2.92 }
    ]
  },
  {
    "id": "P0075",
    "name": "Brown Rice",
    "category": "Pantry",
    "description": "Pack of brown rice",
    "image": "/images/p/P0075.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 6.10 },
      { "brand": "Mio Mart", "price": 6.15 },
      { "brand": "Austin Fresh", "price": 6.07 },
      { "brand": "Aadarsh Deals", "price": 6.12 }
    ]
  },
  {
    "id": "P0076",
    "name": "Whole Wheat Bread",
    "category": "Bakery",
    "description": "Whole wheat bread loaf",
    "image": "/images/p/P0076.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 2.80 },
      { "brand": "Mio Mart", "price": 2.85 },
      { "brand": "Austin Fresh", "price": 2.77 },
      { "brand": "Aadarsh Deals", "price": 2.81 }
    ]
  },
  {
    "id": "P0077",
    "name": "Baguette",
    "category": "Bakery",
    "description": "French baguette bread",
    "image": "/images/p/P0077.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 2.50 },
      { "brand": "Mio Mart", "price": 2.55 },
      { "brand": "Austin Fresh", "price": 2.47 },
      { "brand": "Aadarsh Deals", "price": 2.52 }
    ]
  },
  {
    "id": "P0078",
    "name": "Milk 2L",
    "category": "Dairy",
    "description": "Bottle of fresh milk 2L",
    "image": "/images/p/P0078.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 3.10 },
      { "brand": "Mio Mart", "price": 3.15 },
      { "brand": "Austin Fresh", "price": 3.07 },
      { "brand": "Aadarsh Deals", "price": 3.11 }
    ]
  },
  {
    "id": "P0079",
    "name": "Almond Milk",
    "category": "Dairy",
    "description": "Bottle of almond milk",
    "image": "/images/p/P0079.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 4.00 },
      { "brand": "Mio Mart", "price": 4.05 },
      { "brand": "Austin Fresh", "price": 3.97 },
      { "brand": "Aadarsh Deals", "price": 4.02 }
    ]
  },
  {
    "id": "P0080",
    "name": "Greek Yogurt",
    "category": "Dairy",
    "description": "Tub of Greek yogurt",
    "image": "/images/p/P0080.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 5.30 },
      { "brand": "Mio Mart", "price": 5.35 },
      { "brand": "Austin Fresh", "price": 5.27 },
      { "brand": "Aadarsh Deals", "price": 5.31 }
    ]
  },
    {
    "id": "P0081",
    "name": "Cheddar Cheese",
    "category": "Dairy",
    "description": "Block of cheddar cheese",
    "image": "/images/p/P0081.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 6.10 },
      { "brand": "Mio Mart", "price": 6.15 },
      { "brand": "Austin Fresh", "price": 6.07 },
      { "brand": "Aadarsh Deals", "price": 6.12 }
    ]
  },
  {
    "id": "P0082",
    "name": "Mozzarella Cheese",
    "category": "Dairy",
    "description": "Pack of mozzarella cheese",
    "image": "/images/p/P0082.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 5.40 },
      { "brand": "Mio Mart", "price": 5.45 },
      { "brand": "Austin Fresh", "price": 5.37 },
      { "brand": "Aadarsh Deals", "price": 5.41 }
    ]
  },
  {
    "id": "P0083",
    "name": "Butter Spread",
    "category": "Dairy",
    "description": "Tub of butter spread",
    "image": "/images/p/P0083.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 4.80 },
      { "brand": "Mio Mart", "price": 4.85 },
      { "brand": "Austin Fresh", "price": 4.77 },
      { "brand": "Aadarsh Deals", "price": 4.82 }
    ]
  },
  {
    "id": "P0084",
    "name": "Cream",
    "category": "Dairy",
    "description": "Carton of cream",
    "image": "/images/p/P0084.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 3.50 },
      { "brand": "Mio Mart", "price": 3.55 },
      { "brand": "Austin Fresh", "price": 3.47 },
      { "brand": "Aadarsh Deals", "price": 3.52 }
    ]
  },
  {
    "id": "P0085",
    "name": "Ice Cream Tub",
    "category": "Snacks",
    "description": "2L tub of ice cream",
    "image": "/images/p/P0085.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 6.70 },
      { "brand": "Mio Mart", "price": 6.75 },
      { "brand": "Austin Fresh", "original_price": 6.74, "price": 3.37 },
      { "brand": "Aadarsh Deals", "price": 6.72 }
    ],
    "special": { "type": "Half Price", "store": "Austin Fresh" }
  },
  {
    "id": "P0086",
    "name": "Frozen Peas",
    "category": "Frozen",
    "description": "Pack of frozen peas",
    "image": "/images/p/P0086.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 2.60 },
      { "brand": "Mio Mart", "price": 2.65 },
      { "brand": "Austin Fresh", "price": 2.58 },
      { "brand": "Aadarsh Deals", "price": 2.62 }
    ]
  },
  {
    "id": "P0087",
    "name": "Frozen Chips",
    "category": "Frozen",
    "description": "Pack of frozen potato chips",
    "image": "/images/p/P0087.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 3.40 },
      { "brand": "Mio Mart", "price": 3.45 },
      { "brand": "Austin Fresh", "original_price": 3.43, "price": 2.40 },
      { "brand": "Aadarsh Deals", "price": 3.41 }
    ],
    "special": { "type": "30% OFF", "store": "Austin Fresh" }
  },
  {
    "id": "P0088",
    "name": "Frozen Mixed Veg",
    "category": "Frozen",
    "description": "Pack of frozen mixed vegetables",
    "image": "/images/p/P0088.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 3.10 },
      { "brand": "Mio Mart", "price": 3.15 },
      { "brand": "Austin Fresh", "price": 3.07 },
      { "brand": "Aadarsh Deals", "price": 3.12 }
    ]
  },
  {
    "id": "P0089",
    "name": "Frozen Dumplings",
    "category": "Frozen",
    "description": "Pack of frozen dumplings",
    "image": "/images/p/P0089.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 5.60 },
      { "brand": "Mio Mart", "original_price": 5.65, "price": 2.82 },
      { "brand": "Austin Fresh", "price": 5.58 },
      { "brand": "Aadarsh Deals", "price": 5.61 }
    ],
    "special": { "type": "Half Price", "store": "Mio Mart" }
  },
  {
    "id": "P0090",
    "name": "Frozen Fish Fingers",
    "category": "Frozen",
    "description": "Pack of frozen fish fingers",
    "image": "/images/p/P0090.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 4.80 },
      { "brand": "Mio Mart", "price": 4.85 },
      { "brand": "Austin Fresh", "price": 4.77 },
      { "brand": "Aadarsh Deals", "price": 4.82 }
    ]
  },
  {
    "id": "P0091",
    "name": "Frozen Sausages",
    "category": "Frozen",
    "description": "Pack of frozen sausages",
    "image": "/images/p/P0091.jpg",
    "stores": [
      { "brand": "Justin Groceries", "original_price": 6.50, "price": 4.55 },
      { "brand": "Mio Mart", "price": 6.48 },
      { "brand": "Austin Fresh", "price": 6.46 },
      { "brand": "Aadarsh Deals", "price": 6.49 }
    ],
    "special": { "type": "30% OFF", "store": "Justin Groceries" }
  },
  {
    "id": "P0092",
    "name": "Frozen Nuggets",
    "category": "Frozen",
    "description": "Pack of frozen chicken nuggets",
    "image": "/images/p/P0092.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 4.10 },
      { "brand": "Mio Mart", "price": 4.15 },
      { "brand": "Austin Fresh", "price": 4.07 },
      { "brand": "Aadarsh Deals", "price": 4.11 }
    ]
  },
  {
    "id": "P0093",
    "name": "Frozen Spring Rolls",
    "category": "Frozen",
    "description": "Pack of frozen spring rolls",
    "image": "/images/p/P0093.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 3.80 },
      { "brand": "Mio Mart", "price": 3.85 },
      { "brand": "Austin Fresh", "original_price": 3.83, "price": 2.68 },
      { "brand": "Aadarsh Deals", "price": 3.81 }
    ],
    "special": { "type": "30% OFF", "store": "Austin Fresh" }
  },
  {
    "id": "P0094",
    "name": "Frozen Waffles",
    "category": "Frozen",
    "description": "Pack of frozen waffles",
    "image": "/images/p/P0094.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 4.00 },
      { "brand": "Mio Mart", "original_price": 4.05, "price": 2.03 },
      { "brand": "Austin Fresh", "price": 3.98 },
      { "brand": "Aadarsh Deals", "price": 4.02 }
    ],
    "special": { "type": "Half Price", "store": "Mio Mart" }
  },
  {
    "id": "P0095",
    "name": "Frozen Ice Blocks",
    "category": "Frozen",
    "description": "Pack of frozen ice blocks",
    "image": "/images/p/P0095.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 3.30 },
      { "brand": "Mio Mart", "price": 3.35 },
      { "brand": "Austin Fresh", "price": 3.27 },
      { "brand": "Aadarsh Deals", "price": 3.31 }
    ]
  },
  {
    "id": "P0096",
    "name": "Frozen Pancakes",
    "category": "Frozen",
    "description": "Pack of frozen pancakes",
    "image": "/images/p/P0096.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 3.50 },
      { "brand": "Mio Mart", "price": 3.55 },
      { "brand": "Austin Fresh", "price": 3.47 },
      { "brand": "Aadarsh Deals", "price": 3.52 }
    ]
  },
  {
    "id": "P0097",
    "name": "Frozen Cake",
    "category": "Frozen",
    "description": "Pack of frozen cake slices",
    "image": "/images/p/P0097.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 5.20 },
      { "brand": "Mio Mart", "price": 5.25 },
      { "brand": "Austin Fresh", "price": 5.18 },
      { "brand": "Aadarsh Deals", "price": 5.21 }
    ]
  },
  {
    "id": "P0098",
    "name": "Frozen Pie",
    "category": "Frozen",
    "description": "Pack of frozen pies",
    "image": "/images/p/P0098.jpg",
    "stores": [
      { "brand": "Justin Groceries", "original_price": 4.50, "price": 2.25 },
      { "brand": "Mio Mart", "price": 4.52 },
      { "brand": "Austin Fresh", "price": 4.48 },
      { "brand": "Aadarsh Deals", "price": 4.49 }
    ],
    "special": { "type": "Half Price", "store": "Justin Groceries" }
  },
  {
    "id": "P0099",
    "name": "Frozen Bread Rolls",
    "category": "Frozen",
    "description": "Pack of frozen bread rolls",
    "image": "/images/p/P0099.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 3.10 },
      { "brand": "Mio Mart", "price": 3.15 },
      { "brand": "Austin Fresh", "price": 3.07 },
      { "brand": "Aadarsh Deals", "price": 3.12 }
    ]
  },
  {
    "id": "P0100",
    "name": "Frozen Fruit Mix",
    "category": "Frozen",
    "description": "Pack of frozen fruit mix",
    "image": "/images/p/P0100.jpg",
    "stores": [
      { "brand": "Justin Groceries", "price": 5.80 },
      { "brand": "Mio Mart", "original_price": 5.85, "price": 2.92 },
      { "brand": "Austin Fresh", "price": 5.78 },
      { "brand": "Aadarsh Deals", "price": 5.82 }
    ],
    "special": { "type": "Half Price", "store": "Mio Mart" }
  }


  ]; // End of static fallback data (not used anymore)

  async function loadProducts() {
    try {
      isLoading = true; loadError = null; showLoading();
      
      // First check if backend is available (especially important for production)
      if (!isLocal) {
        console.log("[Products] Production environment - checking backend health...");
        try {
          const healthUrl = `${API_BASE}/api/v1/products/?limit=1`;
          console.log("[Products] Health check:", healthUrl);
          const healthRes = await fetch(healthUrl, { cache: 'no-store', mode: 'cors' });
          if (!healthRes.ok) {
            throw new Error(`Backend health check failed: HTTP ${healthRes.status}`);
          }
          console.log("[Products] Backend health check passed");
        } catch (healthError) {
          console.error("[Products] Backend health check failed:", healthError);
          showBanner(`🚨 Backend unavailable: ${healthError.message}. Check if Docker containers are running.`, 'error');
          throw new Error(`Backend service unavailable: ${healthError.message}`);
        }
      }
      
      const url = `${PRODUCTS_ENDPOINT}?limit=100`;
      console.log("[Products] GET:", url, "isLocal=", isLocal);
      showBanner(`Loading products from ${url} ...`, 'info');

      // Try simple loader first (if available)
      if (typeof loadProductsSimple === 'function') {
        console.log("[Products] Trying simple loader first...");
        const simpleSuccess = await loadProductsSimple();
        if (simpleSuccess) {
          console.log("[Products] Simple loader succeeded!");
          return;
        }
        console.log("[Products] Simple loader failed, trying complex loader...");
      }

      // Try primary fetch with detailed logging
      let res;
      try {
        console.log('[Products] Attempting primary fetch');
        console.log('[Products] URL:', url);
        console.log('[Products] API_BASE:', API_BASE);
        console.log('[Products] Current origin:', window.location.origin);
        console.log('[Products] Environment:', isLocal ? 'local' : 'production');
        
        res = await fetch(url, { cache: 'no-store', mode: 'cors' });
        console.log('[Products] Primary fetch response status:', res.status, res.statusText);
        console.log('[Products] Response headers:', [...res.headers.entries()]);
        console.log('[Products] Primary fetch response:', {
          ok: res.ok,
          status: res.status,
          statusText: res.statusText,
          headers: res.headers
        });
      } catch (e) {
        console.error('[Products] primary fetch failed:', e.name, e.message);
        console.error('[Products] Full error object:', e);
        console.error('[Products] Stack trace:', e.stack);
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
      
      } catch (processingError) {
        console.error('[Products] Error during data processing:', processingError);
        showBanner(`🚨 PROCESSING ERROR: ${processingError.message}`, 'error');
        throw processingError; // Re-throw to trigger main catch block
      }
    } catch (err) {
      console.error("[Products] Failed to load products from API:", err);
      console.error("[Products] Error details - name:", err.name, "message:", err.message);
      console.log("[Products] Current isLocal value:", isLocal);
      console.log("[Products] Current hostname:", window.location.hostname);
      console.log("[Products] Current protocol:", window.location.protocol);
      
      // Disable static fallback since API is working
      console.log("[Products] API failed but not using static fallback - will show error instead");
      if (false) { // Disabled fallback logic
        const fallback = window.STATIC_PRODUCTS || (typeof STATIC_PRODUCTS !== "undefined" ? STATIC_PRODUCTS : []);
        console.log("[Products] Checking fallback - available:", Array.isArray(fallback), "length:", fallback?.length || 0);
        if (Array.isArray(fallback) && fallback.length) {
          console.warn("[Products] Using STATIC_PRODUCTS fallback (local dev) - " + fallback.length + " products");
          showBanner(`API unreachable — using local static products (check backend at ${API_BASE})`, 'error');
          PRODUCTS = normalizeProducts(fallback);
          isLoading = false;
          render();
          return;
        } else {
          console.error("[Products] No static fallback available or fallback is empty");
        }
      } else {
        console.log("[Products] Not local environment, no fallback allowed");
      }

      // In production or when no fallback exists, show an error with a helpful hint
      isLoading = false;
      loadError = err.message || "Unknown error";
      const hint = 'If backend runs in Docker, ensure port 8000 is reachable from this browser and CORS allows this origin.';
      console.info(hint);
      
      // Safe banner call
      try {
        if (typeof showBanner === 'function') {
          showBanner(`Products API error: ${loadError} — ${hint}`,'error');
        } else {
          console.error('showBanner function not available');
        }
      } catch (bannerError) {
        console.error('Error calling showBanner:', bannerError);
      }
      
      try {
        if (typeof showError === 'function') {
          showError(loadError);
        } else {
          console.error('showError function not available');
        }
      } catch (errorFuncError) {
        console.error('Error calling showError:', errorFuncError);
      }
    }
  }

  function normalizeProducts(list) {
    console.log('[Normalize] Input list length:', list?.length);
    // Ensure minimal shape consistency
    const result = list.map((p, idx) => {
      console.log(`[Normalize] Processing product ${idx}:`, p.id, p.name);
      
      // Handle API data structure - convert single price/store to stores array
      let processedStores = [];
      
      if (Array.isArray(p.stores)) {
        // Handle existing stores array format
        processedStores = p.stores.map((s, storeIdx) => {
          console.log(`[Normalize] Processing store ${storeIdx}:`, s.brand, 'price:', s.price, 'type:', typeof s.price);
          return {
            brand: s.brand || "Unknown",
            price: Number(s.price ?? NaN),
            original_price: typeof s.original_price === "number" ? s.original_price : undefined,
            jobNumber: s.jobNumber,
            jobId: s.jobId,
            lastUpdatedAt: s.lastUpdatedAt || s.last_updated_at || s.updatedAt || s.updated_at || null
          };
        }).filter(s => {
          const isValid = Number.isFinite(s.price);
          if (!isValid) console.warn('[Normalize] Filtering out store with invalid price:', s);
          return isValid;
        });
      } else {
        // Handle API format - convert single price/special to stores array
        const price = Number(p.price);
        const storeName = p.special?.store || "Store";
        
        if (Number.isFinite(price)) {
          processedStores = [{
            brand: storeName,
            price: price,
            original_price: undefined,
            jobNumber: null,
            jobId: null,
            lastUpdatedAt: null
          }];
          console.log(`[Normalize] Created single store entry:`, storeName, 'price:', price);
        } else {
          console.warn('[Normalize] Product has invalid price:', p.price);
        }
      }
      
      const normalizedProduct = {
        id: p.id || cryptoRandomId(),
        name: String(p.name || "Unnamed"),
        category: p.category || "Other",
        description: p.description || "",
        image: p.image || "",
        special: p.special || null,
        stores: processedStores
      };
      
      console.log(`[Normalize] Product ${idx} final stores count:`, normalizedProduct.stores.length);
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

  // ===== 4) Filters & Rendering =====
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
      const priceOk = Number.isFinite(minPrice) ? minPrice <= priceMax : true;
      return catOk && offerOk && kwOk && priceOk;
    });
  }

  function cardHTML(item) {
    const badge = item.special ? `<span class="badge" data-type="${item.special.type}">${item.special.type}</span>` : "";
    const liked = WATCHLIST.includes(item.id);
    const likeBtn = `<button class="like-btn ${liked ? "active" : ""}" aria-label="Add to watchlist"
                      onclick="toggleLike('${item.id}')">❤</button>`;

    const stores = Array.isArray(item.stores) ? item.stores : [];
    const rows = stores.map(s => {
      const hasOriginal = typeof s.original_price === "number" && s.original_price > s.price;
      const originalHtml = hasOriginal ? `<span class="original-price">$${s.original_price.toFixed(2)}</span>` : "";
      const currentHtml = `<span class="current-price">$${Number(s.price).toFixed(2)}</span>`;

      const jobLabel = s.jobNumber ? `Job #${s.jobNumber}` : (s.jobId ? `Job ${s.jobId}` : "");
      const lastStr = s.lastUpdatedAt ? `<small class="meta">Updated: ${formatDate(s.lastUpdatedAt)}</small>` : "";
      const jobStr = jobLabel ? `<small class="meta">${jobLabel}</small>` : "";
      const meta = (jobStr || lastStr) ? `<div class="meta-row">${jobStr} ${lastStr}</div>` : "";

      return `
        <div class="price-row">
          <div class="left"><span class="brand">${s.brand}</span>${originalHtml}</div>
          ${currentHtml}
        </div>
        ${meta}
      `;
    }).join("");

    const desc = item.description ? `<div class="desc">${item.description}</div>` : "";

    return `
      <article class="card">
        <div class="media">
          ${badge}
          ${safeImg(item.image, item.id)}
          ${likeBtn}
        </div>
        <h3>${item.name}</h3>
        ${desc}
        <div class="price-list">${rows}</div>
      </article>`;
  }

  function renderPager(total) {
    if (!pager) return;
    pager.innerHTML = "";
    const totalPages = Math.max(1, Math.ceil(total / PER_PAGE));

    const makeBtn = (label, on, { disabled=false, active=false } = {}) => {
      const b = document.createElement("button");
      b.type = "button";
      b.textContent = label;
      if (disabled) b.disabled = true;
      if (active) b.classList.add("active");
      b.addEventListener("click", on);
      pager.appendChild(b);
    };

    makeBtn("«", () => { currentPage = 1; render(); }, { disabled: currentPage === 1 });
    makeBtn("‹", () => { currentPage = Math.max(1, currentPage - 1); render(); }, { disabled: currentPage === 1 });

    for (let p = 1; p <= totalPages; p++) {
      makeBtn(String(p), () => { currentPage = p; render(); }, { active: p === currentPage });
    }

    makeBtn("›", () => { currentPage = Math.min(totalPages, currentPage + 1); render(); }, { disabled: currentPage === totalPages });
    makeBtn("»", () => { currentPage = totalPages; render(); }, { disabled: currentPage === totalPages });
  }

  function render() {
    console.log('[Render] Starting render(), PRODUCTS.length:', PRODUCTS.length);
    const data = getFiltered();
    console.log('[Render] After getFiltered(), filtered data length:', data.length);
    if (gallery) {
      const start = (currentPage - 1) * PER_PAGE;
      const end = start + PER_PAGE;
      const pageData = data.slice(start, end);
      console.log('[Render] Rendering page', currentPage, 'items', start, 'to', end, '- showing', pageData.length, 'products');
      gallery.innerHTML = pageData.map(cardHTML).join("");
      console.log('[Render] Gallery updated with', pageData.length, 'product cards');
      window.scrollTo({ top: 0, behavior: "smooth" });
    } else {
      console.warn('[Render] Gallery element not found!');
    }
    renderPager(data.length);
    console.log('[Render] Render complete');
  }

  // ===== 5) Events =====
  document.querySelectorAll(".valuesButton[data-filter]").forEach(btn => {
    btn.addEventListener("click", () => { activeCategory = btn.dataset.filter; currentPage = 1; render(); });
  });
  document.querySelectorAll(".valuesButton[data-offer]").forEach(btn => {
    btn.addEventListener("click", () => { activeOffer = btn.dataset.offer; currentPage = 1; render(); });
  });

  if (searchInput) {
    searchInput.addEventListener("input", () => { keyword = searchInput.value || ""; currentPage = 1; render(); });
  }
  if (priceRange && currentPrice) {
    currentPrice.textContent = priceRange.value;
    priceRange.addEventListener("input", function () {
      currentPrice.textContent = this.value;
      currentPage = 1; render();
    });
  }
  // collapsible filter sections
  document.querySelectorAll(".filter-section h3").forEach(title => {
    title.addEventListener("click", () => {
      const panel = title.nextElementSibling;
      if (!panel) return;
      panel.classList.toggle("open");
      panel.style.display = panel.classList.contains("open") ? "block" : "none";
    });
  });

  // ===== 6) Watchlist (global for onclick) =====
  window.toggleLike = function toggleLike(productId) {
    const i = WATCHLIST.indexOf(productId);
    if (i === -1) WATCHLIST.push(productId);
    else WATCHLIST.splice(i, 1);
    localStorage.setItem("watchlist", JSON.stringify(WATCHLIST));
    render();
  };

  // ===== 7) Go! =====
  loadProducts();
});
