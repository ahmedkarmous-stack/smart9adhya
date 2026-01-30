"""
Views for Products App
Home, Shop, Product Detail, Cart
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.core.paginator import Paginator
import json

from .models import Product, Cart, Wishlist


def home(request):
    """Home page with featured and trending products"""
    
    # Get user budget for filtering
    budget_filter = None
    if request.user.is_authenticated:
        budget_filter = request.user.current_budget
    
    # Featured products
    featured_qs = Product.objects.filter(is_active=True, is_featured=True)
    if budget_filter:
        featured_qs = featured_qs.filter(price__lte=budget_filter)
    featured = featured_qs.order_by('-rating')[:8]
    
    # Trending products (by reviews)
    trending_qs = Product.objects.filter(is_active=True)
    if budget_filter:
        trending_qs = trending_qs.filter(price__lte=budget_filter)
    trending = trending_qs.order_by('-reviews', '-rating')[:8]
    
    # Sectors with counts
    sectors = []
    for sector, label in Product.SECTOR_CHOICES:
        count = Product.objects.filter(is_active=True, sector=sector).count()
        sectors.append({'name': sector, 'label': label, 'count': count})
    
    context = {
        'featured_products': featured,
        'trending_products': trending,
        'sectors': sectors,
    }
    
    return render(request, 'products/home.html', context)


def shop(request, sector=None):
    """Shop page with filters"""
    
    products = Product.objects.filter(is_active=True)
    
    # Sector filter
    if sector:
        products = products.filter(sector=sector)
    elif request.GET.get('sector'):
        products = products.filter(sector=request.GET.get('sector'))
    
    # Category filter
    category = request.GET.get('category')
    if category:
        products = products.filter(category=category)
    
    # Brand filter
    brand = request.GET.get('brand')
    if brand:
        products = products.filter(brand=brand)
    
    # Price filters
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Budget filter (for authenticated users)
    if request.user.is_authenticated:
        if request.GET.get('budget_filter', 'true') == 'true':
            products = products.filter(price__lte=request.user.current_budget)
    
    # Rating filter
    min_rating = request.GET.get('min_rating')
    if min_rating:
        products = products.filter(rating__gte=min_rating)
    
    # Sorting
    sort = request.GET.get('sort', '-rating')
    valid_sorts = ['-rating', 'rating', '-price', 'price', '-reviews', '-created_at']
    if sort in valid_sorts:
        products = products.order_by(sort)
    
    # Pagination
    paginator = Paginator(products, 24)
    page = request.GET.get('page', 1)
    products_page = paginator.get_page(page)
    
    # Get filter options
    all_brands = Product.objects.filter(is_active=True).values_list('brand', flat=True).distinct()
    all_categories = Product.objects.filter(is_active=True).values_list('category', flat=True).distinct()
    
    context = {
        'products': products_page,
        'current_sector': sector,
        'sectors': Product.SECTOR_CHOICES,
        'brands': sorted(set(all_brands)),
        'categories': sorted(set(all_categories)),
        'current_filters': {
            'sector': sector or request.GET.get('sector', ''),
            'category': category or '',
            'brand': brand or '',
            'min_price': min_price or '',
            'max_price': max_price or '',
            'min_rating': min_rating or '',
            'sort': sort,
        }
    }
    
    return render(request, 'products/shop.html', context)


def product_detail(request, product_id):
    """Product detail page"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Related products (same sector)
    related = Product.objects.filter(
        is_active=True,
        sector=product.sector
    ).exclude(id=product.id).order_by('-rating')[:4]
    
    # Check if in wishlist
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
    
    context = {
        'product': product,
        'related_products': related,
        'in_wishlist': in_wishlist,
    }
    
    return render(request, 'products/detail.html', context)


# ============================================
# CART VIEWS
# ============================================

@login_required
def cart_view(request):
    """Shopping cart page"""
    cart_items = Cart.objects.filter(user=request.user).select_related('product')
    
    subtotal = sum(item.total for item in cart_items)
    tax = subtotal * 0.1  # 10% tax
    total = subtotal + tax
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax': tax,
        'total': total,
    }
    
    return render(request, 'products/cart.html', context)


@login_required
@require_POST
def add_to_cart(request, product_id):
    """Add product to cart"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1))
    
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_count = sum(item.quantity for item in Cart.objects.filter(user=request.user))
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to cart',
            'cart_count': cart_count
        })
    
    messages.success(request, f'{product.name} added to cart!')
    return redirect(request.META.get('HTTP_REFERER', 'products:cart'))


@login_required
@require_POST
def update_cart(request, item_id):
    """Update cart item quantity"""
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        cart_item.delete()
        messages.info(request, 'Item removed from cart.')
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, 'Cart updated.')
    
    return redirect('products:cart')


@login_required
@require_POST
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': f'{product_name} removed'})
    
    messages.info(request, f'{product_name} removed from cart.')
    return redirect('products:cart')


# ============================================
# WISHLIST VIEWS
# ============================================

@login_required
def wishlist_view(request):
    """Wishlist page"""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    
    return render(request, 'products/wishlist.html', {
        'wishlist_items': wishlist_items
    })


@login_required
@require_POST
def toggle_wishlist(request, product_id):
    """Toggle product in wishlist"""
    product = get_object_or_404(Product, id=product_id)
    
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product).first()
    
    if wishlist_item:
        wishlist_item.delete()
        added = False
        message = f'{product.name} removed from wishlist'
    else:
        Wishlist.objects.create(user=request.user, product=product)
        added = True
        message = f'{product.name} added to wishlist'
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'added': added, 'message': message})
    
    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'products:wishlist'))
