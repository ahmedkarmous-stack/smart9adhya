import pandas as pd
import requests
from PIL import Image
from io import BytesIO
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import numpy as np 

# --- CONFIGURATION ---
client = QdrantClient(path="qdrant_local_data")
COLLECTION_NAME = "smart9adhya_multimodal"
model = SentenceTransformer('clip-ViT-B-32')

# 1. NEW HYBRID EMBEDDING FUNCTION (Mean Pooling)
def get_hybrid_embedding(text, url):
    """
    Generates a Combined Vector (Image + Text).
    Logic:
    1. Encode Text.
    2. Try to Encode Image.
    3. If Image works: Average them ((Text + Image) / 2).
    4. If Image fails: Return Text only.
    """
    # Step A: Get Text Vector
    text_vector = model.encode(text)
    
    # Step B: Get Image Vector
    image_vector = None
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        image_vector = model.encode(image)
    except Exception as e:
        # print(f"⚠️ Image failed for: {text[:20]}... using text only.") # Optional logging
        return text_vector # Fallback: Text only

    # Step C: Normalize & Average (The "Mean Pooling" Magic)
    # We normalize to ensure one doesn't overpower the other
    text_vector = text_vector / np.linalg.norm(text_vector)
    image_vector = image_vector / np.linalg.norm(image_vector)
    
    # Combine them
    combined_vector = (text_vector + image_vector) / 2.0
    return combined_vector

# 2. Load Data
df_products = pd.read_csv("products.csv") 
df_reviews = pd.read_csv("reviews.csv")

# 3. Merge Reviews
reviews_grouped = df_reviews.groupby('product_id')['body'].apply(
    lambda x: " ".join(x.astype(str).tolist()[:3])
).reset_index()

df_final = pd.merge(df_products, reviews_grouped, left_on='id', right_on='product_id', how='left')

# 4. Prepare Context
# We are now strictly relying on this context for the text-half of the vector
df_final['ai_context'] = (
    df_final['name'].astype(str) + " " + 
    df_final['category'].astype(str) + " " + 
    df_final['description'].astype(str)
)

# 5. Reset Collection
# CRITICAL: We must delete the old collection because these new vectors 
# are mathematically different from the old "Image Only" ones.
if client.collection_exists(COLLECTION_NAME):
    client.delete_collection(COLLECTION_NAME)

client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=512, distance=Distance.COSINE)
)

# 6. Generate Embeddings (Row by Row)
points = []
print(f"🚀 Starting Hybrid Ingestion for {len(df_final)} products...")

for i, row in df_final.iterrows():
    
    # --- CHANGE: USE HYBRID EMBEDDING ---
    # We pass BOTH the text context and the image URL
    vector = get_hybrid_embedding(row['ai_context'], row['image_url'])
    
    points.append(PointStruct(
        id=str(row['id']),
        vector=vector.tolist(),
        payload={
            "name": row['name'],
            "price": float(row['price']),
            "image_url": row['image_url'],
            "category": row['category'],
            "rating": float(row['avg_rating']) if pd.notnull(row['avg_rating']) else 0,
            # It's often good to save the text context in payload too for debugging
            "text_context": row['ai_context'][:200] 
        }
    ))
    
    if i % 10 == 0:
        print(f"Processed {i}/{len(df_final)}")

print(f"Uploading {len(points)} products to Qdrant...")
client.upsert(collection_name=COLLECTION_NAME, points=points)
client.close()
print("✅ Finished embedding. System is now truly Multimodal!")
