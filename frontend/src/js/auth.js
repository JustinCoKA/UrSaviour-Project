// Configuration for different environments
const API_CONFIG = {
    development: {
        baseURL: '/api/v1'
    },
    production: {
        baseURL: 'https://api.ursaviour.com/api/v1'
    }
};

// Determine current environment
const isProduction = window.location.hostname === 'www.ursaviour.com' || window.location.hostname === 'ursaviour.com';
const config = isProduction ? API_CONFIG.production : API_CONFIG.development;

// Login form handler
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch(`${config.baseURL}/auth/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email: email,
                        password: password
                    })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    
                    // Store the token and user info
                    localStorage.setItem('access_token', data.access_token);
                    localStorage.setItem('user', JSON.stringify(data.user));
                    
                    // Redirect to dashboard or home page
                    window.location.href = '/template.html';
                } else {
                    const errorData = await response.json();
                    alert('Login failed: ' + errorData.detail);
                }
            } catch (error) {
                console.error('Login error:', error);
                alert('An error occurred during login. Please try again.');
            }
        });
    }
});

// Check if user is logged in
function isLoggedIn() {
    return localStorage.getItem('access_token') !== null;
}

// Get current user
function getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

// Logout function
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = '/login.html';
}

// Add authorization header to API requests
function getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return token ? {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    } : {
        'Content-Type': 'application/json'
    };
}