from django.contrib import admin
from .models import Order, OrderItem, Refund

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'total', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    inlines = [OrderItemInline]

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['order', 'reason', 'money_refund', 'status', 'review_start_time']
    list_filter = ['status', 'reason']
