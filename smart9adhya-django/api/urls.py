from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

app_name = 'api'

urlpatterns = [
    # Auth
    path('token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Products
    path('products/', views.ProductListAPIView.as_view(), name='products'),
    path('products/<int:pk>/', views.ProductDetailAPIView.as_view(), name='product_detail'),
    
    # Search
    path('search/', views.SearchAPIView.as_view(), name='search'),
    
    # User
    path('user/profile/', views.UserProfileAPIView.as_view(), name='profile'),
    path('user/budget/', views.BudgetAPIView.as_view(), name='budget'),
]
