/* watchlist.js
 * Renders the user's watchlist as one-column rows.
 * Data source:
 *  - window.PRODUCTS if available
 *  - else, localStorage cache saved by product_page.js
 * Notifications:
 *  - Per-item "email me when discount starts" is stored in localStorage.
 */

(() => {
  const WATCHLIST_KEY = "urs_watchlist_v1";
  const NOTIFY_KEY = "urs_watch_notify_v1";
  const PRODUCTS_CACHE_KEY = "urs_products_cache_v1";

  // Read datasets
  const WATCHLIST = JSON.parse(localStorage.getItem(WATCHLIST_KEY) || "[]");
  const NOTIFY_MAP = JSON.parse(localStorage.getItem(NOTIFY_KEY) || "{}");
  let PRODUCTS = window.PRODUCTS;
  if (!Array.isArray(PRODUCTS)) {
    try {
      PRODUCTS = JSON.parse(localStorage.getItem(PRODUCTS_CACHE_KEY) || "[]");
    } catch (e) {
      console.warn("Failed to read PRODUCTS from cache:", e);
      PRODUCTS = [];
    }
  }

  // DOM
  const list = document.getElementById("watchlist-list");
  const empty = document.getElementById("empty-watchlist");

  // Fallback image helper
  const imgTag = (src, seed) =>
    `<img src="${src || ""}" alt="" loading="lazy"
      onerror="this.onerror=null;this.src='https://picsum.photos/seed/${encodeURIComponent(seed)}/300/200';"/>`;

  // Build a single row
  const rowHTML = (p) => {
    const badge = p.special ? `<span class="badge" data-type="${p.special.type}">${p.special.type}</span>` : "";

    // Build store price lines (show original+discount when available)
    const prices = p.stores.map(s => {
      const hasOriginal = typeof s.original_price === "number" && s.original_price > s.price;
      const right = hasOriginal
        ? `<span><span class="original">$${s.original_price.toFixed(2)}</span>$${Number(s.price).toFixed(2)}</span>`
        : `<span>$${Number(s.price).toFixed(2)}</span>`;
      return `<div class="price-line"><span>${s.brand}</span>${right}</div>`;
    }).join("");

    // Active discount info (if any)
    const discountInfo = p.special
      ? `<div style="margin-top:6px;font-size:.9rem;color:#0f766e;">
           Currently on <strong>${p.special.type}</strong> at <strong>${p.special.store}</strong>.
         </div>`
      : "";

    // Notify toggle state
    const notifyOn = !!NOTIFY_MAP[p.id];

    return `
      <div class="watch-row" data-id="${p.id}">
        <div class="watch-thumb">
          ${badge}
          ${imgTag(p.image, p.id)}
        </div>
        <div class="watch-details">
          <h3>${p.name} <span style="font-weight:500;color:#64748b;">(${p.category})</span></h3>
          <div class="store-prices">${prices}</div>
          ${discountInfo}
        </div>
        <div class="watch-actions">
          <button class="remove-btn" data-remove="${p.id}">Remove</button>
          <label class="notify-wrap">
            <input type="checkbox" data-notify="${p.id}" ${notifyOn ? "checked" : ""}/>
            Email me when a discount starts
          </label>
        </div>
      </div>
    `;
  };

  // Render list
  const render = () => {
    const items = PRODUCTS.filter(p => WATCHLIST.includes(p.id));
    if (items.length === 0) {
      empty.style.display = "block";
      list.innerHTML = "";
      return;
    }
    empty.style.display = "none";
    list.innerHTML = items.map(rowHTML).join("");

    // Bind remove buttons
    list.querySelectorAll("[data-remove]").forEach(btn => {
      btn.addEventListener("click", () => {
        const id = btn.getAttribute("data-remove");
        const wl = new Set(JSON.parse(localStorage.getItem(WATCHLIST_KEY) || "[]"));
        wl.delete(id);
        localStorage.setItem(WATCHLIST_KEY, JSON.stringify([...wl]));
        render();
      });
    });

    // Bind notify toggles
    list.querySelectorAll("[data-notify]").forEach(input => {
      input.addEventListener("change", () => {
        const id = input.getAttribute("data-notify");
        const map = JSON.parse(localStorage.getItem(NOTIFY_KEY) || "{}");
        map[id] = input.checked ? true : false;
        localStorage.setItem(NOTIFY_KEY, JSON.stringify(map));
      });
    });
  };

  // Init
  document.addEventListener("DOMContentLoaded", render);
})();
