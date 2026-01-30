/**
 * Smart9adhya Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize toasts
    initToasts();
    
    // Initialize AJAX cart
    initAjaxCart();
    
    // Initialize wishlist
    initWishlist();
    
    // Initialize image search
    initImageSearch();
    
    // Initialize search suggestions
    initSearchSuggestions();
});

/**
 * Initialize Bootstrap toasts
 */
function initToasts() {
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        setTimeout(() => {
            toast.classList.remove('show');
        }, 5000);
    });
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const container = document.querySelector('.toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast show align-items-center text-bg-${type}`;
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1100';
    container.style.marginTop = '70px';
    document.body.appendChild(container);
    return container;
}

/**
 * Initialize AJAX add to cart
 */
function initAjaxCart() {
    document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            
            const url = this.dataset.url;
            const csrf = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrf,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast(data.message, 'success');
                    updateCartCount(data.cart_count);
                }
            })
            .catch(err => {
                console.error('Cart error:', err);
                showToast('Failed to add to cart', 'danger');
            });
        });
    });
}

function updateCartCount(count) {
    const badge = document.querySelector('.cart-count-badge');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'block' : 'none';
    }
}

/**
 * Initialize wishlist toggle
 */
function initWishlist() {
    document.querySelectorAll('.wishlist-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            
            const url = this.dataset.url;
            const csrf = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrf,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast(data.message, 'success');
                    
                    const icon = this.querySelector('i');
                    if (data.added) {
                        icon.classList.remove('bi-heart');
                        icon.classList.add('bi-heart-fill');
                        this.classList.add('active');
                    } else {
                        icon.classList.remove('bi-heart-fill');
                        icon.classList.add('bi-heart');
                        this.classList.remove('active');
                    }
                }
            })
            .catch(err => {
                console.error('Wishlist error:', err);
            });
        });
    });
}

/**
 * Initialize image search
 */
function initImageSearch() {
    const btn = document.getElementById('imageSearchBtn');
    if (!btn) return;
    
    btn.addEventListener('click', function() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        
        input.onchange = function(e) {
            const file = e.target.files[0];
            if (!file) return;
            
            const reader = new FileReader();
            reader.onload = function(event) {
                const imageData = event.target.result;
                performImageSearch(imageData);
            };
            reader.readAsDataURL(file);
        };
        
        input.click();
    });
}

function performImageSearch(imageData) {
    showToast('Analyzing image...', 'info');
    
    const csrf = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    
    fetch('/search/image/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf
        },
        body: JSON.stringify({ image: imageData })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(`Found ${data.results.length} matching products`, 'success');
            // Handle results display
            displayImageSearchResults(data);
        } else {
            showToast(data.error || 'Search failed', 'danger');
        }
    })
    .catch(err => {
        console.error('Image search error:', err);
        showToast('Image search failed', 'danger');
    });
}

function displayImageSearchResults(data) {
    // Redirect to search with results or show modal
    const params = new URLSearchParams({
        q: data.analysis.objects?.join(' ') || '',
        sector: data.analysis.category || ''
    });
    window.location.href = `/search/?${params}`;
}

/**
 * Initialize search suggestions
 */
function initSearchSuggestions() {
    const searchInput = document.querySelector('.nav-search input[name="q"]');
    if (!searchInput) return;
    
    let debounceTimer;
    
    searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        
        const query = this.value.trim();
        if (query.length < 2) {
            hideSuggestions();
            return;
        }
        
        debounceTimer = setTimeout(() => {
            fetchSuggestions(query);
        }, 300);
    });
    
    // Hide on click outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.nav-search')) {
            hideSuggestions();
        }
    });
}

function fetchSuggestions(query) {
    fetch(`/search/suggestions/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            if (data.suggestions && data.suggestions.length > 0) {
                showSuggestions(data.suggestions);
            } else {
                hideSuggestions();
            }
        })
        .catch(err => console.error('Suggestions error:', err));
}

function showSuggestions(suggestions) {
    let dropdown = document.querySelector('.search-suggestions');
    
    if (!dropdown) {
        dropdown = document.createElement('div');
        dropdown.className = 'search-suggestions';
        dropdown.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 10px;
            margin-top: 5px;
            z-index: 1000;
            max-height: 300px;
            overflow-y: auto;
        `;
        document.querySelector('.nav-search').style.position = 'relative';
        document.querySelector('.nav-search').appendChild(dropdown);
    }
    
    dropdown.innerHTML = suggestions.map(s => `
        <a href="/search/?q=${encodeURIComponent(s.text)}" class="d-block px-3 py-2 text-light" style="border-bottom: 1px solid var(--border);">
            <i class="bi bi-${s.type === 'product' ? 'box' : 'tag'} me-2"></i>
            ${s.text}
            ${s.sector ? `<small class="text-muted ms-2">${s.sector}</small>` : ''}
        </a>
    `).join('');
    
    dropdown.style.display = 'block';
}

function hideSuggestions() {
    const dropdown = document.querySelector('.search-suggestions');
    if (dropdown) {
        dropdown.style.display = 'none';
    }
}

/**
 * Format card number input
 */
function formatCardNumber(input) {
    let value = input.value.replace(/\s/g, '').replace(/\D/g, '');
    let formatted = '';
    for (let i = 0; i < value.length && i < 16; i++) {
        if (i > 0 && i % 4 === 0) formatted += ' ';
        formatted += value[i];
    }
    input.value = formatted;
}

/**
 * Format expiry date input
 */
function formatExpiry(input) {
    let value = input.value.replace(/\D/g, '');
    if (value.length >= 2) {
        value = value.slice(0, 2) + '/' + value.slice(2, 4);
    }
    input.value = value;
}
