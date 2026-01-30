"""
Custom User Model for Smart9adhya
Includes budget tracking and XP system
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from decimal import Decimal


class UserManager(BaseUserManager):
    """Custom user manager"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model with budget and XP tracking"""
    
    username = None  # Remove username field
    email = models.EmailField('Email Address', unique=True)
    
    # Profile
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Budget System
    monthly_budget = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('2000.00')
    )
    current_budget = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('2000.00')
    )
    total_spent = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    budget_month = models.IntegerField(default=0)
    
    # XP System
    xp_points = models.IntegerField(default=0)
    total_xp_earned = models.IntegerField(default=0)
    
    # Preferences
    preferred_payment = models.CharField(max_length=20, default='card')
    email_notifications = models.BooleanField(default=True)
    budget_alerts = models.BooleanField(default=True)
    auto_apply_xp = models.BooleanField(default=False)
    currency = models.CharField(max_length=3, default='USD')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = UserManager()
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email
    
    @property
    def initials(self):
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        return self.email[:2].upper()
    
    def check_budget_reset(self):
        """Reset budget if it's a new month"""
        current_month = timezone.now().month
        if self.budget_month != current_month:
            self.budget_month = current_month
            self.current_budget = self.monthly_budget
            self.total_spent = Decimal('0.00')
            self.save(update_fields=['budget_month', 'current_budget', 'total_spent'])
            return True
        return False
    
    def spend_budget(self, amount):
        """Deduct amount from budget"""
        amount = Decimal(str(amount))
        self.current_budget -= amount
        self.total_spent += amount
        self.save(update_fields=['current_budget', 'total_spent'])
    
    def refund_budget(self, amount):
        """Add amount back to budget"""
        amount = Decimal(str(amount))
        self.current_budget += amount
        self.total_spent = max(Decimal('0.00'), self.total_spent - amount)
        self.save(update_fields=['current_budget', 'total_spent'])
    
    def add_xp(self, amount):
        """Add XP points"""
        self.xp_points += amount
        self.total_xp_earned += amount
        self.save(update_fields=['xp_points', 'total_xp_earned'])
    
    def use_xp(self, amount):
        """Use XP points as discount"""
        if self.xp_points >= amount:
            self.xp_points -= amount
            self.save(update_fields=['xp_points'])
            return True
        return False
    
    @property
    def xp_value(self):
        """XP value in dollars (100 XP = $1)"""
        return Decimal(self.xp_points) / 100


class PaymentCard(models.Model):
    """User payment cards"""
    
    CARD_TYPES = [
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('amex', 'American Express'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_cards')
    last_four = models.CharField(max_length=4)
    expiry = models.CharField(max_length=5)  # MM/YY
    cardholder_name = models.CharField(max_length=100)
    card_type = models.CharField(max_length=20, choices=CARD_TYPES, default='other')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"•••• {self.last_four}"
    
    def save(self, *args, **kwargs):
        # Ensure only one default card
        if self.is_default:
            PaymentCard.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class DeliveryAddress(models.Model):
    """User delivery addresses"""
    
    LABEL_CHOICES = [
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=10, choices=LABEL_CHOICES, default='home')
    recipient_name = models.CharField(max_length=100)
    street = models.CharField(max_length=200)
    apartment = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=50, default='US')
    phone = models.CharField(max_length=20, blank=True)
    instructions = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
        verbose_name_plural = 'Delivery Addresses'
    
    def __str__(self):
        return f"{self.label.title()}: {self.street}, {self.city}"
    
    def save(self, *args, **kwargs):
        if self.is_default:
            DeliveryAddress.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
