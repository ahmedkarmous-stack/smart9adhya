"""
Order Models for Smart9adhya
"""

from django.db import models
from django.conf import settings
from decimal import Decimal
import uuid


class Order(models.Model):
    """Order model"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHODS = [
        ('card', 'Credit/Debit Card'),
        ('paypal', 'PayPal'),
        ('applepay', 'Apple Pay'),
        ('googlepay', 'Google Pay'),
        ('cod', 'Cash on Delivery'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    order_id = models.CharField(max_length=20, unique=True, editable=False)
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    xp_discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    xp_earned = models.IntegerField(default=0)
    shipping_address = models.JSONField(default=dict)
    
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='card')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    tracking_number = models.CharField(max_length=100, blank=True)
    carrier = models.CharField(max_length=50, blank=True)
    estimated_delivery = models.DateField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    gift_wrap = models.BooleanField(default=False)
    gift_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_id}"
    
    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = f"ORD{uuid.uuid4().hex[:8].upper()}"
        if not self.pk:
            self.xp_earned = self.calculate_xp()
        super().save(*args, **kwargs)
    
    def calculate_xp(self):
        base_xp = int(float(self.subtotal) * 10)
        if float(self.subtotal) >= 500:
            base_xp += 100
        elif float(self.subtotal) >= 100:
            base_xp += 50
        return base_xp
    
    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    product_brand = models.CharField(max_length=100)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_image = models.URLField(max_length=500)
    quantity = models.PositiveIntegerField(default=1)
    
    @property
    def total(self):
        return self.product_price * self.quantity


class Refund(models.Model):
    REASON_CHOICES = [
        ('damaged', 'Product Damaged'),
        ('wrong', 'Wrong Item'),
        ('quality', 'Poor Quality'),
        ('notasexpected', 'Not As Described'),
        ('late', 'Late Delivery'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='refund')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField()
    photos = models.JSONField(default=list, blank=True)
    has_photos = models.BooleanField(default=False)
    money_refund = models.DecimalField(max_digits=10, decimal_places=2)
    bonus_xp = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True)
    review_start_time = models.DateTimeField(auto_now_add=True)
    approval_time = models.DateTimeField(null=True, blank=True)
    
    def approve(self):
        from django.utils import timezone
        self.status = 'approved'
        self.approval_time = timezone.now()
        self.save()
        user = self.order.user
        user.refund_budget(self.money_refund)
        user.add_xp(self.bonus_xp)
