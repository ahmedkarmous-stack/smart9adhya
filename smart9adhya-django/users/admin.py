"""
Admin configuration for Users app
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, PaymentCard, DeliveryAddress


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'monthly_budget', 'current_budget', 'xp_points', 'is_active']
    list_filter = ['is_active', 'is_staff', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone', 'date_of_birth')}),
        ('Budget', {'fields': ('monthly_budget', 'current_budget', 'total_spent', 'budget_month')}),
        ('XP', {'fields': ('xp_points', 'total_xp_earned')}),
        ('Preferences', {'fields': ('preferred_payment', 'email_notifications', 'budget_alerts', 'auto_apply_xp', 'currency')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )


@admin.register(PaymentCard)
class PaymentCardAdmin(admin.ModelAdmin):
    list_display = ['user', 'card_type', 'last_four', 'is_default']
    list_filter = ['card_type', 'is_default']


@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'label', 'city', 'country', 'is_default']
    list_filter = ['label', 'country', 'is_default']
