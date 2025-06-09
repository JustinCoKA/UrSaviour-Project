// API Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';

// DOM Elements
const productGrid = document.querySelector('.product-grid');
const watchlistItems = document.querySelector('.watchlist-items');
const chatContainer = document.querySelector('.chat-container');

// Fetch Products
async function fetchProducts() {
    try {
        const response = await fetch(`${API_BASE_URL}/products`);
        const data = await response.json();
        displayProducts(data);
    } catch (error) {
        console.error('Error fetching products:', error);
    }
}

// Display Products
function displayProducts(products) {
    productGrid.innerHTML = products.map(product => `
        <div class="product-card">
            <img src="${product.image_url}" alt="${product.name}">
            <h3>${product.name}</h3>
            <p class="price">$${product.price}</p>
            <p class="discount">${product.discount}% OFF</p>
            <button onclick="addToWatchlist(${product.id})">Add to Watchlist</button>
        </div>
    `).join('');
}

// Add to Watchlist
async function addToWatchlist(productId) {
    try {
        const response = await fetch(`${API_BASE_URL}/watchlist`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ product_id: productId })
        });
        
        if (response.ok) {
            alert('Added to watchlist!');
            fetchWatchlist();
        }
    } catch (error) {
        console.error('Error adding to watchlist:', error);
    }
}

// Fetch Watchlist
async function fetchWatchlist() {
    try {
        const response = await fetch(`${API_BASE_URL}/watchlist`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        const data = await response.json();
        displayWatchlist(data);
    } catch (error) {
        console.error('Error fetching watchlist:', error);
    }
}

// Display Watchlist
function displayWatchlist(items) {
    watchlistItems.innerHTML = items.map(item => `
        <div class="watchlist-item">
            <img src="${item.product.image_url}" alt="${item.product.name}">
            <h3>${item.product.name}</h3>
            <p class="price">$${item.product.price}</p>
            <p class="discount">${item.product.discount}% OFF</p>
            <button onclick="removeFromWatchlist(${item.id})">Remove</button>
        </div>
    `).join('');
}

// Initialize Chat Interface
function initChatInterface() {
    chatContainer.innerHTML = `
        <div class="chat-messages"></div>
        <div class="chat-input">
            <input type="text" placeholder="Ask about deals...">
            <button onclick="sendMessage()">Send</button>
        </div>
    `;
}

// Send Message to AI Assistant
async function sendMessage() {
    const input = document.querySelector('.chat-input input');
    const message = input.value.trim();
    
    if (!message) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/assistant/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ message })
        });
        
        const data = await response.json();
        displayMessage(message, data.response);
        input.value = '';
    } catch (error) {
        console.error('Error sending message:', error);
    }
}

// Display Chat Message
function displayMessage(userMessage, assistantResponse) {
    const messagesContainer = document.querySelector('.chat-messages');
    messagesContainer.innerHTML += `
        <div class="message user-message">
            <p>${userMessage}</p>
        </div>
        <div class="message assistant-message">
            <p>${assistantResponse}</p>
        </div>
    `;
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    fetchProducts();
    initChatInterface();
    
    // Check if user is logged in
    const token = localStorage.getItem('token');
    if (token) {
        fetchWatchlist();
    }
}); 