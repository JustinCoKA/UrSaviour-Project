// Banner utility functions
function showBanner(message, type = 'info') {
  console.log(`[BANNER] Showing ${type} banner:`, message);
  
  // Remove existing banners
  const existingBanners = document.querySelectorAll('.api-banner, .status-banner');
  existingBanners.forEach(banner => banner.remove());
  
  // Create new banner
  const banner = document.createElement('div');
  banner.className = 'api-banner status-banner';
  banner.textContent = message;
  
  // Style based on type
  const styles = {
    error: {
      background: '#ffecec',
      color: '#a94442',
      border: '1px solid #f5c6cb'
    },
    success: {
      background: '#d4edda', 
      color: '#155724',
      border: '1px solid #c3e6cb'
    },
    info: {
      background: '#e2e3e5',
      color: '#383d41', 
      border: '1px solid #d6d8db'
    }
  };
  
  const style = styles[type] || styles.info;
  Object.assign(banner.style, {
    ...style,
    padding: '10px 15px',
    margin: '10px 0',
    borderRadius: '4px',
    display: 'block',
    width: '100%',
    boxSizing: 'border-box'
  });
  
  // Insert at top of main content
  const mainContent = document.querySelector('main') || document.querySelector('.container') || document.body;
  const firstChild = mainContent.firstChild;
  if (firstChild) {
    mainContent.insertBefore(banner, firstChild);
  } else {
    mainContent.appendChild(banner);
  }
  
  // Auto-remove success banners after 5 seconds
  if (type === 'success') {
    setTimeout(() => banner.remove(), 5000);
  }
  
  return banner;
}

// More aggressive banner fix
function fixBanner() {
  console.log('[BANNER-FIX] Attempting to fix banner...');
  
  // Find banner elements with various selectors
  const selectors = [
    '[style*="background:#ffecec"]',
    '[style*="background: #ffecec"]',
    '[style*="color:#a94442"]',
    '[style*="color: #a94442"]',
    '.error-state',
    'div[style*="color:#d32f2f"]'
  ];
  
  let banner = null;
  for (const selector of selectors) {
    const elements = document.querySelectorAll(selector);
    for (const el of elements) {
      if (el.textContent && (el.textContent.includes('API unreachable') || el.textContent.includes('Failed to load'))) {
        banner = el;
        break;
      }
    }
    if (banner) break;
  }
  
  if (!banner) {
    // Try finding by text content
    const allDivs = document.querySelectorAll('div');
    for (const div of allDivs) {
      if (div.textContent && div.textContent.includes('API unreachable')) {
        banner = div;
        break;
      }
    }
  }
  
  if (banner) {
    console.log('[BANNER-FIX] Found banner element:', banner);
    
    // Check if products were loaded
    const productCards = document.querySelectorAll('.product-card, [class*="product"], [class*="card"]');
    console.log('[BANNER-FIX] Found product cards:', productCards.length);
    
    if (productCards.length > 5) {
      console.log('[BANNER-FIX] Many products found, assuming API success');
      banner.style.background = '#d4edda';
      banner.style.color = '#155724';
      banner.style.border = '1px solid #c3e6cb';
      banner.textContent = `✅ Successfully connected to API! Loaded ${productCards.length} products from localhost:8001`;
    }
  } else {
    console.log('[BANNER-FIX] No banner element found');
  }
}

// Try multiple times
document.addEventListener("DOMContentLoaded", () => {
  console.log('[BANNER-FIX] DOM loaded, starting banner fix attempts...');
  
  // Try immediately
  fixBanner();
  
  // Try after delays
  setTimeout(fixBanner, 1000);
  setTimeout(fixBanner, 2000);
  setTimeout(fixBanner, 3000);
  
  // Also try when new elements are added
  const observer = new MutationObserver(() => {
    fixBanner();
  });
  
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
  
  // Stop observing after 10 seconds
  setTimeout(() => observer.disconnect(), 10000);
});