"""
Product Models for Smart9adhya
"""

from django.db import models
from django.conf import settings
from decimal import Decimal


class Product(models.Model):
    """Product model"""
    
    SECTOR_CHOICES = [
        ('Fashion', 'Fashion'),
        ('Electronics', 'Electronics'),
        ('Furniture', 'Furniture'),
        ('Food', 'Food & Beverages'),
        ('Healthcare', 'Healthcare'),
        ('Sports', 'Sports & Fitness'),
        ('Wine', 'Wine & Spirits'),
    ]
    
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    sector = models.CharField(max_length=50, choices=SECTOR_CHOICES)
    category = models.CharField(max_length=100)
    subcategory = models.CharField(max_length=100, blank=True)
    
    image = models.URLField(max_length=500)
    images = models.JSONField(default=list, blank=True)
    
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=Decimal('0.0'))
    reviews = models.IntegerField(default=0)
    stock = models.IntegerField(default=100)
    
    tags = models.JSONField(default=list, blank=True)
    attributes = models.JSONField(default=dict, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    discount = models.IntegerField(default=0)  # Percentage
    
    # Qdrant sync status
    qdrant_indexed = models.BooleanField(default=False)
    qdrant_indexed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-rating', '-reviews']
        indexes = [
            models.Index(fields=['sector', 'price']),
            models.Index(fields=['brand']),
            models.Index(fields=['is_active', 'sector']),
        ]
    
    def __str__(self):
        return f"{self.brand} - {self.name}"
    
    @property
    def discounted_price(self):
        if self.discount > 0:
            return self.price * (1 - Decimal(self.discount) / 100)
        return self.price
    
    @property
    def in_stock(self):
        return self.stock > 0
    
    @property
    def price_range(self):
        """Get price range category"""
        price = float(self.price)
        if price < 25:
            return 'budget'
        elif price < 100:
            return 'mid-range'
        elif price < 500:
            return 'premium'
        else:
            return 'luxury'


class Cart(models.Model):
    """Shopping cart item"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.product.name} x{self.quantity}"
    
    @property
    def total(self):
        return self.product.price * self.quantity


class Wishlist(models.Model):
    """User wishlist"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wishlist_items'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.product.name}"
