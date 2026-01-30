"""
URL patterns for products app
"""

from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('shop/<str:sector>/', views.shop, name='shop_sector'),
    path('product/<int:product_id>/', views.product_detail, name='detail'),
    
    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
]
