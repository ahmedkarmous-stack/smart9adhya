import os
import json
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, Range, MatchValue
from sentence_transformers import SentenceTransformer
from PIL import Image
from groq import Groq 

# --- CONFIGURATION ---
client = QdrantClient(path="qdrant_local_data")
COLLECTION_NAME = "smart9adhya_multimodal"
model = SentenceTransformer('clip-ViT-B-32')

#the api key
os.environ["GROQ_API_KEY"] = "gsk_..." 
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def analyze_query_with_groq(query):
    """
    Uses the LLM to extract the 'Intent' and 'Category' from the user's search.
    Example: "Jeans under 200" -> Category: "Jeans"
    """
    prompt = f"""
    You are a search query parser. Extract the most likely product category from this search query.
    
    Query: "{query}"
    
    Rules:
    - Return ONLY the category name as a single word (e.g., "Jeans", "Dresses", "Watches", "Health", "Food").
    - If the query is vague (like "gift ideas"), return "None".
    - Match the capitalization typical for e-commerce (Title Case).
    - Do not write any other text. Just the word.
    """
    
    try:
        completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.1, # Low temperature for precision
            max_tokens=10
        )
        category = completion.choices[0].message.content.strip()
        return category.replace('"', '').replace('.', '')
    except:
        return "None"

def generate_explanation(product, query, user_budget):
    prompt = f"""Explain why {product['name']} (${product['price']}) is a good match for '{query}' (Budget: ${user_budget}). 1 sentence."""
    try:
        res = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.7, max_tokens=50
        )
        return res.choices[0].message.content.strip()
    except:
        return "Great match for your budget!"

def search_products(query, user_budget, search_type="text"):
    
    # 1. ANALYZE INTENT (The "Smart" Layer)
    # We ask the AI: "What is the user looking for?"
    detected_category = analyze_query_with_groq(query)
    print(f"AI Detected Category: [{detected_category}]")

    # 2. BUILD FILTERS
    search_filters = [
        FieldCondition(key="price", range=Range(lte=user_budget))
    ]
    

    if detected_category and detected_category != "None":
        search_filters.append(
            FieldCondition(key="category", match=MatchValue(value=detected_category))
        )

    # 3. VECTOR SEARCH
    if search_type == "image":
        img = Image.open(query)
        query_vector = model.encode(img).tolist()
    else:
        query_vector = model.encode(query).tolist()

    print(f"Searching Qdrant...")
    try:
        response = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            query_filter=Filter(must=search_filters), # Apply the Smart Filters
            limit=5
        )
    except Exception as e:
        print(f"Search Error: {e}")
        return []

    # 4. PROCESS RESULTS
    final_results = []
    candidates = [hit.payload for hit in response.points]

    if not candidates:
        print(f"No items found in category '{detected_category}' under ${user_budget}.")
        return []

    print(f"Generating explanations for {len(candidates[:3])} items...\n")
    
    for product in candidates[:3]:
        explanation = generate_explanation(product, query, user_budget)
        final_results.append({
            "name": product['name'],
            "price": f"${product['price']:.2f}",
            "why": explanation
        })

    return final_results

# --- TEST ---
if _name_ == "_main_":
    budget = 200.0
    print("=" * 60)
    # Test with your specific query
    q = "blue denim jeans slim fit"
    print(f"QUERY: '{q}'")
    
    results = search_products(q, budget)
    
    for i, p in enumerate(results, 1):
        print(f" Result #{i}")
        print(f" Name: {p['name']}")
        print(f" Price: {p['price']}")
        print(f" Why: {p['why']}")
        print()
    
    client.close()
