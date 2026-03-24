// product data - professional dishes with marketing descriptions, high-quality imagery placeholders
    const products = [
        { id: 1, name: "The Alchemy Plate", desc: "Hand-thrown stoneware with molten yellow glaze.", price: 68, img: "https://placehold.co/400x400/111111/F5B81B?text=Alchemy+Plate" },
        { id: 2, name: "Onyx & Gold Rim", desc: "Black porcelain with 24k gold rim, elegant contrast.", price: 89, img: "https://placehold.co/400x400/222222/F5B81B?text=Onyx+Gold" },
        { id: 3, name: "Curve Bowl Set", desc: "Set of 4 matte black nesting bowls, yellow undertones.", price: 72, img: "https://placehold.co/400x400/1E1E1E/F5B81B?text=Bowl+Set" },
        { id: 4, name: "Signature Yellow Platter", desc: "Statement piece, reactive glaze, 14 inches.", price: 124, img: "https://placehold.co/400x400/2C2C2C/F5B81B?text=Yellow+Platter" }
    ];

    const productGrid = document.getElementById('products-grid');
    function renderProducts() {
        if(!productGrid) return;
        productGrid.innerHTML = '';
        products.forEach(prod => {
            const card = document.createElement('div');
            card.className = 'product-card';
            card.innerHTML = `
                <img class="product-img" src="${prod.img}" alt="${prod.name}" loading="lazy">
                <div class="product-info">
                    <div class="product-title">${prod.name}</div>
                    <div class="product-desc">${prod.desc}</div>
                    <div class="price">$${prod.price} <small>USD</small></div>
                    <button class="add-to-cart" data-id="${prod.id}" data-name="${prod.name}" data-price="${prod.price}">
                        <i class="fas fa-shopping-bag"></i> Add to cart
                    </button>
                </div>
            `;
            productGrid.appendChild(card);
        });

        // attach add to cart event listeners (simulate marketing toast)
        document.querySelectorAll('.add-to-cart').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const name = btn.getAttribute('data-name');
                // show a mini marketing style notification
                const toast = document.createElement('div');
                toast.innerText = `✨ ${name} added to your basket — Free shipping over $100 ✨`;
                toast.style.position = 'fixed';
                toast.style.bottom = '30px';
                toast.style.left = '50%';
                toast.style.transform = 'translateX(-50%)';
                toast.style.backgroundColor = '#111111';
                toast.style.color = '#F5B81B';
                toast.style.padding = '14px 28px';
                toast.style.borderRadius = '60px';
                toast.style.fontWeight = '600';
                toast.style.zIndex = '1000';
                toast.style.boxShadow = '0 10px 25px rgba(0,0,0,0.1)';
                toast.style.fontFamily = 'Inter, sans-serif';
                document.body.appendChild(toast);
                setTimeout(() => toast.remove(), 2800);
            });
        });
    }

    // replace placeholder hero image with more professional food-styled image? but keep high quality marketing.
    // We also improve hero image to a ceramic set representation. I'll set a more elegant image using unsplash-like placeholder but custom.
    const heroImg = document.querySelector('.hero-image img');
    if(heroImg) {
        heroImg.src = "https://placehold.co/800x600/FFFFFF/222222?text=Handcrafted+Porcelain+Collection&fontsize=14";
        heroImg.alt = "Curated dinnerware set with yellow accents";
    }

    // update gallery images for more professional look (yellow/black/white)
    const galleryImgs = document.querySelectorAll('.gallery-item img');
    const gallerySrcs = [
        "https://placehold.co/800x600/FAF7F0/222222?text=Elegant+Yellow+Table+Setting",
        "https://placehold.co/800x600/F5B81B/FFFFFF?text=Black+White+Dinnerware",
        "https://placehold.co/800x600/111111/F5B81B?text=Chef's+Collection"
    ];
    if(galleryImgs.length === 3) {
        galleryImgs.forEach((img, idx) => {
            img.src = gallerySrcs[idx];
            img.style.objectFit = "cover";
        });
    }

    // banner button event
    const bannerBtn = document.querySelector('.banner-btn');
    if(bannerBtn) {
        bannerBtn.addEventListener('click', () => {
            alert("Exclusive pre-order launched! Discover limited Ochre Glaze series.");
        });
    }

    // newsletter
    const subscribeBtn = document.querySelector('.news-form button');
    if(subscribeBtn) {
        subscribeBtn.addEventListener('click', () => {
            const emailInput = document.querySelector('.news-form input');
            if(emailInput && emailInput.value.trim() !== "") {
                alert(`Thanks for subscribing! Your 15% discount code will arrive at ${emailInput.value}`);
                emailInput.value = "";
            } else {
                alert("Please enter a valid email to receive exclusive offers.");
            }
        });
    }

    // primary shop now button
    const shopBtn = document.querySelector('.btn-primary');
    if(shopBtn) {
        shopBtn.addEventListener('click', () => {
            document.querySelector('.featured-grid')?.scrollIntoView({ behavior: 'smooth' });
        });
    }

    renderProducts();