"""
Qdrant Vector Database Service for Smart9adhya
Handles product embeddings, similarity search, and RAG operations
"""

import logging
from typing import List, Dict, Any, Optional
from django.conf import settings

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qdrant_models
    from qdrant_client.http.exceptions import UnexpectedResponse
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    logging.warning("Qdrant client not installed. Running without vector search.")

logger = logging.getLogger('qdrant')

# Qdrant client singleton
_qdrant_client = None


def get_qdrant_client() -> Optional['QdrantClient']:
    """Get or create Qdrant client instance"""
    global _qdrant_client
    
    if not QDRANT_AVAILABLE:
        return None
    
    if _qdrant_client is None:
        try:
            _qdrant_client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
                timeout=30
            )
            logger.info(f"Connected to Qdrant at {settings.QDRANT_URL}")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            return None
    
    return _qdrant_client


def init_qdrant_collection() -> bool:
    """Initialize Qdrant collection if not exists"""
    client = get_qdrant_client()
    if not client:
        return False
    
    try:
        collections = client.get_collections().collections
        exists = any(c.name == settings.QDRANT_COLLECTION for c in collections)
        
        if not exists:
            client.create_collection(
                collection_name=settings.QDRANT_COLLECTION,
                vectors_config=qdrant_models.VectorParams(
                    size=settings.QDRANT_VECTOR_SIZE,
                    distance=qdrant_models.Distance.COSINE
                )
            )
            logger.info(f"Created Qdrant collection: {settings.QDRANT_COLLECTION}")
        else:
            logger.info(f"Qdrant collection exists: {settings.QDRANT_COLLECTION}")
        
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Qdrant collection: {e}")
        return False


# ============================================
# EMBEDDING GENERATION
# ============================================

# Color keywords mapping
COLOR_KEYWORDS = {
    'red': ['red', 'crimson', 'scarlet', 'ruby', 'burgundy', 'maroon'],
    'orange': ['orange', 'tangerine', 'coral', 'peach'],
    'yellow': ['yellow', 'gold', 'golden', 'mustard', 'lemon'],
    'green': ['green', 'olive', 'emerald', 'mint', 'forest', 'sage'],
    'blue': ['blue', 'navy', 'azure', 'cobalt', 'teal', 'turquoise', 'cyan'],
    'purple': ['purple', 'violet', 'lavender', 'plum', 'magenta'],
    'pink': ['pink', 'rose', 'blush', 'fuchsia', 'salmon'],
    'brown': ['brown', 'tan', 'chocolate', 'coffee', 'caramel', 'mocha'],
    'black': ['black', 'ebony', 'onyx', 'charcoal'],
    'white': ['white', 'ivory', 'cream', 'pearl', 'snow'],
    'gray': ['gray', 'grey', 'silver', 'slate', 'ash'],
    'beige': ['beige', 'nude', 'sand', 'khaki', 'taupe'],
}

# Materials list
MATERIALS = [
    'leather', 'cotton', 'silk', 'wool', 'polyester', 'denim', 'linen',
    'metal', 'wood', 'glass', 'plastic', 'ceramic', 'velvet', 'suede',
    'bamboo', 'steel', 'aluminum', 'rubber', 'canvas', 'nylon'
]

# Stopwords
STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
}


def hash_string(s: str) -> int:
    """Simple hash function for strings"""
    h = 0
    for char in s:
        h = ((h << 5) - h) + ord(char)
        h = h & 0xFFFFFFFF  # Keep 32-bit
    return h


def extract_keywords(text: str) -> List[str]:
    """Extract meaningful keywords from text"""
    import re
    words = re.sub(r'[^a-z0-9\s]', '', text.lower()).split()
    return [w for w in words if len(w) > 2 and w not in STOPWORDS]


def extract_colors(text: str) -> List[str]:
    """Extract colors from text"""
    text_lower = text.lower()
    detected = []
    for color, keywords in COLOR_KEYWORDS.items():
        if any(k in text_lower for k in keywords):
            detected.append(color)
    return detected


def extract_materials(text: str) -> List[str]:
    """Extract materials from text"""
    text_lower = text.lower()
    return [m for m in MATERIALS if m in text_lower]


def infer_use_cases(product) -> List[str]:
    """Infer use cases from product"""
    import re
    use_cases = []
    
    text = f"{product.name} {' '.join(product.tags or [])}".lower()
    
    patterns = {
        'work': r'office|work|business|professional',
        'home': r'home|house|living|bedroom|kitchen',
        'travel': r'travel|luggage|portable|carry',
        'outdoor': r'outdoor|hiking|camping|garden',
        'wellness': r'health|vitamin|supplement|organic',
        'entertainment': r'game|gaming|entertainment|fun',
        'fashion': r'style|fashion|trendy|designer',
        'cooking': r'cook|kitchen|food|recipe',
        'fitness': r'fitness|gym|workout|exercise|sport',
        'tech': r'tech|smart|digital|wireless|bluetooth',
        'beauty': r'beauty|skincare|cosmetic|makeup',
        'gift': r'gift|present|special',
    }
    
    for use_case, pattern in patterns.items():
        if re.search(pattern, text):
            use_cases.append(use_case)
    
    return use_cases


def generate_product_embedding(product) -> List[float]:
    """Generate embedding vector for a product"""
    vector_size = settings.QDRANT_VECTOR_SIZE
    embedding = [0.0] * vector_size
    
    # Category encoding (positions 0-15)
    categories = ['Fashion', 'Electronics', 'Furniture', 'Food', 'Healthcare', 'Sports', 'Wine']
    try:
        cat_idx = categories.index(product.sector)
        embedding[cat_idx] = 1.0
    except ValueError:
        pass
    
    # Price range encoding (positions 16-19)
    price = float(product.price)
    if price < 25:
        embedding[16] = 1.0
    elif price < 100:
        embedding[17] = 1.0
    elif price < 500:
        embedding[18] = 1.0
    else:
        embedding[19] = 1.0
    
    # Rating encoding (positions 20-24)
    rating = float(product.rating) if product.rating else 3.0
    rating_idx = min(int(rating), 4)
    embedding[20 + rating_idx] = rating / 5.0
    
    # Keyword encoding (positions 25-74)
    tags_text = ' '.join(product.tags or [])
    keywords = extract_keywords(f"{product.name} {tags_text}")
    for keyword in keywords:
        idx = hash_string(keyword) % 50
        embedding[25 + idx] = min(embedding[25 + idx] + 0.3, 1.0)
    
    # Color encoding (positions 75-89)
    colors = extract_colors(f"{product.name} {tags_text}")
    color_map = {
        'red': 75, 'orange': 76, 'yellow': 77, 'green': 78, 'blue': 79,
        'purple': 80, 'pink': 81, 'brown': 82, 'black': 83, 'white': 84,
        'gray': 85, 'beige': 86, 'navy': 87,
    }
    for color in colors:
        if color in color_map:
            embedding[color_map[color]] = 1.0
    
    # Material encoding (positions 90-109)
    materials = extract_materials(product.name)
    for material in materials:
        idx = hash_string(material) % 20
        embedding[90 + idx] = 1.0
    
    # Use case encoding (positions 110-127)
    use_cases = infer_use_cases(product)
    use_case_map = {
        'work': 110, 'home': 111, 'travel': 112, 'outdoor': 113,
        'wellness': 114, 'entertainment': 115, 'fashion': 116, 'cooking': 117,
        'fitness': 118, 'tech': 119, 'beauty': 120, 'gift': 121,
    }
    for uc in use_cases:
        if uc in use_case_map:
            embedding[use_case_map[uc]] = 1.0
    
    # Normalize vector
    magnitude = sum(v * v for v in embedding) ** 0.5
    if magnitude > 0:
        embedding = [v / magnitude for v in embedding]
    
    return embedding


def generate_query_embedding(query: str, intents: List[str] = None) -> List[float]:
    """Generate embedding vector for search query"""
    vector_size = settings.QDRANT_VECTOR_SIZE
    embedding = [0.0] * vector_size
    
    intents = intents or detect_intent(query)
    
    # Apply intent weights
    if 'budget' in intents:
        embedding[16] = 0.8
    if 'premium' in intents:
        embedding[18] = 0.8
        embedding[24] = 0.5
    
    # Keywords
    keywords = extract_keywords(query)
    for keyword in keywords:
        idx = hash_string(keyword) % 50
        embedding[25 + idx] = 0.5
    
    # Colors
    colors = extract_colors(query)
    color_map = {
        'red': 75, 'orange': 76, 'yellow': 77, 'green': 78, 'blue': 79,
        'purple': 80, 'pink': 81, 'brown': 82, 'black': 83, 'white': 84,
        'gray': 85, 'beige': 86, 'navy': 87,
    }
    for color in colors:
        if color in color_map:
            embedding[color_map[color]] = 0.8
    
    # Category detection
    categories = ['Fashion', 'Electronics', 'Furniture', 'Food', 'Healthcare', 'Sports', 'Wine']
    query_lower = query.lower()
    for i, cat in enumerate(categories):
        if cat.lower() in query_lower:
            embedding[i] = 1.0
    
    # Normalize
    magnitude = sum(v * v for v in embedding) ** 0.5
    if magnitude > 0:
        embedding = [v / magnitude for v in embedding]
    
    return embedding


def detect_intent(query: str) -> List[str]:
    """Detect user intent from query"""
    import re
    intents = []
    query_lower = query.lower()
    
    patterns = {
        'budget': r'cheap|affordable|budget|value|under \$|low price|inexpensive',
        'premium': r'best|premium|luxury|top|high.?end|quality|expensive',
        'trending': r'popular|trending|hot|new|latest|bestsell',
        'healthy': r'healthy|organic|natural|vitamin|wellness|bio',
        'tech': r'smart|wireless|bluetooth|digital|electronic|tech',
    }
    
    for intent, pattern in patterns.items():
        if re.search(pattern, query_lower):
            intents.append(intent)
    
    return intents


# ============================================
# INDEXING OPERATIONS
# ============================================

def index_product(product) -> bool:
    """Index a single product in Qdrant"""
    client = get_qdrant_client()
    if not client:
        return False
    
    try:
        embedding = generate_product_embedding(product)
        
        client.upsert(
            collection_name=settings.QDRANT_COLLECTION,
            points=[
                qdrant_models.PointStruct(
                    id=product.id,
                    vector=embedding,
                    payload={
                        'product_id': product.id,
                        'name': product.name,
                        'brand': product.brand,
                        'price': float(product.price),
                        'sector': product.sector,
                        'category': product.category,
                        'rating': float(product.rating) if product.rating else 0,
                        'reviews': product.reviews,
                        'image': product.image,
                        'tags': product.tags or [],
                    }
                )
            ]
        )
        
        # Update product status
        from django.utils import timezone
        product.qdrant_indexed = True
        product.qdrant_indexed_at = timezone.now()
        product.save(update_fields=['qdrant_indexed', 'qdrant_indexed_at'])
        
        logger.info(f"Indexed product {product.id}: {product.name}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to index product {product.id}: {e}")
        return False


def index_products(products) -> Dict[str, int]:
    """Batch index multiple products"""
    client = get_qdrant_client()
    if not client:
        return {'indexed': 0, 'failed': len(products)}
    
    points = []
    for product in products:
        try:
            embedding = generate_product_embedding(product)
            points.append(
                qdrant_models.PointStruct(
                    id=product.id,
                    vector=embedding,
                    payload={
                        'product_id': product.id,
                        'name': product.name,
                        'brand': product.brand,
                        'price': float(product.price),
                        'sector': product.sector,
                        'category': product.category,
                        'rating': float(product.rating) if product.rating else 0,
                        'reviews': product.reviews,
                        'image': product.image,
                        'tags': product.tags or [],
                    }
                )
            )
        except Exception as e:
            logger.error(f"Failed to create embedding for product {product.id}: {e}")
    
    if not points:
        return {'indexed': 0, 'failed': len(products)}
    
    try:
        # Batch upsert in chunks
        chunk_size = 100
        for i in range(0, len(points), chunk_size):
            chunk = points[i:i + chunk_size]
            client.upsert(
                collection_name=settings.QDRANT_COLLECTION,
                points=chunk
            )
        
        # Update indexed status
        from django.utils import timezone
        product_ids = [p.id for p in products]
        from products.models import Product
        Product.objects.filter(id__in=product_ids).update(
            qdrant_indexed=True,
            qdrant_indexed_at=timezone.now()
        )
        
        logger.info(f"Batch indexed {len(points)} products")
        return {'indexed': len(points), 'failed': len(products) - len(points)}
    
    except Exception as e:
        logger.error(f"Batch indexing failed: {e}")
        return {'indexed': 0, 'failed': len(products)}


def delete_product_from_index(product_id: int) -> bool:
    """Remove product from Qdrant index"""
    client = get_qdrant_client()
    if not client:
        return False
    
    try:
        client.delete(
            collection_name=settings.QDRANT_COLLECTION,
            points_selector=qdrant_models.PointIdsList(points=[product_id])
        )
        logger.info(f"Deleted product {product_id} from index")
        return True
    except Exception as e:
        logger.error(f"Failed to delete product {product_id}: {e}")
        return False


# ============================================
# SEARCH OPERATIONS
# ============================================

def search_similar(
    query: str,
    limit: int = 20,
    budget: float = None,
    sector: str = None
) -> List[Dict[str, Any]]:
    """Search for similar products using vector similarity"""
    client = get_qdrant_client()
    if not client:
        logger.warning("Qdrant not available, using fallback search")
        return []
    
    try:
        # Detect intent
        intents = detect_intent(query)
        
        # Generate query embedding
        query_embedding = generate_query_embedding(query, intents)
        
        # Build filter
        filter_conditions = []
        
        if budget:
            filter_conditions.append(
                qdrant_models.FieldCondition(
                    key="price",
                    range=qdrant_models.Range(lte=budget)
                )
            )
        
        if sector and sector.lower() != 'all':
            filter_conditions.append(
                qdrant_models.FieldCondition(
                    key="sector",
                    match=qdrant_models.MatchValue(value=sector)
                )
            )
        
        search_filter = None
        if filter_conditions:
            search_filter = qdrant_models.Filter(must=filter_conditions)
        
        # Execute search
        results = client.search(
            collection_name=settings.QDRANT_COLLECTION,
            query_vector=query_embedding,
            limit=limit,
            query_filter=search_filter,
            score_threshold=0.3,
            with_payload=True
        )
        
        # Format results
        formatted = []
        for i, result in enumerate(results):
            formatted.append({
                'product_id': result.payload.get('product_id'),
                'name': result.payload.get('name'),
                'brand': result.payload.get('brand'),
                'price': result.payload.get('price'),
                'sector': result.payload.get('sector'),
                'category': result.payload.get('category'),
                'rating': result.payload.get('rating'),
                'reviews': result.payload.get('reviews'),
                'image': result.payload.get('image'),
                'tags': result.payload.get('tags', []),
                'score': result.score,
                'rank': i + 1,
                'match_percentage': round(result.score * 100),
            })
        
        logger.info(f"Search '{query}' returned {len(formatted)} results")
        return formatted
    
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return []


def get_collection_stats() -> Optional[Dict[str, Any]]:
    """Get Qdrant collection statistics"""
    client = get_qdrant_client()
    if not client:
        return None
    
    try:
        info = client.get_collection(settings.QDRANT_COLLECTION)
        return {
            'points_count': info.points_count,
            'vectors_count': info.vectors_count,
            'indexed_vectors_count': info.indexed_vectors_count,
            'status': info.status,
        }
    except Exception as e:
        logger.error(f"Failed to get collection stats: {e}")
        return None
