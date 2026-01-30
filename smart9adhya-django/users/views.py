"""
Views for User Management
Registration, Login, Profile, Settings
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from decimal import Decimal
import json

from .models import User, PaymentCard, DeliveryAddress
from .forms import (
    UserRegistrationForm, UserLoginForm, UserProfileForm,
    PaymentCardForm, DeliveryAddressForm, BudgetForm
)


def register_view(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('products:home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to Smart9adhya, {user.first_name}!')
            return redirect('products:home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('products:home')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Check budget reset
            user.check_budget_reset()
            
            messages.success(request, f'Welcome back, {user.first_name}!')
            
            # Redirect to next page or home
            next_url = request.GET.get('next', 'products:home')
            return redirect(next_url)
    else:
        form = UserLoginForm()
    
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """User logout"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('products:home')


@login_required
def profile_view(request):
    """User profile page"""
    user = request.user
    
    # Get active tab
    active_tab = request.GET.get('tab', 'profile')
    
    # Forms
    profile_form = UserProfileForm(instance=user)
    card_form = PaymentCardForm()
    address_form = DeliveryAddressForm()
    budget_form = BudgetForm(instance=user)
    
    # Handle form submissions
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'profile':
            profile_form = UserProfileForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('users:profile')
        
        elif form_type == 'budget':
            old_budget = user.monthly_budget
            budget_form = BudgetForm(request.POST, instance=user)
            if budget_form.is_valid():
                new_budget = budget_form.cleaned_data['monthly_budget']
                diff = new_budget - old_budget
                user.monthly_budget = new_budget
                user.current_budget = max(Decimal('0'), user.current_budget + diff)
                user.save()
                messages.success(request, 'Budget updated successfully!')
                return redirect('users:profile')
        
        elif form_type == 'card':
            card_form = PaymentCardForm(request.POST)
            if card_form.is_valid():
                card = card_form.save(commit=False)
                card.user = user
                card.save()
                messages.success(request, 'Payment card added!')
                return redirect('users:profile')
        
        elif form_type == 'address':
            address_form = DeliveryAddressForm(request.POST)
            if address_form.is_valid():
                address = address_form.save(commit=False)
                address.user = user
                address.save()
                messages.success(request, 'Address added!')
                return redirect('users:profile')
    
    context = {
        'active_tab': active_tab,
        'profile_form': profile_form,
        'card_form': card_form,
        'address_form': address_form,
        'budget_form': budget_form,
        'payment_cards': user.payment_cards.all(),
        'addresses': user.addresses.all(),
    }
    
    return render(request, 'users/profile.html', context)


@login_required
@require_POST
def delete_card(request, card_id):
    """Delete payment card"""
    card = get_object_or_404(PaymentCard, id=card_id, user=request.user)
    card.delete()
    messages.success(request, 'Card removed.')
    return redirect('users:profile')


@login_required
@require_POST
def set_default_card(request, card_id):
    """Set default payment card"""
    card = get_object_or_404(PaymentCard, id=card_id, user=request.user)
    card.is_default = True
    card.save()
    messages.success(request, 'Default card updated.')
    return redirect('users:profile')


@login_required
@require_POST
def delete_address(request, address_id):
    """Delete delivery address"""
    address = get_object_or_404(DeliveryAddress, id=address_id, user=request.user)
    address.delete()
    messages.success(request, 'Address removed.')
    return redirect('users:profile')


@login_required
@require_POST
def set_default_address(request, address_id):
    """Set default delivery address"""
    address = get_object_or_404(DeliveryAddress, id=address_id, user=request.user)
    address.is_default = True
    address.save()
    messages.success(request, 'Default address updated.')
    return redirect('users:profile')


@login_required
def budget_view(request):
    """Budget management page"""
    user = request.user
    user.check_budget_reset()
    
    context = {
        'monthly_budget': user.monthly_budget,
        'current_budget': user.current_budget,
        'total_spent': user.total_spent,
        'spent_percentage': (user.total_spent / user.monthly_budget * 100) if user.monthly_budget > 0 else 0,
    }
    
    return render(request, 'users/budget.html', context)


@login_required
def xp_view(request):
    """XP points page"""
    user = request.user
    
    context = {
        'xp_points': user.xp_points,
        'total_xp_earned': user.total_xp_earned,
        'xp_value': user.xp_value,
    }
    
    return render(request, 'users/xp.html', context)
