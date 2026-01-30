"""
URL patterns for users app
"""

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('budget/', views.budget_view, name='budget'),
    path('xp/', views.xp_view, name='xp'),
    
    # Card management
    path('cards/<int:card_id>/delete/', views.delete_card, name='delete_card'),
    path('cards/<int:card_id>/default/', views.set_default_card, name='set_default_card'),
    
    # Address management
    path('addresses/<int:address_id>/delete/', views.delete_address, name='delete_address'),
    path('addresses/<int:address_id>/default/', views.set_default_address, name='set_default_address'),
]
