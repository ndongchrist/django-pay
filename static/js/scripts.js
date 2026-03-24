// static/js/scripts.js

// ✅ Remove the hardcoded products array - we now use Django-rendered HTML

document.addEventListener('DOMContentLoaded', function() {
    
    // 🛒 Add to Cart Functionality (works with Django-rendered buttons)
    document.querySelectorAll('.add-to-cart').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const name = btn.getAttribute('data-name');
            const price = btn.getAttribute('data-price');
            const id = btn.getAttribute('data-id');
            
            // Show marketing-style toast notification
            showToast(`✨ ${name} added to your basket — Free shipping over $100 ✨`);
            
            // Optional: Send to backend via fetch for cart persistence
            // addToCartAPI(id, 1); 
        });
    });

    // 🍞 Toast notification helper
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

    // 🖼️ Enhance hero image if no product image available
    const heroImg = document.querySelector('.hero-image img');
    if(heroImg && !heroImg.src.includes('placehold')) {
        heroImg.style.transition = 'transform 0.3s ease';
        heroImg.addEventListener('mouseenter', () => {
            heroImg.style.transform = 'scale(1.02)';
        });
        heroImg.addEventListener('mouseleave', () => {
            heroImg.style.transform = 'scale(1)';
        });
    }

    // 🎨 Banner button interaction
    const bannerBtn = document.querySelector('.banner-btn');
    if(bannerBtn) {
        bannerBtn.addEventListener('click', () => {
            showToast("🎨 Exclusive pre-order launched! Discover limited Ochre Glaze series.");
            // Optional: redirect to collection page
            // window.location.href = "{% url 'collection:ochre' %}";
        });
    }

    // 📧 Newsletter form submission
    const newsletterForm = document.getElementById('newsletter-form');
    if(newsletterForm) {
        newsletterForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const email = newsletterForm.querySelector('input[type="email"]').value;
            
            // Simulate API call
            setTimeout(() => {
                showToast(`🎉 Thanks! Your 15% code is on its way to ${email}`);
                newsletterForm.reset();
            }, 500);
            
            // Real implementation:
            // fetch('/api/subscribe/', {
            //     method: 'POST',
            //     headers: {
            //         'Content-Type': 'application/json',
            //         'X-CSRFToken': getCookie('csrftoken')
            //     },
            //     body: JSON.stringify({ email })
            // });
        });
    }

    // 🔐 CSRF helper for AJAX requests
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

    // Optional: API function for cart persistence
    async function addToCartAPI(productId, quantity) {
        try {
            const response = await fetch('/api/cart/add/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ product_id: productId, quantity })
            });
            const data = await response.json();
            if (data.success) {
                // Update cart badge count if you have one
                const badge = document.querySelector('.cart-badge');
                if (badge) badge.textContent = data.cart_count;
            }
        } catch (error) {
            console.error('Cart error:', error);
        }
    }
});