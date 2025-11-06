// Configuration for different environments
const API_CONFIG = {
    development: {
        // Use explicit API origin in local development (no reverse proxy when serving static files)
        baseURL: 'http://localhost:8000/api/v1'
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
    const registerForm = document.getElementById('registerForm');
    
    // Password strength checker for registration
    const passwordField = document.getElementById('password');
    const strengthBar = document.getElementById('strength-bar');
    const strengthText = document.getElementById('strength-text');
    
    if (passwordField && strengthBar && strengthText) {
        passwordField.addEventListener('input', function() {
            updatePasswordStrength(passwordField.value);
        });
    }
    
    function checkPasswordStrength(password) {
        let strength = 0;
        if (password.length >= 8) strength++;
        if (/[A-Z]/.test(password)) strength++;
        if (/[a-z]/.test(password)) strength++;
        if (/\d/.test(password)) strength++;
        if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength++;
        return strength;
    }
    
    function updatePasswordStrength(password) {
        const score = checkPasswordStrength(password);
        const percent = (score / 5) * 100;
        strengthBar.style.width = percent + "%";
        
        if (score <= 2) {
            strengthBar.style.backgroundColor = "#e57373"; // weak (red)
            strengthText.textContent = "Weak";
        } else if (score === 3 || score === 4) {
            strengthBar.style.backgroundColor = "#ffb74d"; // medium (orange)
            strengthText.textContent = "Medium";
        } else {
            strengthBar.style.backgroundColor = "#81c784"; // strong (green)
            strengthText.textContent = "Strong";
        }
    }
    
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
                    
                    // Redirect to watchlist page after successful login
                    window.location.href = 'watchlist.html';
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

    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const firstName = document.getElementById('first_name').value;
            const lastName = document.getElementById('last_name').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password').value;
            
            // Enhanced client-side validation
            const errors = [];
            
            if (password.length < 8) {
                errors.push("Password must be at least 8 characters long.");
            }
            if (!/\d/.test(password)) {
                errors.push("Password must include at least one number.");
            }
            if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
                errors.push("Password must include at least one special character.");
            }
            if (password !== confirmPassword) {
                errors.push("Passwords do not match.");
            }
            
            if (errors.length > 0) {
                alert(errors.join("\n"));
                return;
            }
            
            try {
                const response = await fetch(`${config.baseURL}/auth/register`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        // API expects camelCase per spec
                        firstName: firstName,
                        lastName: lastName,
                        email: email,
                        password: password
                    })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    alert('Registration successful! Please log in.');
                    // Use relative path to avoid server-root mismatch (e.g., 127.0.0.1:5500 vs /frontend/src)
                    window.location.href = 'login.html';
                } else {
                    const errorData = await response.json();
                    alert('Registration failed: ' + (errorData.detail || 'Unknown error'));
                }
            } catch (error) {
                console.error('Registration error:', error);
                alert('An error occurred during registration. Please try again.');
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
    // Use relative path for portability across dev servers
    window.location.href = 'login.html';
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