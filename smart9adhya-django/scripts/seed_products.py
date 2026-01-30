#!/usr/bin/env python
"""
Smart9adhya - Product Seeding Script
=====================================
This script seeds the database with sample products and indexes them in Qdrant.

Usage:
    python scripts/seed_products.py           # Add products
    python scripts/seed_products.py --fresh   # Clear and re-add all products

Run from project root:
    python scripts/seed_products.py
"""

import os
import sys
import django

# Setup Django environment
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart9adhya.settings')
django.setup()

from decimal import Decimal
from products.models import Product
from search.qdrant_service import init_qdrant_collection, index_products, get_collection_stats

# ============================================
# PRODUCT DATA - 30 Products across 7 sectors
# ============================================

PRODUCTS = [
    # ==================== FASHION (5) ====================
    {
        "name": "Classic Cotton T-Shirt",
        "brand": "Nike",
        "description": "Premium cotton t-shirt with a relaxed fit. Perfect for everyday casual wear.",
        "price": Decimal("29.99"),
        "sector": "Fashion",
        "category": "T-Shirts",
        "rating": Decimal("4.5"),
        "reviews": 234,
        "stock": 150,
        "image": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400",
        "tags": ["casual", "cotton", "summer", "comfortable"],
        "is_featured": True,
        "discount": 0
    },
    {
        "name": "Slim Fit Jeans",
        "brand": "Levi's",
        "description": "Classic slim fit jeans made from premium denim. Timeless style for any occasion.",
        "price": Decimal("79.99"),
        "sector": "Fashion",
        "category": "Jeans",
        "rating": Decimal("4.7"),
        "reviews": 567,
        "stock": 200,
        "image": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400",
        "tags": ["denim", "slim", "classic", "blue"],
        "is_featured": False,
        "discount": 10
    },
    {
        "name": "Running Sneakers Pro",
        "brand": "Adidas",
        "description": "High-performance running shoes with advanced cushioning technology.",
        "price": Decimal("129.99"),
        "sector": "Fashion",
        "category": "Shoes",
        "rating": Decimal("4.8"),
        "reviews": 890,
        "stock": 100,
        "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400",
        "tags": ["running", "sports", "comfort", "athletic"],
        "is_featured": True,
        "discount": 0
    },
    {
        "name": "Leather Jacket Premium",
        "brand": "Zara",
        "description": "Genuine leather jacket with a modern cut. Perfect for fall and winter.",
        "price": Decimal("199.99"),
        "sector": "Fashion",
        "category": "Jackets",
        "rating": Decimal("4.6"),
        "reviews": 345,
        "stock": 50,
        "image": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400",
        "tags": ["leather", "premium", "winter", "black"],
        "is_featured": False,
        "discount": 15
    },
    {
        "name": "Summer Floral Dress",
        "brand": "H&M",
        "description": "Light and breezy summer dress with beautiful floral pattern.",
        "price": Decimal("49.99"),
        "sector": "Fashion",
        "category": "Dresses",
        "rating": Decimal("4.4"),
        "reviews": 456,
        "stock": 120,
        "image": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400",
        "tags": ["summer", "casual", "floral", "light"],
        "is_featured": False,
        "discount": 0
    },
    
    # ==================== ELECTRONICS (5) ====================
    {
        "name": "Wireless Bluetooth Headphones",
        "brand": "Sony",
        "description": "Premium noise-cancelling headphones with 30-hour battery life.",
        "price": Decimal("199.99"),
        "sector": "Electronics",
        "category": "Audio",
        "rating": Decimal("4.6"),
        "reviews": 1234,
        "stock": 80,
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
        "tags": ["wireless", "bluetooth", "noise-cancelling", "premium"],
        "is_featured": True,
        "discount": 0
    },
    {
        "name": "Smart Watch Pro Max",
        "brand": "Apple",
        "description": "Advanced smartwatch with health monitoring, GPS, and cellular connectivity.",
        "price": Decimal("399.99"),
        "sector": "Electronics",
        "category": "Wearables",
        "rating": Decimal("4.9"),
        "reviews": 2345,
        "stock": 60,
        "image": "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=400",
        "tags": ["smart", "fitness", "health", "gps", "premium"],
        "is_featured": True,
        "discount": 0
    },
    {
        "name": "4K Ultra HD Smart TV 55\"",
        "brand": "Samsung",
        "description": "Crystal clear 4K display with smart TV features and voice control.",
        "price": Decimal("699.99"),
        "sector": "Electronics",
        "category": "TVs",
        "rating": Decimal("4.7"),
        "reviews": 876,
        "stock": 30,
        "image": "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=400",
        "tags": ["4k", "smart-tv", "streaming", "large"],
        "is_featured": False,
        "discount": 10
    },
    {
        "name": "Wireless Earbuds Pro",
        "brand": "Apple",
        "description": "True wireless earbuds with spatial audio and active noise cancellation.",
        "price": Decimal("249.99"),
        "sector": "Electronics",
        "category": "Audio",
        "rating": Decimal("4.8"),
        "reviews": 3456,
        "stock": 150,
        "image": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400",
        "tags": ["wireless", "earbuds", "premium", "portable"],
        "is_featured": True,
        "discount": 0
    },
    {
        "name": "Gaming Laptop RTX",
        "brand": "ASUS",
        "description": "High-performance gaming laptop with RTX graphics and 144Hz display.",
        "price": Decimal("1299.99"),
        "sector": "Electronics",
        "category": "Computers",
        "rating": Decimal("4.7"),
        "reviews": 678,
        "stock": 25,
        "image": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400",
        "tags": ["gaming", "laptop", "performance", "rtx"],
        "is_featured": False,
        "discount": 5
    },
    
    # ==================== FURNITURE (4) ====================
    {
        "name": "Modern Sofa Set 3-Seater",
        "brand": "IKEA",
        "description": "Contemporary 3-seater sofa with premium fabric and comfortable cushions.",
        "price": Decimal("899.99"),
        "sector": "Furniture",
        "category": "Living Room",
        "rating": Decimal("4.4"),
        "reviews": 345,
        "stock": 20,
        "image": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400",
        "tags": ["modern", "comfortable", "fabric", "living-room"],
        "is_featured": False,
        "discount": 0
    },
    {
        "name": "Ergonomic Office Chair Pro",
        "brand": "Herman Miller",
        "description": "Premium ergonomic chair with lumbar support and adjustable armrests.",
        "price": Decimal("499.99"),
        "sector": "Furniture",
        "category": "Office",
        "rating": Decimal("4.8"),
        "reviews": 678,
        "stock": 40,
        "image": "https://images.unsplash.com/photo-1580480055273-228ff5388ef8?w=400",
        "tags": ["ergonomic", "office", "adjustable", "premium"],
        "is_featured": True,
        "discount": 0
    },
    {
        "name": "Queen Size Bed Frame",
        "brand": "West Elm",
        "description": "Elegant queen size bed frame made from solid wood.",
        "price": Decimal("799.99"),
        "sector": "Furniture",
        "category": "Bedroom",
        "rating": Decimal("4.5"),
        "reviews": 234,
        "stock": 15,
        "image": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=400",
        "tags": ["bedroom", "wood", "modern", "queen"],
        "is_featured": False,
        "discount": 10
    },
    {
        "name": "Dining Table Set 6-Person",
        "brand": "IKEA",
        "description": "Complete dining set with table and 6 chairs. Perfect for family meals.",
        "price": Decimal("599.99"),
        "sector": "Furniture",
        "category": "Dining",
        "rating": Decimal("4.3"),
        "reviews": 189,
        "stock": 18,
        "image": "https://images.unsplash.com/photo-1617806118233-18e1de247200?w=400",
        "tags": ["dining", "wood", "family", "set"],
        "is_featured": False,
        "discount": 0
    },
    
    # ==================== FOOD & BEVERAGES (4) ====================
    {
        "name": "Organic Coffee Beans Premium",
        "brand": "Starbucks",
        "description": "100% Arabica organic coffee beans. Rich and smooth flavor profile.",
        "price": Decimal("14.99"),
        "sector": "Food",
        "category": "Beverages",
        "rating": Decimal("4.5"),
        "reviews": 456,
        "stock": 300,
        "image": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=400",
        "tags": ["organic", "arabica", "premium", "coffee"],
        "is_featured": False,
        "discount": 0
    },
    {
        "name": "Protein Bar Variety Pack",
        "brand": "Quest",
        "description": "20g protein per bar. Pack of 12 with assorted flavors.",
        "price": Decimal("24.99"),
        "sector": "Food",
        "category": "Snacks",
        "rating": Decimal("4.3"),
        "reviews": 789,
        "stock": 200,
        "image": "https://images.unsplash.com/photo-1622484211148-4e7a14c5f4c5?w=400",
        "tags": ["protein", "healthy", "fitness", "snack"],
        "is_featured": False,
        "discount": 15
    },
    {
        "name": "Extra Virgin Olive Oil",
        "brand": "Bertolli",
        "description": "Premium Italian extra virgin olive oil. Cold-pressed for maximum flavor.",
        "price": Decimal("12.99"),
        "sector": "Food",
        "category": "Cooking",
        "rating": Decimal("4.6"),
        "reviews": 567,
        "stock": 250,
        "image": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400",
        "tags": ["organic", "cooking", "italian", "healthy"],
        "is_featured": False,
        "discount": 0
    },
    {
        "name": "Organic Green Tea Collection",
        "brand": "Twinings",
        "description": "Assorted organic green tea bags. 50 count variety pack.",
        "price": Decimal("8.99"),
        "sector": "Food",
        "category": "Beverages",
        "rating": Decimal("4.4"),
        "reviews": 345,
        "stock": 400,
        "image": "https://images.unsplash.com/photo-1556881286-fc6915169721?w=400",
        "tags": ["organic", "tea", "healthy", "green"],
        "is_featured": False,
        "discount": 0
    },
    
    # ==================== HEALTHCARE (4) ====================
    {
        "name": "Vitamin D3 5000 IU",
        "brand": "Nature Made",
        "description": "High potency Vitamin D3 supplements. 180 softgels per bottle.",
        "price": Decimal("19.99"),
        "sector": "Healthcare",
        "category": "Vitamins",
        "rating": Decimal("4.6"),
        "reviews": 1234,
        "stock": 300,
        "image": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400",
        "tags": ["vitamins", "health", "immune", "supplements"],
        "is_featured": False,
        "discount": 0
    },
    {
        "name": "Face Moisturizer Daily",
        "brand": "CeraVe",
        "description": "Hydrating facial moisturizer with hyaluronic acid. For all skin types.",
        "price": Decimal("16.99"),
        "sector": "Healthcare",
        "category": "Skincare",
        "rating": Decimal("4.7"),
        "reviews": 2345,
        "stock": 180,
        "image": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400",
        "tags": ["skincare", "hydrating", "daily", "moisturizer"],
        "is_featured": True,
        "discount": 0
    },
    {
        "name": "Electric Toothbrush Smart",
        "brand": "Oral-B",
        "description": "Smart electric toothbrush with pressure sensor and Bluetooth connectivity.",
        "price": Decimal("89.99"),
        "sector": "Healthcare",
        "category": "Dental",
        "rating": Decimal("4.5"),
        "reviews": 876,
        "stock": 90,
        "image": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=400",
        "tags": ["dental", "electric", "smart", "oral-care"],
        "is_featured": False,
        "discount": 10
    },
    {
        "name": "Multivitamin Gummies Adults",
        "brand": "Vitafusion",
        "description": "Complete daily multivitamin in delicious gummy form. 150 count.",
        "price": Decimal("14.99"),
        "sector": "Healthcare",
        "category": "Vitamins",
        "rating": Decimal("4.4"),
        "reviews": 678,
        "stock": 250,
        "image": "https://images.unsplash.com/photo-1550572017-edd951aa8f72?w=400",
        "tags": ["vitamins", "gummies", "daily", "wellness"],
        "is_featured": False,
        "discount": 0
    },
    
    # ==================== SPORTS & FITNESS (4) ====================
    {
        "name": "Yoga Mat Premium Non-Slip",
        "brand": "Lululemon",
        "description": "Professional-grade yoga mat with superior grip and cushioning.",
        "price": Decimal("78.99"),
        "sector": "Sports",
        "category": "Yoga",
        "rating": Decimal("4.8"),
        "reviews": 567,
        "stock": 120,
        "image": "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=400",
        "tags": ["yoga", "fitness", "non-slip", "premium"],
        "is_featured": True,
        "discount": 0
    },
    {
        "name": "Adjustable Dumbbells Set",
        "brand": "Bowflex",
        "description": "Space-saving adjustable dumbbells. 5-52.5 lbs per dumbbell.",
        "price": Decimal("349.99"),
        "sector": "Sports",
        "category": "Weights",
        "rating": Decimal("4.7"),
        "reviews": 890,
        "stock": 35,
        "image": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=400",
        "tags": ["weights", "home-gym", "adjustable", "strength"],
        "is_featured": False,
        "discount": 0
    },
    {
        "name": "Running Shoes Ultra Light",
        "brand": "Nike",
        "description": "Ultra lightweight running shoes for maximum speed and comfort.",
        "price": Decimal("159.99"),
        "sector": "Sports",
        "category": "Footwear",
        "rating": Decimal("4.6"),
        "reviews": 1234,
        "stock": 80,
        "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400",
        "tags": ["running", "performance", "comfort", "lightweight"],
        "is_featured": False,
        "discount": 5
    },
    {
        "name": "Resistance Bands Set Pro",
        "brand": "TheraBand",
        "description": "Professional resistance bands set with 5 different strength levels.",
        "price": Decimal("29.99"),
        "sector": "Sports",
        "category": "Accessories",
        "rating": Decimal("4.5"),
        "reviews": 456,
        "stock": 200,
        "image": "https://images.unsplash.com/photo-1598289431512-b97b0917affc?w=400",
        "tags": ["resistance", "workout", "portable", "fitness"],
        "is_featured": False,
        "discount": 0
    },
    
    # ==================== WINE & SPIRITS (4) ====================
    {
        "name": "Cabernet Sauvignon Reserve",
        "brand": "Robert Mondavi",
        "description": "Full-bodied Napa Valley Cabernet with rich tannins and dark fruit notes.",
        "price": Decimal("45.99"),
        "sector": "Wine",
        "category": "Red Wine",
        "rating": Decimal("4.6"),
        "reviews": 234,
        "stock": 60,
        "image": "https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=400",
        "tags": ["red", "cabernet", "reserve", "napa"],
        "is_featured": False,
        "discount": 0
    },
    {
        "name": "Champagne Brut Imperial",
        "brand": "Moët & Chandon",
        "description": "Prestigious champagne with fine bubbles and elegant flavor profile.",
        "price": Decimal("59.99"),
        "sector": "Wine",
        "category": "Champagne",
        "rating": Decimal("4.8"),
        "reviews": 456,
        "stock": 40,
        "image": "https://images.unsplash.com/photo-1594372365401-3b5ff14eaaed?w=400",
        "tags": ["champagne", "brut", "celebration", "premium"],
        "is_featured": True,
        "discount": 0
    },
    {
        "name": "Pinot Grigio Classic",
        "brand": "Santa Margherita",
        "description": "Crisp and refreshing Italian Pinot Grigio. Perfect for summer.",
        "price": Decimal("24.99"),
        "sector": "Wine",
        "category": "White Wine",
        "rating": Decimal("4.5"),
        "reviews": 345,
        "stock": 80,
        "image": "https://images.unsplash.com/photo-1558001373-7b93ee48ffa0?w=400",
        "tags": ["white", "italian", "crisp", "refreshing"],
        "is_featured": False,
        "discount": 10
    },
    {
        "name": "Rosé Wine Premium",
        "brand": "Whispering Angel",
        "description": "Elegant Provence rosé with delicate flavors and beautiful pale color.",
        "price": Decimal("29.99"),
        "sector": "Wine",
        "category": "Rosé",
        "rating": Decimal("4.4"),
        "reviews": 567,
        "stock": 70,
        "image": "https://images.unsplash.com/photo-1558001373-7b93ee48ffa0?w=400",
        "tags": ["rosé", "french", "summer", "elegant"],
        "is_featured": False,
        "discount": 0
    },
]


def seed_products(fresh=False):
    """
    Seed products into the database and Qdrant
    
    Args:
        fresh: If True, delete all existing products first
    """
    print("=" * 60)
    print("🔥 Smart9adhya Product Seeding Script")
    print("=" * 60)
    
    # Clear existing products if --fresh flag
    if fresh:
        print("\n🗑️  Clearing existing products...")
        count = Product.objects.all().delete()[0]
        print(f"   Deleted {count} products")
    
    # Create products
    print(f"\n📦 Creating {len(PRODUCTS)} products...")
    created_count = 0
    updated_count = 0
    
    for i, data in enumerate(PRODUCTS, 1):
        product, created = Product.objects.update_or_create(
            name=data['name'],
            brand=data['brand'],
            defaults={
                'description': data.get('description', ''),
                'price': data['price'],
                'sector': data['sector'],
                'category': data['category'],
                'rating': data.get('rating', Decimal('4.0')),
                'reviews': data.get('reviews', 0),
                'stock': data.get('stock', 100),
                'image': data['image'],
                'tags': data.get('tags', []),
                'is_active': True,
                'is_featured': data.get('is_featured', False),
                'discount': data.get('discount', 0),
            }
        )
        
        if created:
            created_count += 1
            status = "✅ Created"
        else:
            updated_count += 1
            status = "🔄 Updated"
        
        print(f"   [{i:02d}/{len(PRODUCTS)}] {status}: {product.name[:40]}")
    
    print(f"\n   📊 Summary: {created_count} created, {updated_count} updated")
    
    # Initialize and index in Qdrant
    print("\n🔍 Initializing Qdrant...")
    
    if init_qdrant_collection():
        print("   ✅ Qdrant collection ready")
        
        print("\n📡 Indexing products in Qdrant...")
        products = Product.objects.filter(is_active=True)
        result = index_products(products)
        
        print(f"   ✅ Indexed: {result['indexed']} products")
        if result['failed'] > 0:
            print(f"   ⚠️  Failed: {result['failed']} products")
        
        # Show stats
        stats = get_collection_stats()
        if stats:
            print(f"\n   📊 Qdrant Stats:")
            print(f"      - Points: {stats.get('points_count', 'N/A')}")
            print(f"      - Status: {stats.get('status', 'N/A')}")
    else:
        print("   ⚠️  Qdrant not available - skipping indexing")
        print("   💡 Tip: Start Qdrant with: docker run -p 6333:6333 qdrant/qdrant")
    
    # Final summary
    print("\n" + "=" * 60)
    print("✅ SEEDING COMPLETE!")
    print("=" * 60)
    
    total = Product.objects.count()
    featured = Product.objects.filter(is_featured=True).count()
    
    print(f"\n📊 Database Statistics:")
    print(f"   - Total Products: {total}")
    print(f"   - Featured Products: {featured}")
    
    # Show products by sector
    print(f"\n📦 Products by Sector:")
    for sector, label in Product.SECTOR_CHOICES:
        count = Product.objects.filter(sector=sector).count()
        print(f"   - {label}: {count}")
    
    print(f"\n🚀 Ready to go! Run: python manage.py runserver")
    print()


if __name__ == '__main__':
    # Check for --fresh flag
    fresh = '--fresh' in sys.argv
    seed_products(fresh=fresh)
