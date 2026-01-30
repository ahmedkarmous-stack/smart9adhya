"""
Forms for User Management
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, PaymentCard, DeliveryAddress


class UserRegistrationForm(UserCreationForm):
    """User registration form"""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address'
        })
    )
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )
    monthly_budget = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        initial=2000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Monthly budget',
            'min': '100'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'monthly_budget', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.current_budget = self.cleaned_data['monthly_budget']
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    """User login form"""
    
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class UserProfileForm(forms.ModelForm):
    """User profile update form"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'date_of_birth']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class BudgetForm(forms.ModelForm):
    """Budget update form"""
    
    class Meta:
        model = User
        fields = ['monthly_budget']
        widgets = {
            'monthly_budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '100',
                'step': '50'
            })
        }


class PaymentCardForm(forms.ModelForm):
    """Payment card form"""
    
    card_number = forms.CharField(
        max_length=19,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1234 5678 9012 3456',
            'maxlength': '19'
        })
    )
    
    class Meta:
        model = PaymentCard
        fields = ['cardholder_name', 'expiry', 'is_default']
        widgets = {
            'cardholder_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name on card'
            }),
            'expiry': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'MM/YY',
                'maxlength': '5'
            }),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_card_number(self):
        number = self.cleaned_data['card_number'].replace(' ', '')
        if len(number) < 13:
            raise forms.ValidationError('Invalid card number')
        return number
    
    def save(self, commit=True):
        card = super().save(commit=False)
        number = self.cleaned_data['card_number']
        card.last_four = number[-4:]
        
        # Detect card type
        first_digit = number[0]
        if first_digit == '4':
            card.card_type = 'visa'
        elif first_digit == '5':
            card.card_type = 'mastercard'
        elif first_digit == '3':
            card.card_type = 'amex'
        else:
            card.card_type = 'other'
        
        if commit:
            card.save()
        return card


class DeliveryAddressForm(forms.ModelForm):
    """Delivery address form"""
    
    class Meta:
        model = DeliveryAddress
        fields = [
            'label', 'recipient_name', 'street', 'apartment',
            'city', 'state', 'zip_code', 'country', 'phone',
            'instructions', 'is_default'
        ]
        widgets = {
            'label': forms.Select(attrs={'class': 'form-select'}),
            'recipient_name': forms.TextInput(attrs={'class': 'form-control'}),
            'street': forms.TextInput(attrs={'class': 'form-control'}),
            'apartment': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('US', 'United States'),
                ('CA', 'Canada'),
                ('UK', 'United Kingdom'),
                ('FR', 'France'),
                ('DE', 'Germany'),
                ('TN', 'Tunisia'),
            ]),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
