"""
Views for Orders App
Checkout, Order History, Refunds
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from decimal import Decimal

from .models import Order, OrderItem, Refund
from products.models import Cart


@login_required
def checkout(request):
    """Checkout page"""
    cart_items = Cart.objects.filter(user=request.user).select_related('product')
    
    if not cart_items:
        messages.warning(request, 'Your cart is empty.')
        return redirect('products:cart')
    
    subtotal = sum(item.total for item in cart_items)
    tax = subtotal * Decimal('0.10')
    total = subtotal + tax
    
    # Check budget
    if total > request.user.current_budget:
        messages.error(request, 'Order exceeds your budget.')
        return redirect('products:cart')
    
    if request.method == 'POST':
        # Get shipping address
        address = request.user.addresses.filter(is_default=True).first()
        if not address:
            messages.error(request, 'Please add a delivery address first.')
            return redirect('users:profile')
        
        shipping_address = {
            'name': address.recipient_name,
            'street': address.street,
            'apartment': address.apartment,
            'city': address.city,
            'state': address.state,
            'zip_code': address.zip_code,
            'country': address.country,
            'phone': address.phone,
        }
        
        # Apply XP discount if requested
        xp_discount = Decimal('0.00')
        if request.POST.get('use_xp') and request.user.xp_points > 0:
            max_xp_discount = min(request.user.xp_value, total * Decimal('0.20'))  # Max 20%
            xp_discount = max_xp_discount
            request.user.use_xp(int(xp_discount * 100))
        
        final_total = total - xp_discount
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            subtotal=subtotal,
            tax=tax,
            xp_discount=xp_discount,
            total=final_total,
            shipping_address=shipping_address,
            payment_method=request.POST.get('payment_method', 'card'),
            payment_status='paid',
            status='confirmed'
        )
        
        # Create order items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                product_brand=cart_item.product.brand,
                product_price=cart_item.product.price,
                product_image=cart_item.product.image,
                quantity=cart_item.quantity
            )
        
        # Update user budget and XP
        request.user.spend_budget(final_total)
        request.user.add_xp(order.xp_earned)
        
        # Clear cart
        cart_items.delete()
        
        messages.success(request, f'Order {order.order_id} placed successfully! You earned {order.xp_earned} XP.')
        return redirect('orders:detail', order_id=order.order_id)
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax': tax,
        'total': total,
        'addresses': request.user.addresses.all(),
        'payment_cards': request.user.payment_cards.all(),
        'xp_available': request.user.xp_points,
        'xp_value': request.user.xp_value,
    }
    
    return render(request, 'orders/checkout.html', context)


@login_required
def order_list(request):
    """Order history"""
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    
    return render(request, 'orders/list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    """Order detail page"""
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    
    return render(request, 'orders/detail.html', {'order': order})


@login_required
def refund_request(request, order_id):
    """Request refund"""
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    
    if hasattr(order, 'refund'):
        messages.warning(request, 'Refund already requested for this order.')
        return redirect('orders:detail', order_id=order_id)
    
    if request.method == 'POST':
        money_refund = order.subtotal
        bonus_xp = int(order.xp_earned * 0.25)
        
        photos = request.POST.getlist('photos', [])
        
        refund = Refund.objects.create(
            order=order,
            reason=request.POST.get('reason'),
            description=request.POST.get('description'),
            photos=photos,
            has_photos=len(photos) > 0,
            money_refund=money_refund,
            bonus_xp=bonus_xp,
        )
        
        messages.success(request, 'Refund request submitted. Review time: 2-5 minutes.')
        return redirect('orders:detail', order_id=order_id)
    
    return render(request, 'orders/refund.html', {'order': order})


@login_required
def refund_list(request):
    """List all refund requests"""
    refunds = Refund.objects.filter(order__user=request.user).select_related('order')
    
    return render(request, 'orders/refunds.html', {'refunds': refunds})
