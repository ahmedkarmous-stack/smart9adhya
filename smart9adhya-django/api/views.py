from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from products.models import Product
from search.qdrant_service import search_similar, detect_intent
from .serializers import ProductSerializer, UserSerializer

class ProductListAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        qs = Product.objects.filter(is_active=True)
        sector = self.request.query_params.get('sector')
        if sector:
            qs = qs.filter(sector=sector)
        return qs

class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

class SearchAPIView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        sector = request.query_params.get('sector')
        limit = int(request.query_params.get('limit', 20))
        
        budget = None
        if request.user.is_authenticated:
            budget = float(request.user.current_budget)
        
        intents = detect_intent(query)
        results = search_similar(query, limit, budget, sector)
        
        return Response({
            'query': query,
            'intents': intents,
            'count': len(results),
            'results': results
        })

class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class BudgetAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        user.check_budget_reset()
        return Response({
            'monthly_budget': user.monthly_budget,
            'current_budget': user.current_budget,
            'total_spent': user.total_spent,
            'xp_points': user.xp_points
        })
