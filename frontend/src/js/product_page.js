//1. product_page.js

document.addEventListener("DOMContentLoaded", function() {
    const gallery = document.getElementById("product-gallery");
    const moreBtn = document.getElementById("more-here");
    
    // Check if elements exist before proceeding
    if (!gallery || !moreBtn) {
        console.error("Product gallery or more button not found.");
        return;
    }

    // Generate fake data 
    let products = [];
    for (let i = 1; i <= 20; i++) {
        products.push({
            name: "Item " + i,
            image: "https://placehold.co/250x150?text=Item+" + i,
            stores: [
                { brand: "Store A", price: (i * 2.5).toFixed(2) },
                { brand: "Store B", price: (i * 2.3).toFixed(2) },
                { brand: "Store C", price: (i * 2.7).toFixed(2) }, 
                { brand: "Store D", price: (i * 2.7).toFixed(2) }
            ]
        });
    }

    let shown = 0;
    const perPage = 6;

    function showProducts() {
        for (let i = shown; i < shown + perPage && i < products.length; i++) {
            const item = products[i];
            const card = document.createElement("div");
            card.className = "card";

            const priceList = item.stores.map(store =>
                `<div><span>${store.brand}</span><span>$${store.price}</span></div>`
            ).join("");

            card.innerHTML = `
                <img src="${item.image}" alt="${item.name}">
                <h3>${item.name}</h3>
                <div class="price-list">
                    ${priceList}
                </div>
            `;
            gallery.appendChild(card);
        }
        shown += perPage;

        if (shown >= products.length) {
            moreBtn.style.display = "none";
        }
    }
//2. Price range Buttion 
    moreBtn.addEventListener("click", showProducts);

    // Show first batch
    showProducts();
});

const priceRange = document.getElementById('priceRange');
        const currentPrice = document.getElementById('currentPrice');

        priceRange.addEventListener('input', function() {
            currentPrice.textContent = this.value;
        });

//3. Accordon 
var acc = document.getElementsByClassName("ac-Catergories");
var i;

for (i = 0; i < acc.length; i++) {
  acc[i].addEventListener("click", function() {
    /* Toggle between adding and removing the "active" class,
    to highlight the button that controls the panel */
    this.classList.toggle("active");

    /* Toggle between hiding and showing the active panel */
    var panel = this.nextElementSibling;
    if (panel.style.display === "block") {
      panel.style.display = "none";
    } else {
      panel.style.display = "block";
    }
  });
}