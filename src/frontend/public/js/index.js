// app.js - Main frontend application logic for MyChama

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const mpesaLoginBtn = document.getElementById('mpesa-login-btn');
    const phoneInput = document.getElementById('login-phone');
    const passwordInput = document.getElementById('login-password');
    const signupPhoneInput = document.getElementById('signup-phone');
    const signupUsernameInput = document.getElementById('signup-username');
    const signupEmailInput = document.getElementById('signup-email');
    const signupPasswordInput = document.getElementById('signup-password');
    const authTabs = document.querySelectorAll('.tab');
    const authForms = document.querySelectorAll('.auth-form');
    
    // Base API URL
    const API_BASE_URL = window.location.origin.includes('localhost') 
        ? 'http://localhost:8000/api' 
        : 'https://your-production-api.com/api';
    
    // Current login request ID for polling
    let currentLoginRequestId = null;
    let loginPollInterval = null;
    
    // Initialize application
    init();
    
    function init() {
        // Check for existing session
        checkExistingSession();
        
        // Setup event listeners
        setupEventListeners();
    }
    
    function checkExistingSession() {
        const token = localStorage.getItem('authToken');
        if (token) {
            // Verify token is still valid
            verifyToken(token)
                .then(valid => {
                    if (valid) {
                        redirectToDashboard();
                    } else {
                        localStorage.removeItem('authToken');
                    }
                })
                .catch(error => {
                    console.error('Session verification failed:', error);
                    localStorage.removeItem('authToken');
                });
        }
    }
    
    function setupEventListeners() {
        // Tab switching
        authTabs.forEach(tab => {
            tab.addEventListener('click', switchAuthTab);
        });
        
        // Form submissions
        if (loginForm) {
            loginForm.addEventListener('submit', handleLogin);
        }
        
        if (signupForm) {
            signupForm.addEventListener('submit', handleSignup);
        }
        
        if (mpesaLoginBtn) {
            mpesaLoginBtn.addEventListener('click', handleMpesaLogin);
        }
        
        // Phone number formatting
        if (phoneInput) {
            phoneInput.addEventListener('blur', formatPhoneNumber);
        }
        
        if (signupPhoneInput) {
            signupPhoneInput.addEventListener('blur', formatPhoneNumber);
        }
    }
    
    function switchAuthTab(e) {
        const tabName = e.target.getAttribute('data-tab');
        
        // Update active tab
        authTabs.forEach(tab => {
            tab.classList.remove('active');
            if (tab.getAttribute('data-tab') === tabName) {
                tab.classList.add('active');
            }
        });
        
        // Show corresponding form
        authForms.forEach(form => {
            form.classList.remove('active');
            if (form.id === `${tabName}-form`) {
                form.classList.add('active');
            }
        });
    }
    
    async function handleLogin(e) {
        e.preventDefault();
        
        const phone = formatPhoneNumber(phoneInput.value);
        const password = passwordInput.value;
        
        if (!phone || !password) {
            showAlert('Please fill in all fields', 'error');
            return;
        }
        
        try {
            showLoading(loginForm, 'Logging in...');
            
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    phone_number: phone,
                    password: password
                })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Login failed');
            }
            
            // Store token and redirect
            localStorage.setItem('authToken', data.access_token);
            redirectToDashboard();
        } catch (error) {
            console.error('Login error:', error);
            showAlert(error.message || 'Login failed. Please try again.', 'error');
        } finally {
            hideLoading(loginForm, 'Login');
        }
    }
    
    async function handleSignup(e) {
        e.preventDefault();
        
        const username = signupUsernameInput.value.trim();
        const phone = formatPhoneNumber(signupPhoneInput.value);
        const email = signupEmailInput.value.trim();
        const password = signupPasswordInput.value;
        
        if (!username || !phone || !email || !password) {
            showAlert('Please fill in all fields', 'error');
            return;
        }
        
        if (password.length < 6) {
            showAlert('Password must be at least 6 characters', 'error');
            return;
        }
        
        try {
            showLoading(signupForm, 'Creating account...');
            
            const response = await fetch(`${API_BASE_URL}/auth/signup`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: username,
                    phone_number: phone,
                    email: email,
                    password: password
                })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Signup failed');
            }
            
            // Automatically log the user in after signup
            localStorage.setItem('authToken', data.access_token);
            showAlert('Account created successfully!', 'success');
            redirectToDashboard();
        } catch (error) {
            console.error('Signup error:', error);
            showAlert(error.message || 'Signup failed. Please try again.', 'error');
        } finally {
            hideLoading(signupForm, 'Create Account');
        }
    }
    
    async function handleMpesaLogin() {
        const phone = formatPhoneNumber(phoneInput.value);
        
        if (!phone) {
            showAlert('Please enter your phone number', 'error');
            return;
        }
        
        try {
            showLoading(mpesaLoginBtn, 'Sending request...');
            
            const response = await fetch(`${API_BASE_URL}/auth/mpesa/login/initiate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    phone_number: phone
                })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Failed to initiate M-Pesa login');
            }
            
            // Start polling for login status
            currentLoginRequestId = data.request_id;
            startLoginPolling(currentLoginRequestId);
            
            showAlert('Check your phone for M-Pesa prompt', 'info');
        } catch (error) {
            console.error('M-Pesa login error:', error);
            showAlert(error.message || 'M-Pesa login failed. Please try again.', 'error');
        } finally {
            hideLoading(mpesaLoginBtn, 'Login with M-Pesa');
        }
    }
    
    function startLoginPolling(requestId) {
        // Clear any existing interval
        if (loginPollInterval) {
            clearInterval(loginPollInterval);
        }
        
        loginPollInterval = setInterval(async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/auth/mpesa/login/status/${requestId}`);
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.detail || 'Login status check failed');
                }
                
                if (data.access_token) {
                    // Login successful
                    clearInterval(loginPollInterval);
                    localStorage.setItem('authToken', data.access_token);
                    redirectToDashboard();
                } else if (data.status === 'expired' || data.status === 'failed') {
                    // Login failed or expired
                    clearInterval(loginPollInterval);
                    showAlert(data.message || 'Login failed. Please try again.', 'error');
                }
                // Continue polling if status is pending
            } catch (error) {
                console.error('Polling error:', error);
                clearInterval(loginPollInterval);
                showAlert('Error checking login status', 'error');
            }
        }, 2000); // Poll every 2 seconds
    }
    
    async function verifyToken(token) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/verify`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            return response.ok;
        } catch (error) {
            console.error('Token verification error:', error);
            return false;
        }
    }
    
    function formatPhoneNumber(phone) {
        if (!phone) return '';
        
        // Remove all non-digit characters
        const digits = phone.replace(/\D/g, '');
        
        // Convert to 254 format
        if (digits.startsWith('0') && digits.length === 10) {
            return '254' + digits.substring(1);
        } else if (digits.startsWith('7') && digits.length === 9) {
            return '254' + digits;
        } else if (digits.startsWith('254') && digits.length === 12) {
            return digits;
        } else if (digits.length === 9) {
            return '254' + digits;
        }
        
        // Return as is if doesn't match Kenyan formats
        return digits;
    }
    
    function showLoading(formElement, loadingText = 'Loading...') {
        const submitButton = formElement.querySelector('button[type="submit"]') || formElement;
        submitButton.disabled = true;
        
        if (submitButton.tagName === 'BUTTON') {
            const originalText = submitButton.textContent;
            submitButton.dataset.originalText = originalText;
            submitButton.textContent = loadingText;
        }
    }
    
    function hideLoading(formElement, originalText = 'Submit') {
        const submitButton = formElement.querySelector('button[type="submit"]') || formElement;
        submitButton.disabled = false;
        
        if (submitButton.tagName === 'BUTTON') {
            submitButton.textContent = submitButton.dataset.originalText || originalText;
        }
    }
    
    function showAlert(message, type = 'info') {
        // Remove any existing alerts
        const existingAlert = document.querySelector('.alert');
        if (existingAlert) {
            existingAlert.remove();
        }
        
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;
        
        // Add some basic styling
        alertDiv.style.position = 'fixed';
        alertDiv.style.top = '20px';
        alertDiv.style.right = '20px';
        alertDiv.style.padding = '15px';
        alertDiv.style.borderRadius = '5px';
        alertDiv.style.color = 'white';
        alertDiv.style.zIndex = '1000';
        
        switch (type) {
            case 'error':
                alertDiv.style.backgroundColor = '#ef4444';
                break;
            case 'success':
                alertDiv.style.backgroundColor = '#10b981';
                break;
            case 'info':
                alertDiv.style.backgroundColor = '#3b82f6';
                break;
            default:
                alertDiv.style.backgroundColor = '#3b82f6';
        }
        
        document.body.appendChild(alertDiv);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
    
    function redirectToDashboard() {
        window.location.href = '/dashboard.html';
    }
    
    // Make functions available globally if needed
    window.formatPhoneNumber = formatPhoneNumber;
});