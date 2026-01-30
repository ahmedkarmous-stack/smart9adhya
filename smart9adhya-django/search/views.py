"""
Views for Search App
RAG-based semantic search and image search
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q
import json
import base64

from products.models import Product
from .qdrant_service import search_similar, detect_intent, get_collection_stats


def search_view(request):
    """Main search page"""
    query = request.GET.get('q', '').strip()
    sector = request.GET.get('sector', '')
    
    results = []
    intents = []
    qdrant_used = False
    
    if query:
        # Get user budget
        budget = None
        if request.user.is_authenticated:
            budget = float(request.user.current_budget)
        
        # Detect intents
        intents = detect_intent(query)
        
        # Try Qdrant search first
        qdrant_results = search_similar(
            query=query,
            limit=24,
            budget=budget,
            sector=sector if sector else None
        )
        
        if qdrant_results:
            qdrant_used = True
            # Get full product objects
            product_ids = [r['product_id'] for r in qdrant_results]
            products_map = {p.id: p for p in Product.objects.filter(id__in=product_ids)}
            
            for qr in qdrant_results:
                product = products_map.get(qr['product_id'])
                if product:
                    results.append({
                        'product': product,
                        'score': qr['score'],
                        'rank': qr['rank'],
                        'match_percentage': qr['match_percentage'],
                        'explanation': generate_explanation(product, query, intents)
                    })
        else:
            # Fallback to Django ORM search
            products = Product.objects.filter(is_active=True)
            
            # Text search
            products = products.filter(
                Q(name__icontains=query) |
                Q(brand__icontains=query) |
                Q(category__icontains=query) |
                Q(tags__icontains=query)
            )
            
            # Apply budget filter
            if budget:
                products = products.filter(price__lte=budget)
            
            # Apply sector filter
            if sector:
                products = products.filter(sector=sector)
            
            products = products.order_by('-rating')[:24]
            
            for i, product in enumerate(products):
                results.append({
                    'product': product,
                    'score': 0.8 - (i * 0.02),
                    'rank': i + 1,
                    'match_percentage': 80 - (i * 2),
                    'explanation': generate_explanation(product, query, intents)
                })
    
    context = {
        'query': query,
        'results': results,
        'intents': intents,
        'sectors': Product.SECTOR_CHOICES,
        'current_sector': sector,
        'qdrant_used': qdrant_used,
        'result_count': len(results),
    }
    
    return render(request, 'search/results.html', context)


def generate_explanation(product, query, intents):
    """Generate explanation for why product matches"""
    explanations = []
    query_lower = query.lower()
    name_lower = product.name.lower()
    brand_lower = product.brand.lower()
    
    # Name match
    query_words = query_lower.split()
    if any(word in name_lower for word in query_words):
        explanations.append({'icon': '🎯', 'text': 'Name matches your search', 'weight': 'high'})
    
    # Brand match
    if brand_lower in query_lower or query_lower in brand_lower:
        explanations.append({'icon': '🏷️', 'text': f'Brand: {product.brand}', 'weight': 'high'})
    
    # Category match
    if product.sector.lower() in query_lower:
        explanations.append({'icon': '📦', 'text': f'Category: {product.sector}', 'weight': 'medium'})
    
    # Intent-based explanations
    if 'budget' in intents and float(product.price) < 50:
        explanations.append({'icon': '💰', 'text': 'Budget-friendly option', 'weight': 'medium'})
    
    if 'premium' in intents and float(product.rating) >= 4.5:
        explanations.append({'icon': '⭐', 'text': f'High rated: {product.rating}/5', 'weight': 'medium'})
    
    if 'trending' in intents and product.reviews > 100:
        explanations.append({'icon': '🔥', 'text': f'Popular: {product.reviews} reviews', 'weight': 'low'})
    
    if not explanations:
        explanations.append({'icon': '✨', 'text': 'Relevant to your search', 'weight': 'low'})
    
    return explanations


@require_POST
def image_search(request):
    """Handle image-based search"""
    try:
        data = json.loads(request.body)
        image_data = data.get('image')
        
        if not image_data:
            return JsonResponse({'error': 'No image provided'}, status=400)
        
        # Analyze image (placeholder - integrate with vision API)
        analysis = analyze_image(image_data)
        
        # Search based on analysis
        budget = None
        if request.user.is_authenticated:
            budget = float(request.user.current_budget)
        
        search_query = ' '.join([
            analysis.get('category', ''),
            ' '.join(analysis.get('colors', [])),
            ' '.join(analysis.get('objects', []))
        ])
        
        results = search_similar(
            query=search_query,
            limit=20,
            budget=budget,
            sector=analysis.get('category')
        )
        
        return JsonResponse({
            'success': True,
            'analysis': analysis,
            'results': results
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def analyze_image(image_data):
    """Analyze image and extract features (placeholder)"""
    # In production, integrate with:
    # - TensorFlow/PyTorch for local inference
    # - OpenAI Vision API
    # - Google Cloud Vision
    # - Amazon Rekognition
    
    return {
        'category': 'Fashion',
        'confidence': 0.75,
        'colors': ['blue', 'white'],
        'objects': ['clothing', 'shirt'],
        'style': ['casual']
    }


def suggestions(request):
    """Get search suggestions"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    # Product name suggestions
    products = Product.objects.filter(
        is_active=True,
        name__icontains=query
    ).values('name', 'brand', 'sector')[:10]
    
    # Brand suggestions
    brands = Product.objects.filter(
        is_active=True,
        brand__icontains=query
    ).values_list('brand', flat=True).distinct()[:5]
    
    suggestions = []
    
    for p in products:
        suggestions.append({
            'type': 'product',
            'text': p['name'],
            'sector': p['sector']
        })
    
    for brand in brands:
        suggestions.append({
            'type': 'brand',
            'text': brand
        })
    
    return JsonResponse({'suggestions': suggestions[:15]})


def stats_view(request):
    """View Qdrant collection stats (admin only)"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    stats = get_collection_stats()
    return JsonResponse({'stats': stats})
