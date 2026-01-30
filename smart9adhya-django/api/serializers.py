from rest_framework import serializers
from products.models import Product
from users.models import User

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'brand', 'price', 'sector', 'category', 
                  'rating', 'reviews', 'image', 'tags', 'is_featured']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'monthly_budget',
                  'current_budget', 'xp_points', 'total_xp_earned']
        read_only_fields = ['id', 'email']
