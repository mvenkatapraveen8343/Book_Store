document.addEventListener('DOMContentLoaded', initializeAllFeatures);

function initializeAllFeatures() {
    initializeNavigation();
    initializeDropdowns();
    initializeAuthForms();
    initializeSearchFilters();
    initializeCartFunctionality();
    initializeProductInteractions();
    initializeAdminFeatures();
    initializeFilePreview();
    initializePaymentFunctionality();
    initializeFormValidation();
}

function initializeNavigation() {
    const mobileToggle = document.getElementById('mobileToggle');
    const mobileClose = document.getElementById('mobileClose');
    const navOverlay = document.getElementById('navOverlay');
    const mainNav = document.getElementById('mainNav');
    
    if (!mobileToggle || !mainNav) return;

    function openMobileMenu() {
        mainNav.classList.add('active');
        if (navOverlay) navOverlay.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }

    function closeMobileMenu() {
        mainNav.classList.remove('active');
        if (navOverlay) navOverlay.style.display = 'none';
        document.body.style.overflow = '';
        document.querySelectorAll('.user-menu').forEach(menu => menu.classList.remove('active'));
    }

    if (mobileToggle) {
        mobileToggle.addEventListener('click', openMobileMenu);
    }
    
    if (mobileClose) {
        mobileClose.addEventListener('click', closeMobileMenu);
    }
    
    if (navOverlay) {
        navOverlay.addEventListener('click', closeMobileMenu);
    }
}

function initializeDropdowns() {
    const userMenus = document.querySelectorAll('.user-menu');
    
    userMenus.forEach(menu => {
        const userBtn = menu.querySelector('.user-btn');
        if (userBtn) {
            userBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                userMenus.forEach(otherMenu => {
                    if (otherMenu !== menu) otherMenu.classList.remove('active');
                });
                menu.classList.toggle('active');
            });
        }
    });

    document.addEventListener('click', e => {
        if (!e.target.closest('.user-menu')) {
            userMenus.forEach(menu => menu.classList.remove('active'));
        }
    });
}

function initializeAuthForms() {
    const mobileInput = document.getElementById('mobile');
    if (mobileInput) {
        mobileInput.addEventListener('input', function() {
            this.value = this.value.replace(/[^0-9]/g, '').slice(0, 10);
        });
    }

    const otpInputs = document.querySelectorAll('input[name="cotp"]');
    otpInputs.forEach(input => {
        input.addEventListener('input', function() {
            this.value = this.value.replace(/[^0-9]/g, '').slice(0, 6);
        });
    });

    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                submitBtn.disabled = true;

                setTimeout(() => {
                    if (submitBtn.disabled) {
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                    }
                }, 3000);
            }
        });
    });
}

function initializeFormValidation() {
    const passwordForms = document.querySelectorAll('form');
    passwordForms.forEach(form => {
        const password = form.querySelector('input[name="password"]');
        const cpassword = form.querySelector('input[name="cpassword"]');
        const newPassword = form.querySelector('input[name="new_password"]');
        const confirmPassword = form.querySelector('input[name="confirm_password"]');

        function validatePasswords(pass1, pass2) {
            if (pass1 && pass2 && pass1.value && pass2.value && pass1.value !== pass2.value) {
                pass2.setCustomValidity('Passwords do not match');
                return false;
            } else {
                pass2.setCustomValidity('');
                return true;
            }
        }

        if (password && cpassword) {
            password.addEventListener('input', () => validatePasswords(password, cpassword));
            cpassword.addEventListener('input', () => validatePasswords(password, cpassword));
        }

        if (newPassword && confirmPassword) {
            newPassword.addEventListener('input', () => validatePasswords(newPassword, confirmPassword));
            confirmPassword.addEventListener('input', () => validatePasswords(newPassword, confirmPassword));
        }
    });

    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('blur', function() {
            const email = this.value.trim();
            if (email && !isValidEmail(email)) {
                showFieldError(this, 'Please enter a valid email address');
            } else {
                clearFieldError(this);
            }
        });
    });
}

function initializeSearchFilters() {
    const searchInput = document.getElementById('searchInput');
    const categoryFilter = document.getElementById('categoryFilter');
    const bookCards = document.querySelectorAll('.book-card');

    if (searchInput && bookCards.length > 0) {
        function filterBooks() {
            const searchTerm = searchInput.value.toLowerCase();
            const selectedCategory = categoryFilter ? categoryFilter.value : '';

            bookCards.forEach(card => {
                const title = (card.dataset.title || '').toLowerCase();
                const category = (card.dataset.category || '').toLowerCase();
                const matchesSearch = title.includes(searchTerm);
                const matchesCategory = !selectedCategory || category === selectedCategory;
                card.style.display = (matchesSearch && matchesCategory) ? 'block' : 'none';
            });
        }

        searchInput.addEventListener('input', filterBooks);
        if (categoryFilter) categoryFilter.addEventListener('change', filterBooks);
    }

    const searchProducts = document.getElementById('searchProducts');
    const productCards = document.querySelectorAll('.product-card');

    if (searchProducts && productCards.length > 0) {
        searchProducts.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            productCards.forEach(card => {
                const title = (card.dataset.title || '').toLowerCase();
                const category = (card.dataset.category || '').toLowerCase();
                const matchesSearch = title.includes(searchTerm) || category.includes(searchTerm);
                card.style.display = matchesSearch ? 'block' : 'none';
            });
        });
    }
}

function initializeProductInteractions() {
    const deleteButtons = document.querySelectorAll('.btn-danger');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this book?')) {
                e.preventDefault();
            }
        });
    });
}

function initializeAdminFeatures() {
}

function initializeFilePreview() {
    const fileInput = document.getElementById('product_image');
    const filePreview = document.getElementById('filePreview');
    
    if (fileInput && filePreview) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    filePreview.innerHTML = `<img src="${e.target.result}" class="preview-image" alt="Preview">`;
                };
                reader.readAsDataURL(file);
            } else {
                filePreview.innerHTML = '';
            }
        });
        
        console.log('File preview initialized');
    }
}

function initializeCartFunctionality() {
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.dataset.productId;
            const stock = parseInt(this.dataset.stock);
            const button = this;

            if (stock <= 0) {
                showNotification('This book is out of stock', 'error');
                return;
            }

            const originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
            button.disabled = true;

            const timeoutId = setTimeout(() => {
                button.innerHTML = originalText;
                button.disabled = false;
            }, 800);

            fetch(`/add_to_cart/${productId}`, {
                method: 'POST',
                headers: { 
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                }
            })
            .then(res => res.json())
            .then(data => {
                clearTimeout(timeoutId);
                if (data.success) {
                    const newStock = data.stock;
                    button.dataset.stock = newStock;

                    const card = button.closest('.book-card');
                    const stockElement = card.querySelector('.book-stock span');
                    if (stockElement) {
                        if (newStock > 0) {
                            stockElement.innerHTML = `<i class="fas fa-check-circle"></i> ${newStock} in stock`;
                        } else {
                            stockElement.className = 'out-of-stock';
                            stockElement.innerHTML = '<i class="fas fa-times-circle"></i> Out of stock';
                        }
                    }

                    if (newStock <= 0) {
                        button.innerHTML = '<i class="fas fa-bell"></i> Notify Me';
                        button.disabled = true;
                        button.classList.remove('btn-primary');
                        button.classList.add('btn-outline');
                    } else {
                        button.innerHTML = originalText;
                        button.disabled = false;
                    }

                    if (data.cart_count !== undefined) {
                        updateCartCountTo(data.cart_count);
                        sessionStorage.setItem('cart_count', data.cart_count);
                    }

                    showNotification('Book added to cart successfully!', 'success');
                } else {
                    button.innerHTML = originalText;
                    button.disabled = false;
                    showNotification(data.error || 'Failed to add to cart', 'error');
                }
            })
            .catch(() => {
                clearTimeout(timeoutId);
                button.innerHTML = originalText;
                button.disabled = false;
                showNotification('Please check your internet connection', 'error');
            });
        });
    });

    const savedCartCount = sessionStorage.getItem('cart_count');
    if (savedCartCount) {
        updateCartCountTo(parseInt(savedCartCount));
    }
    initializeCartQuantityButtons();
}

function initializeCartQuantityButtons() {
    const quantityButtons = document.querySelectorAll('.quantity-btn');
    
    quantityButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const url = this.getAttribute('href');
            if (!url) return;
            
            const originalHtml = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            this.classList.add('disabled');
            
            fetch(url, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (data.cart_count !== undefined) {
                        updateCartCountTo(data.cart_count);
                        sessionStorage.setItem('cart_count', data.cart_count);
                    }
                    
                    if (data.removed) {
                        window.location.reload();
                        return;
                    }
                    
                    const quantityDisplay = this.closest('.quantity-buttons').querySelector('.quantity-display');
                    if (quantityDisplay && data.quantity) {
                        quantityDisplay.textContent = data.quantity;
                    }
                    
                    const itemTotal = this.closest('.cart-item').querySelector('.total-price');
                    if (itemTotal && data.total_price) {
                        itemTotal.textContent = data.total_price;
                    }
                    
                    const grandTotal = document.querySelector('.grand-total');
                    if (grandTotal && data.grand_total !== undefined) {
                        grandTotal.textContent = '₹' + data.grand_total;
                    }
                    
                    showNotification('Cart updated successfully', 'success');
                } else {
                    showNotification(data.message || 'Failed to update cart', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Failed to update cart', 'error');
            })
            .finally(() => {
                this.innerHTML = originalHtml;
                this.classList.remove('disabled');
            });
        });
    });
    
    const removeButtons = document.querySelectorAll('.remove-btn');
    removeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const url = this.getAttribute('href');
            if (!url) return;
            
            if (!confirm('Are you sure you want to remove this item from your cart?')) {
                return;
            }
            
            const originalHtml = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Removing...';
            this.disabled = true;
            
            fetch(url, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (data.cart_count !== undefined) {
                        updateCartCountTo(data.cart_count);
                        sessionStorage.setItem('cart_count', data.cart_count);
                    }
                    
                    const cartItem = this.closest('.cart-item');
                    if (cartItem) {
                        cartItem.remove();
                    }
                    
                    const grandTotal = document.querySelector('.grand-total');
                    if (grandTotal && data.grand_total !== undefined) {
                        grandTotal.textContent = '₹' + data.grand_total;
                    }
                    
                    const remainingItems = document.querySelectorAll('.cart-item');
                    if (remainingItems.length === 0) {
                        window.location.reload();
                    }
                    
                    showNotification('Item removed from cart', 'success');
                } else {
                    showNotification(data.message || 'Failed to remove item', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Failed to remove item', 'error');
            })
            .finally(() => {
                this.innerHTML = originalHtml;
                this.disabled = false;
            });
        });
    });
}

function initializePaymentFunctionality() {
    const checkoutBtn = document.getElementById('checkoutBtn');

    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', function() {
            const grandTotalText = document.querySelector('.grand-total')?.textContent;
            const total = parseInt(grandTotalText?.replace(/[₹,]/g, '') || '0');

            if (!total || total <= 0) {
                showNotification("Your cart is empty!", 'error');
                return;
            }

            const user_id = document.body.dataset.userId || '{{ user_id }}';
            const amountInPaise = total * 100;

            const options = {
                key: "rzp_test_RTMUKCN9huQkLG",
                amount: amountInPaise,
                currency: "INR",
                name: "BookHub",
                description: "Book Purchase",
                image: "/static/images/logo.png",
                handler: function(response) {
                    showNotification('Payment successful!', 'success');
                    updateCartCountTo(0);
                    sessionStorage.setItem('cart_count', '0');

                    fetch("/payment_success", {
                        method: "POST",
                        headers: { "Content-Type": "application/x-www-form-urlencoded" },
                        body: new URLSearchParams({
                            razorpay_payment_id: response.razorpay_payment_id,
                            userid: user_id
                        })
                    }).finally(() => {
                        setTimeout(() => {
                            window.location.href = "/user_dashboard";
                        }, 1200);
                    });
                },
                prefill: {
                    name: document.body.dataset.userName || "Customer",
                    email: "mvenkatapraveen8343@gmail.com",
                    contact: "+91 6301866127"
                },
                theme: { color: "#2563eb" }
            };

            const rzp = new Razorpay(options);
            rzp.on('payment.failed', function() {
                showNotification("Payment failed. Please try again.", 'error');
            });
            rzp.open();
        });
    }
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function showFieldError(input, message) {
    clearFieldError(input);
    const errorElement = document.createElement('div');
    errorElement.className = 'error-message';
    errorElement.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
    input.parentElement.appendChild(errorElement);
    input.parentElement.classList.add('error');
}

function clearFieldError(input) {
    const formGroup = input.parentElement;
    const existingError = formGroup.querySelector('.error-message');
    if (existingError) existingError.remove();
    formGroup.classList.remove('error');
}

function updateCartCountTo(newCount) {
    const cartCounts = document.querySelectorAll('.cart-count');
    cartCounts.forEach(cartCount => {
        cartCount.textContent = newCount;
        cartCount.style.display = newCount === 0 ? 'none' : 'flex';
    });

    if (typeof updateSessionCartCount === 'function') {
        updateSessionCartCount(newCount);
    }
}

function showNotification(message, type = 'info') {
    const existing = document.querySelector('.notification');
    if (existing) existing.remove();

    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close">&times;</button>
    `;
    
    if (!document.querySelector('#notification-styles')) {
        const styles = document.createElement('style');
        styles.id = 'notification-styles';
        styles.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                padding: 1rem 1.5rem;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                display: flex;
                align-items: center;
                gap: 1rem;
                z-index: 10000;
                max-width: 400px;
                animation: slideInRight 0.3s ease;
            }
            .notification-success {
                border-left: 4px solid #10b981;
            }
            .notification-error {
                border-left: 4px solid #ef4444;
            }
            .notification-info {
                border-left: 4px solid #2563eb;
            }
            .notification-warning {
                border-left: 4px solid #f59e0b;
            }
            .notification-content {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                flex: 1;
            }
            .notification-close {
                background: none;
                border: none;
                font-size: 1.2rem;
                cursor: pointer;
                padding: 0;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;
        document.head.appendChild(styles);
    }
    
    document.body.appendChild(notification);
    
    notification.querySelector('.notification-close').addEventListener('click', () => notification.remove());
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}