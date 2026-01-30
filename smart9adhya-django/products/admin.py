"""
Admin configuration for Products app
"""

from django.contrib import admin
from .models import Product, Cart, Wishlist


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'sector', 'price', 'rating', 'reviews', 'stock', 'is_active', 'is_featured', 'qdrant_indexed']
    list_filter = ['sector', 'is_active', 'is_featured', 'qdrant_indexed']
    search_fields = ['name', 'brand', 'category']
    list_editable = ['is_active', 'is_featured']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('name', 'brand', 'description')}),
        ('Pricing', {'fields': ('price', 'original_price', 'discount')}),
        ('Categorization', {'fields': ('sector', 'category', 'subcategory', 'tags')}),
        ('Media', {'fields': ('image', 'images')}),
        ('Stats', {'fields': ('rating', 'reviews', 'stock')}),
        ('Attributes', {'fields': ('attributes',)}),
        ('Status', {'fields': ('is_active', 'is_featured', 'qdrant_indexed', 'qdrant_indexed_at')}),
    )
    
    actions = ['index_in_qdrant']
    
    def index_in_qdrant(self, request, queryset):
        from search.qdrant_service import index_products
        result = index_products(queryset)
        self.message_user(request, f"Indexed {result['indexed']} products, {result['failed']} failed")
    
    index_in_qdrant.short_description = "Index selected products in Qdrant"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity', 'added_at']
    list_filter = ['added_at']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'added_at']
    list_filter = ['added_at']