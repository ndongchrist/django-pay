// static/js/cart.js
// Professional Frontend Cart – LocalStorage only (Fixed)

const CART_KEY = 'plate-cart';

function getCart() {
    return JSON.parse(localStorage.getItem(CART_KEY)) || [];
}

function saveCart(cart) {
    localStorage.setItem(CART_KEY, JSON.stringify(cart));
}

function getTotalItems(cart) {
    return cart.reduce((sum, item) => sum + item.quantity, 0);
}

function getCartTotal(cart) {
    return cart.reduce((sum, item) => sum + (item.price * item.quantity), 0).toFixed(2);
}

// Toast notification
function showToast(message) {
    const toast = document.createElement('div');
    toast.innerHTML = message;
    Object.assign(toast.style, {
        position: 'fixed',
        bottom: '30px',
        left: '50%',
        transform: 'translateX(-50%)',
        backgroundColor: '#111111',
        color: '#F5B81B',
        padding: '14px 28px',
        borderRadius: '60px',
        fontWeight: '600',
        zIndex: '1000',
        boxShadow: '0 10px 25px rgba(0,0,0,0.1)',
        fontFamily: 'Inter, sans-serif',
        animation: 'fadeInUp 0.3s ease'
    });
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s';
        setTimeout(() => toast.remove(), 300);
    }, 2800);
}

// ====================== ADD TO CART ======================
function addToCart(id, name, price, imageUrl) {
    let cart = getCart();
    const productId = parseInt(id);                    // Ensure number
    const existing = cart.find(item => item.id === productId);

    if (existing) {
        existing.quantity += 1;
        showToast(`✨ ${name} quantity increased — now ${existing.quantity} in basket`);
    } else {
        cart.push({
            id: productId,
            name: name,
            price: parseFloat(price),
            imageUrl: imageUrl || 'https://placehold.co/400x400/111111/F5B81B?text=Plate',
            quantity: 1
        });
        showToast(`✨ ${name} added to your basket — Free shipping over $100 ✨`);
    }

    saveCart(cart);
    updateHeaderBadge();
    renderCurrentPage();          // Refresh cart page instantly if open
}

// ====================== REMOVE ITEM ======================
function removeFromCart(id) {
    const productId = parseInt(id);
    let cart = getCart().filter(item => item.id !== productId);
    saveCart(cart);
    updateHeaderBadge();
    renderCurrentPage();
}

// ====================== UPDATE QUANTITY ======================
function updateQuantity(id, newQty) {
    const productId = parseInt(id);
    newQty = parseInt(newQty);

    if (newQty < 1) {
        removeFromCart(productId);   // Remove completely if quantity reaches 0
        return;
    }

    let cart = getCart();
    const item = cart.find(i => i.id === productId);
    if (item) {
        item.quantity = newQty;
        saveCart(cart);
        updateHeaderBadge();
        renderCurrentPage();
    }
}

// ====================== HEADER BADGE ======================
function updateHeaderBadge() {
    const badge = document.getElementById('cart-count-badge');
    if (badge) {
        const count = getTotalItems(getCart());
        badge.textContent = count;
        badge.style.display = count > 0 ? 'flex' : 'none';
    }
}

// ====================== RENDER PAGES ======================
function renderCurrentPage() {
    const cart = getCart();
    const path = window.location.pathname;

    if (path.includes('/cart/')) {
        renderCartPage(cart);
    } else if (path.includes('/checkout/')) {
        renderCheckoutPage(cart);
    }
}

function renderCartPage(cart) {
    const container = document.getElementById('cart-items');
    if (!container) return;

    if (cart.length === 0) {
        container.innerHTML = `
            <div style="text-align:center; padding:4rem 2rem; background:#fafafa; border-radius:16px;">
                <i class="fas fa-shopping-bag" style="font-size:4rem; color:#ddd; margin-bottom:1rem;"></i>
                <h3>Your basket is empty</h3>
                <p style="color:#666; max-width:300px; margin:1rem auto;">When you add beautiful dinnerware, it will appear here.</p>
                <a href="/" class="btn-primary" style="display:inline-block; margin-top:1rem;">Start Shopping</a>
            </div>`;
        document.getElementById('cart-summary').style.display = 'none';
        return;
    }

    let html = '';
    cart.forEach(item => {
        const subtotal = (item.price * item.quantity).toFixed(2);
        html += `
        <div style="display:flex; gap:1.5rem; padding:1.5rem 0; border-bottom:1px solid #eee; align-items:center;">
            <img src="${item.imageUrl}" alt="${item.name}" style="width:120px; height:120px; object-fit:cover; border-radius:12px;">
            
            <div style="flex:1;">
                <div style="font-weight:600; font-size:1.1rem;">${item.name}</div>
                <div style="color:#666; font-size:0.95rem;">$${item.price.toFixed(2)} USD each</div>
            </div>

            <!-- Quantity Controls -->
            <div style="display:flex; align-items:center; gap:8px; background:#f8f8f8; border-radius:50px; padding:6px 12px;">
                <button onclick="updateQuantity(${item.id}, ${item.quantity - 1})" 
                        style="width:32px;height:32px;border:none;background:#fff;border-radius:50%;cursor:pointer;">–</button>
                <span style="font-weight:600; min-width:28px; text-align:center;">${item.quantity}</span>
                <button onclick="updateQuantity(${item.id}, ${item.quantity + 1})" 
                        style="width:32px;height:32px;border:none;background:#fff;border-radius:50%;cursor:pointer;">+</button>
            </div>

            <div style="text-align:right; min-width:100px;">
                <div style="font-weight:700;">$${subtotal}</div>
            </div>

            <!-- Remove Button -->
            <button onclick="removeFromCart(${item.id})" 
                    style="background:none; border:none; color:#e74c3c; font-size:1.6rem; cursor:pointer; padding:0 12px;">
                ×
            </button>
        </div>`;
    });

    container.innerHTML = html;

    // Summary
    const total = getCartTotal(cart);
    document.getElementById('cart-subtotal').textContent = `$${total}`;
    document.getElementById('cart-total').textContent = `$${total}`;
    document.getElementById('cart-summary').style.display = 'block';
}

function renderCheckoutPage(cart) {
    // We no longer rely on localStorage cart for checkout page
    // The backend now provides real order data via Django template
    // So we do nothing here - the template already renders the real order
    console.log('%cCheckout page rendered via Django template', 'color:#F5B81B');
}

// ====================== INITIALIZATION ======================
document.addEventListener('DOMContentLoaded', function () {
    updateHeaderBadge();

    // Attach to all Add to Cart buttons
    document.querySelectorAll('.add-to-cart').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const id       = btn.getAttribute('data-id');
            const name     = btn.getAttribute('data-name');
            const price    = btn.getAttribute('data-price');
            const imageUrl = btn.getAttribute('data-image');

            addToCart(id, name, price, imageUrl);
        });
    });

    // Render if we are on cart or checkout page
    renderCurrentPage();

    console.log('%c✅ Platē Cart System initialized (Fixed Version)', 'color:#F5B81B; font-weight:700');
});

async function processCheckout() {
    const cart = getCart();
    if (cart.length === 0) {
        showToast("Your cart is empty");
        return;
    }

    const checkoutBtn = document.getElementById('proceed-checkout-btn');
    if (checkoutBtn) checkoutBtn.disabled = true;

    try {
        const response = await fetch(PROCESS_CHECKOUT_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')   // reuse your existing getCookie helper
            },
            body: JSON.stringify({ cart: cart })
        });

        const result = await response.json();

        if (result.success) {
            showToast(`✅ Order #${result.order_id} created successfully! Total: $${result.total}`);

            // Clear the frontend cart
            localStorage.removeItem(CART_KEY);
            updateHeaderBadge();

            window.location.href = CHECKOUT_URL;
        } else {
            showToast(`Error: ${result.error || 'Failed to create order'}`);
        }
    } catch (error) {
        console.error(error);
        showToast("Network error. Please try again.");
    } finally {
        if (checkoutBtn) checkoutBtn.disabled = false;
    }
}

// Helper: get CSRF token (add this if not already in scripts.js)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie) {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ====================== INITIALIZATION (Updated) ======================
document.addEventListener('DOMContentLoaded', function () {
    updateHeaderBadge();

    // Add to Cart buttons
    document.querySelectorAll('.add-to-cart').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const id       = btn.getAttribute('data-id');
            const name     = btn.getAttribute('data-name');
            const price    = btn.getAttribute('data-price');
            const imageUrl = btn.getAttribute('data-image');
            addToCart(id, name, price, imageUrl);
        });
    });

    // NEW: Checkout button listener
    const checkoutBtn = document.getElementById('proceed-checkout-btn');
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', processCheckout);
    }

    // Render current page
    renderCurrentPage();

    console.log('%c✅ Platē Cart + Checkout System Ready', 'color:#F5B81B; font-weight:700');
});
