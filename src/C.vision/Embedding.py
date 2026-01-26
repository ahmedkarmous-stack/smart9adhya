import pandas as pd
import requests
from PIL import Image
from io import BytesIO
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

# --- CONFIGURATION ---
client = QdrantClient(path="qdrant_local_data")
COLLECTION_NAME = "smart9adhya_multimodal"
model = SentenceTransformer('clip-ViT-B-32')

# 1. Download & Process Image
def get_embedding_from_url(url, fallback_text):
    """
    Tries to download and embed the image. 
    If it fails (broken link), it falls back to embedding the text.
    """
    try:
        # Download image (timeout 5s to prevent hanging)
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        # Embed the IMAGE
        return model.encode(image)
    except Exception as e:
        print(f"⚠️ Could not process image {url}: {e}. Falling back to text.")
        # Fallback: Embed the TEXT
        return model.encode(fallback_text)

# 2. Load Data
df_products = pd.read_csv("products.csv") 
df_reviews = pd.read_csv("reviews.csv")

# 3. Merge Reviews
reviews_grouped = df_reviews.groupby('product_id')['body'].apply(
    lambda x: " ".join(x.astype(str).tolist()[:3])
).reset_index()

df_final = pd.merge(df_products, reviews_grouped, left_on='id', right_on='product_id', how='left')

# 4. Prepare Context (for fallback)
df_final['ai_context'] = (
    df_final['name'] + " " + df_final['category'] + " " + df_final['description']
)

# 5. Reset Collection
if client.collection_exists(COLLECTION_NAME):
    client.delete_collection(COLLECTION_NAME)

client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=512, distance=Distance.COSINE)
)

# 6. Generate Embeddings (Row by Row)
points = []
for i, row in df_final.iterrows():
    # --- CHANGE: GENERATE EMBEDDING FROM URL ---
    vector = get_embedding_from_url(row['image_url'], row['ai_context'])
    
    points.append(PointStruct(
        id=str(row['id']),
        vector=vector.tolist(),
        payload={
            "name": row['name'],
            "price": float(row['price']),
            "image_url": row['image_url'],
            "category": row['category'],
            "rating": float(row['avg_rating']) if pd.notnull(row['avg_rating']) else 0
        }
    ))
    
    if i % 10 == 0:
        print(f"Processed {i}/{len(df_final)}")

print(f"Uploading {len(points)} products...")
client.upsert(collection_name=COLLECTION_NAME, points=points)
client.close()
print("finished embedding")
