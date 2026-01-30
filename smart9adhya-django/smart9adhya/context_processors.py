"""
Context Processors for Smart9adhya
Add global context to all templates
"""

from products.models import Cart


def cart_context(request):
    """Add cart information to all templates"""
    cart_count = 0
    cart_total = 0
    
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        cart_count = sum(item.quantity for item in cart_items)
        cart_total = sum(item.product.price * item.quantity for item in cart_items)
    else:
        # Handle session-based cart for anonymous users
        cart = request.session.get('cart', {})
        cart_count = sum(cart.values())
    
    return {
        'cart_count': cart_count,
        'cart_total': cart_total,
    }


def user_context(request):
    """Add user-specific information to all templates"""
    context = {
        'user_budget': 0,
        'user_xp': 0,
    }
    
    if request.user.is_authenticated:
        # Check and reset budget if new month
        request.user.check_budget_reset()
        
        context['user_budget'] = request.user.current_budget
        context['user_xp'] = request.user.xp_points
        context['user_initials'] = request.user.initials
    
    return context
