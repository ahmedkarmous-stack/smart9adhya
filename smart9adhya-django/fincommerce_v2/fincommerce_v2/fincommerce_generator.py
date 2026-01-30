"""
FinCommerce Engine - Complete Database Generator v2
====================================================
- 2000+ products, 300 users, 5000 behaviors, 4000 reviews
- Real Unsplash image URLs
- Detailed realistic descriptions
- NO missing values
- CSV export

Usage: python fincommerce_generator.py
"""

import json, random, uuid, hashlib, os
from datetime import datetime
from pathlib import Path

try:
    from faker import Faker
    import pandas as pd
except ImportError:
    import subprocess
    subprocess.run(["pip", "install", "faker", "pandas", "-q"])
    from faker import Faker
    import pandas as pd

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    QDRANT_OK = True
except:
    QDRANT_OK = False

# Config
DB_PATH = "./qdrant_db"
OUT_DIR = "./csv_export"
NUM_PRODUCTS, NUM_USERS, NUM_BEHAVIORS, NUM_REVIEWS = 2000, 300, 5000, 4000

fake = Faker()
Faker.seed(42)
random.seed(42)

# Real Unsplash Images
IMAGES = {
    "Laptops": ["https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600",
                "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=600",
                "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600"],
    "Smartphones": ["https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600",
                    "https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=600"],
    "Headphones": ["https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600",
                   "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=600"],
    "Smartwatches": ["https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600",
                    "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=600"],
    "Tablets": ["https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=600"],
    "Dresses": ["https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=600",
                "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=600"],
    "Shoes": ["https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600",
              "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=600"],
    "Handbags": ["https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=600"],
    "Jackets": ["https://images.unsplash.com/photo-1551028719-00167b16eac5?w=600"],
    "Watches": ["https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=600"],
    "Jeans": ["https://images.unsplash.com/photo-1542272604-787c3835535d?w=600"],
    "T-Shirts": ["https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600"],
    "Coffee & Tea": ["https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=600"],
    "Chocolates": ["https://images.unsplash.com/photo-1481391319762-47dff72954d9?w=600"],
    "Gourmet Foods": ["https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=600"],
    "Olive Oil": ["https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=600"],
    "Cheese": ["https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=600"],
    "Fitness Equipment": ["https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=600"],
    "Sports Apparel": ["https://images.unsplash.com/photo-1556906781-9a412961c28c?w=600"],
    "Outdoor Gear": ["https://images.unsplash.com/photo-1551632811-561732d1e306?w=600"],
    "Yoga & Pilates": ["https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=600"],
    "Running Gear": ["https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?w=600"],
    "Red Wine": ["https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=600"],
    "White Wine": ["https://images.unsplash.com/photo-1558001373-7b93ee48ffa0?w=600"],
    "Champagne": ["https://images.unsplash.com/photo-1549918864-48ac978761a4?w=600"],
    "Spirits": ["https://images.unsplash.com/photo-1569529465841-dfecdab7503b?w=600"],
    "Craft Beer": ["https://images.unsplash.com/photo-1535958636474-b021ee887b13?w=600"],
    "Vitamins": ["https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=600"],
    "Skincare": ["https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600"],
    "Medical Devices": ["https://images.unsplash.com/photo-1631815588090-d4bfec5b1ccb?w=600"],
    "Personal Care": ["https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=600"],
    "Essential Oils": ["https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?w=600"],
    "Sofas": ["https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600"],
    "Beds": ["https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=600"],
    "Desks & Chairs": ["https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=600"],
    "Dining": ["https://images.unsplash.com/photo-1617806118233-18e1de247200?w=600"],
    "Storage": ["https://images.unsplash.com/photo-1558997519-83ea9252edf8?w=600"],
    "Lighting": ["https://images.unsplash.com/photo-1524484485831-a92ffc0de03f?w=600"]
}

DEFAULT_IMG = {
    "Electronics": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600",
    "Fashion": "https://images.unsplash.com/photo-1441984904996-e0b6ba687e04?w=600",
    "Food": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=600",
    "Sports": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=600",
    "Wine": "https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=600",
    "Healthcare": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=600",
    "Furniture": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600"
}

# Categories with brands and models
CATS = {
    "Laptops": {"sector": "Electronics", "brands": {"Apple": ["MacBook Air M3", "MacBook Pro 14", "MacBook Pro 16"], "Dell": ["XPS 13", "XPS 15", "Inspiron 15"], "HP": ["Spectre x360", "Envy 15", "Pavilion"], "Lenovo": ["ThinkPad X1", "IdeaPad 5", "Yoga 9i"], "ASUS": ["ZenBook 14", "ROG Zephyrus", "VivoBook"]}, "price": (699, 3499)},
    "Smartphones": {"sector": "Electronics", "brands": {"Apple": ["iPhone 15", "iPhone 15 Pro", "iPhone 15 Pro Max"], "Samsung": ["Galaxy S24", "Galaxy S24 Ultra", "Galaxy Z Fold5"], "Google": ["Pixel 8", "Pixel 8 Pro"]}, "price": (399, 1599)},
    "Headphones": {"sector": "Electronics", "brands": {"Sony": ["WH-1000XM5", "WF-1000XM5"], "Apple": ["AirPods Pro 2", "AirPods Max"], "Bose": ["QuietComfort Ultra", "QuietComfort 45"], "Sennheiser": ["Momentum 4", "HD 660S2"]}, "price": (99, 599)},
    "Smartwatches": {"sector": "Electronics", "brands": {"Apple": ["Watch Series 9", "Watch Ultra 2", "Watch SE"], "Samsung": ["Galaxy Watch 6"], "Garmin": ["Fenix 7", "Forerunner 965"]}, "price": (249, 899)},
    "Tablets": {"sector": "Electronics", "brands": {"Apple": ["iPad Pro 12.9", "iPad Air", "iPad 10th Gen"], "Samsung": ["Galaxy Tab S9", "Galaxy Tab S9+"]}, "price": (449, 1499)},
    "Dresses": {"sector": "Fashion", "brands": {"Zara": ["Midi Dress", "Maxi Dress", "Cocktail Dress"], "H&M": ["Wrap Dress", "Party Dress"], "Reformation": ["Juliette Dress", "Gavin Dress"], "Free People": ["Boho Maxi", "Floral Mini"]}, "price": (39, 398)},
    "Shoes": {"sector": "Fashion", "brands": {"Nike": ["Air Max 90", "Air Force 1", "Dunk Low"], "Adidas": ["Ultraboost", "Stan Smith", "Superstar"], "New Balance": ["990v5", "574", "550"], "Converse": ["Chuck Taylor", "Chuck 70"]}, "price": (59, 250)},
    "Handbags": {"sector": "Fashion", "brands": {"Coach": ["Tabby Shoulder Bag", "Willow Tote"], "Michael Kors": ["Jet Set Tote", "Soho Shoulder"], "Kate Spade": ["Spencer Satchel", "Knott Tote"], "Tory Burch": ["Kira Chevron", "Robinson Tote"]}, "price": (128, 598)},
    "Jackets": {"sector": "Fashion", "brands": {"The North Face": ["Thermoball", "Nuptse 1996"], "Patagonia": ["Nano Puff", "Down Sweater"], "Columbia": ["Watertight II"], "Levi's": ["Trucker Jacket"]}, "price": (89, 399)},
    "Watches": {"sector": "Fashion", "brands": {"Seiko": ["Presage", "Prospex"], "Tissot": ["PRX", "Gentleman"], "Fossil": ["Grant", "Neutra"], "Citizen": ["Eco-Drive", "Promaster"]}, "price": (125, 795)},
    "Jeans": {"sector": "Fashion", "brands": {"Levi's": ["501 Original", "511 Slim", "721 High Rise"], "Diesel": ["Sleenker", "D-Strukt"], "AG": ["The Legging", "The Prima"]}, "price": (69, 248)},
    "T-Shirts": {"sector": "Fashion", "brands": {"Uniqlo": ["Supima Cotton", "AIRism"], "COS": ["Regular Fit Tee"], "Everlane": ["Organic Cotton Crew"]}, "price": (19, 65)},
    "Gourmet Foods": {"sector": "Food", "brands": {"Whole Foods": ["Organic Quinoa", "Truffle Oil"], "Trader Joe's": ["Cookie Butter", "Everything Bagel"], "Eataly": ["San Marzano Tomatoes", "Parmigiano"]}, "price": (12, 89)},
    "Coffee & Tea": {"sector": "Food", "brands": {"Nespresso": ["Vertuo", "Original Line"], "Lavazza": ["Super Crema", "Qualità Oro"], "Twinings": ["Earl Grey", "English Breakfast"], "Harney & Sons": ["Paris", "Hot Cinnamon"]}, "price": (12, 65)},
    "Chocolates": {"sector": "Food", "brands": {"Godiva": ["Gold Collection", "Truffle Flight"], "Lindt": ["Excellence 85%", "Lindor"], "Valrhona": ["Guanaja 70%", "Manjari"]}, "price": (8, 75)},
    "Olive Oil": {"sector": "Food", "brands": {"California Olive Ranch": ["Extra Virgin", "Reserve"], "Colavita": ["Premium EVOO"], "Partanna": ["Sicilian EVOO"]}, "price": (12, 48)},
    "Cheese": {"sector": "Food", "brands": {"Président": ["Brie", "Camembert"], "Kerrygold": ["Dubliner", "Aged Cheddar"], "Tillamook": ["Sharp Cheddar"]}, "price": (8, 35)},
    "Fitness Equipment": {"sector": "Sports", "brands": {"Bowflex": ["SelectTech Dumbbells", "Max Trainer"], "Peloton": ["Bike+", "Tread"], "NordicTrack": ["Commercial 1750", "RW900 Rower"], "Rogue": ["Echo Bike", "Ohio Bar"]}, "price": (199, 2999)},
    "Sports Apparel": {"sector": "Sports", "brands": {"Nike": ["Dri-FIT Tee", "Pro Compression"], "Lululemon": ["Align Leggings", "ABC Pants"], "Under Armour": ["HeatGear", "ColdGear"], "Gymshark": ["Vital Seamless", "Apex Shorts"]}, "price": (35, 148)},
    "Outdoor Gear": {"sector": "Sports", "brands": {"REI": ["Flash 55 Pack", "Quarter Dome Tent"], "Osprey": ["Atmos AG 65", "Daylite Plus"], "Black Diamond": ["Spot Headlamp", "Trail Poles"]}, "price": (45, 549)},
    "Yoga & Pilates": {"sector": "Sports", "brands": {"Manduka": ["PRO Mat", "eKO Lite"], "Liforme": ["Original Mat", "Travel Mat"], "Gaiam": ["Premium Mat", "Block Set"]}, "price": (25, 148)},
    "Running Gear": {"sector": "Sports", "brands": {"Nike": ["Vaporfly", "Pegasus 40"], "Brooks": ["Ghost 15", "Glycerin 20"], "ASICS": ["Gel-Kayano 30"], "Hoka": ["Clifton 9", "Bondi 8"]}, "price": (120, 275)},
    "Red Wine": {"sector": "Wine", "brands": {"Château Margaux": ["Grand Vin 2019", "Pavillon Rouge"], "Caymus": ["Napa Cabernet 2021"], "Penfolds": ["Bin 389", "Grange"], "Meiomi": ["Pinot Noir 2022"]}, "price": (18, 395)},
    "White Wine": {"sector": "Wine", "brands": {"Cloudy Bay": ["Sauvignon Blanc 2023"], "Rombauer": ["Chardonnay 2022"], "Kim Crawford": ["Sauvignon Blanc"], "Cakebread": ["Chardonnay"]}, "price": (15, 185)},
    "Champagne": {"sector": "Wine", "brands": {"Dom Pérignon": ["Vintage 2013", "Rosé 2009"], "Moët & Chandon": ["Impérial Brut", "Rosé"], "Veuve Clicquot": ["Yellow Label", "La Grande Dame"]}, "price": (55, 495)},
    "Spirits": {"sector": "Wine", "brands": {"Macallan": ["12 Year Sherry Oak", "18 Year"], "Grey Goose": ["Original Vodka"], "Patrón": ["Silver Tequila", "Reposado"], "Hendrick's": ["Original Gin"]}, "price": (35, 395)},
    "Craft Beer": {"sector": "Wine", "brands": {"Sierra Nevada": ["Pale Ale", "Torpedo IPA"], "Dogfish Head": ["90 Minute IPA"], "Stone": ["Stone IPA", "Delicious IPA"]}, "price": (12, 45)},
    "Vitamins": {"sector": "Healthcare", "brands": {"Nature Made": ["Vitamin D3", "Fish Oil", "Multivitamin"], "Garden of Life": ["Vitamin Code", "Probiotics"], "Nordic Naturals": ["Ultimate Omega"]}, "price": (15, 65)},
    "Skincare": {"sector": "Healthcare", "brands": {"CeraVe": ["Moisturizing Cream", "Hydrating Cleanser"], "La Roche-Posay": ["Toleriane", "Effaclar"], "Drunk Elephant": ["Protini Cream", "C-Firma"], "The Ordinary": ["Niacinamide", "Hyaluronic Acid"]}, "price": (12, 125)},
    "Medical Devices": {"sector": "Healthcare", "brands": {"Omron": ["Platinum BP Monitor", "TENS Unit"], "Withings": ["Body+ Scale", "BPM Connect"], "Braun": ["ThermoScan 7"]}, "price": (35, 349)},
    "Personal Care": {"sector": "Healthcare", "brands": {"Philips Sonicare": ["DiamondClean", "ProtectiveClean"], "Oral-B": ["iO Series 9", "Smart 1500"], "Waterpik": ["Aquarius Flosser"]}, "price": (35, 299)},
    "Essential Oils": {"sector": "Healthcare", "brands": {"doTERRA": ["Lavender", "Peppermint"], "Young Living": ["Thieves", "Lemon"], "Plant Therapy": ["Eucalyptus", "Tea Tree"]}, "price": (12, 85)},
    "Sofas": {"sector": "Furniture", "brands": {"West Elm": ["Harmony Sofa", "Haven Sectional"], "IKEA": ["KIVIK", "FRIHETEN"], "Article": ["Sven Sofa", "Timber Sofa"], "Crate & Barrel": ["Lounge Deep", "Gather"]}, "price": (599, 3999)},
    "Beds": {"sector": "Furniture", "brands": {"Casper": ["Original", "Wave Hybrid"], "Purple": ["Original", "Hybrid Premier"], "Tempur-Pedic": ["TEMPUR-Adapt", "ProAdapt"], "Saatva": ["Classic", "Loom & Leaf"]}, "price": (699, 3499)},
    "Desks & Chairs": {"sector": "Furniture", "brands": {"Herman Miller": ["Aeron Chair", "Embody"], "Steelcase": ["Leap Chair", "Gesture"], "Secretlab": ["TITAN Evo", "Magnus Desk"], "Autonomous": ["ErgoChair Pro", "SmartDesk"]}, "price": (299, 1895)},
    "Dining": {"sector": "Furniture", "brands": {"West Elm": ["Mid-Century Table", "Dining Chair"], "IKEA": ["EKEDALEN", "NORDVIKEN"], "Pottery Barn": ["Toscana Table"]}, "price": (249, 2499)},
    "Storage": {"sector": "Furniture", "brands": {"IKEA": ["KALLAX", "PAX", "MALM"], "Container Store": ["Elfa Classic"], "California Closets": ["Custom Walk-In"]}, "price": (79, 1299)},
    "Lighting": {"sector": "Furniture", "brands": {"Philips Hue": ["Starter Kit", "Play Bar"], "West Elm": ["Mobile Chandelier", "Floor Lamp"], "IKEA": ["HEKTAR", "TERTIAL"]}, "price": (35, 549)}
}

COLORS = ["Black", "White", "Navy", "Gray", "Beige", "Red", "Blue", "Green", "Brown", "Pink", "Silver", "Gold"]
SIZES = ["XS", "S", "M", "L", "XL", "XXL"]
MATERIALS = ["Cotton", "Leather", "Polyester", "Wool", "Silk", "Linen", "Denim", "Canvas", "Nylon"]
PAYMENT = ["credit_card", "debit_card", "paypal", "apple_pay", "google_pay", "klarna", "affirm"]

def get_img(cat, sector, idx):
    if cat in IMAGES:
        return IMAGES[cat][idx % len(IMAGES[cat])]
    return DEFAULT_IMG.get(sector, DEFAULT_IMG["Electronics"])

def make_embed(text):
    h = hashlib.sha256(text.encode()).digest()
    random.seed(int.from_bytes(h[:4], 'big'))
    e = [random.gauss(0, 1) for _ in range(384)]
    m = sum(x*x for x in e) ** 0.5
    return [x/m for x in e]

def gen_desc(brand, model, cat, sector, attrs):
    """Generate realistic description."""
    if sector == "Electronics":
        if cat == "Laptops":
            return f"The {brand} {model} delivers exceptional performance with its {attrs.get('processor', 'latest')} processor and {attrs.get('ram', '16GB')} RAM. Features a stunning {attrs.get('screen', '14-inch')} Retina display, {attrs.get('storage', '512GB')} SSD storage, and up to {attrs.get('battery', '18 hours')} battery life. Perfect for professionals, creatives, and students who demand power and portability."
        elif cat == "Smartphones":
            return f"Experience the {brand} {model} with its advanced {attrs.get('camera', '48MP')} camera system and {attrs.get('screen', '6.1-inch')} Super Retina XDR display. Powered by the {attrs.get('chip', 'latest')} chip with {attrs.get('storage', '256GB')} storage. Features {attrs.get('battery', 'all-day')} battery life, Face ID, and 5G connectivity for seamless performance."
        elif cat == "Headphones":
            return f"Immerse yourself in sound with the {brand} {model}. Industry-leading noise cancellation, {attrs.get('battery', '30-hour')} battery life, and premium drivers deliver exceptional audio quality. Features adaptive sound control, multipoint Bluetooth connection, and touch controls. Perfect for commuting, working, or relaxing."
        else:
            return f"The {brand} {model} combines cutting-edge technology with premium design. Features {attrs.get('display', 'brilliant display')}, long battery life, and seamless connectivity. Built for those who demand the best in portable electronics."
    elif sector == "Fashion":
        return f"Elevate your style with the {brand} {model}. Crafted from premium {attrs.get('material', 'fabric')} in {attrs.get('color', 'classic')} colorway. Features {attrs.get('fit', 'modern fit')} construction for all-day comfort. Perfect for {attrs.get('occasion', 'casual and formal occasions')}. Machine washable for easy care."
    elif sector == "Food":
        return f"Savor the exceptional quality of {brand} {model}. Sourced from {attrs.get('origin', 'premium suppliers')} and crafted using traditional methods. {attrs.get('certification', 'Non-GMO')} certified with no artificial preservatives. Perfect for gourmet cooking, gifting, or everyday indulgence."
    elif sector == "Sports":
        return f"Push your limits with the {brand} {model}. Engineered for peak performance with {attrs.get('tech', 'advanced technology')} and premium materials. Features {attrs.get('feature', 'ergonomic design')} for maximum comfort during intense workouts. Built to perform when it matters most."
    elif sector == "Wine":
        return f"Discover the {brand} {model} from {attrs.get('region', 'premier vineyards')}. This {attrs.get('type', 'exceptional vintage')} features notes of {attrs.get('notes', 'rich fruit and subtle oak')}, with a {attrs.get('finish', 'smooth, lingering')} finish. Perfect with {attrs.get('pairing', 'grilled meats and aged cheese')}. Alcohol: {attrs.get('abv', '13.5')}%."
    elif sector == "Healthcare":
        return f"Support your wellness with {brand} {model}. Formulated with {attrs.get('ingredients', 'premium ingredients')} for {attrs.get('benefit', 'optimal health')}. {attrs.get('certification', 'Third-party tested')} and {attrs.get('dietary', 'suitable for most diets')}. Recommended dosage: {attrs.get('dosage', 'as directed')}."
    elif sector == "Furniture":
        return f"Transform your space with the {brand} {model}. Crafted from {attrs.get('material', 'premium materials')} with {attrs.get('finish', 'elegant finish')}. Dimensions: {attrs.get('dims', 'see specifications')}. Features {attrs.get('feature', 'modern design')} that complements any interior. Assembly: {attrs.get('assembly', 'easy assembly')}."
    return f"{brand} {model} - Premium quality {cat.lower()} designed for exceptional performance."

def gen_products(n):
    print(f"📦 Generating {n} products...")
    prods = []
    cats = list(CATS.keys())
    # Ensure balanced distribution by cycling through categories
    cat_cycle = (cats * (n // len(cats) + 1))[:n]
    random.shuffle(cat_cycle)
    
    for i in range(n):
        cat = cat_cycle[i]  # Use balanced distribution
        info = CATS[cat]
        sector = info["sector"]
        brand = random.choice(list(info["brands"].keys()))
        model = random.choice(info["brands"][brand])
        price = round(random.uniform(*info["price"]), 2)
        
        # Attributes based on category
        attrs = {"color": random.choice(COLORS)}
        if sector == "Electronics":
            attrs.update({"processor": random.choice(["Apple M3", "Intel i7", "AMD Ryzen 7", "Snapdragon 8"]),
                         "ram": random.choice(["8GB", "16GB", "32GB"]),
                         "storage": random.choice(["256GB", "512GB", "1TB"]),
                         "screen": random.choice(["13-inch", "14-inch", "15-inch", "6.1-inch", "6.7-inch"]),
                         "battery": random.choice(["15 hours", "18 hours", "22 hours", "all-day"])})
        elif sector == "Fashion":
            attrs.update({"size": random.choice(SIZES), "material": random.choice(MATERIALS),
                         "fit": random.choice(["slim fit", "regular fit", "relaxed fit"]),
                         "occasion": random.choice(["casual wear", "business", "evening", "athletic"])})
        elif sector == "Food":
            attrs.update({"weight": random.choice(["100g", "250g", "500g", "1kg"]),
                         "origin": random.choice(["Italy", "France", "USA", "Japan"]),
                         "certification": random.choice(["Organic", "Non-GMO", "Fair Trade"])})
        elif sector == "Wine":
            attrs.update({"region": random.choice(["Napa Valley", "Bordeaux", "Tuscany", "Rioja"]),
                         "vintage": str(random.randint(2018, 2023)),
                         "abv": str(round(random.uniform(12, 15), 1)),
                         "notes": random.choice(["blackberry and oak", "citrus and mineral", "cherry and vanilla"])})
        elif sector == "Healthcare":
            attrs.update({"count": random.choice(["30", "60", "90", "120"]),
                         "form": random.choice(["Capsules", "Tablets", "Gummies"]),
                         "dosage": random.choice(["1 daily", "2 daily", "as needed"])})
        elif sector == "Furniture":
            attrs.update({"material": random.choice(["Solid Oak", "Walnut", "Leather", "Fabric"]),
                         "dims": f"{random.randint(60,200)}W x {random.randint(40,100)}D x {random.randint(30,120)}H cm",
                         "assembly": random.choice(["Easy assembly", "No assembly", "Professional delivery"])})
        
        desc = gen_desc(brand, model, cat, sector, attrs)
        img = get_img(cat, sector, i)
        
        inst_avail = price > 100 and random.random() > 0.3
        inst_months = random.choice([3, 6, 12, 24]) if inst_avail else 0
        
        prod = {
            "id": str(uuid.uuid4()),
            "product_id": f"PROD-{i+1:05d}",
            "name": f"{brand} {model}",
            "brand": brand,
            "model": model,
            "category": cat,
            "sector": sector,
            "description": desc,
            "price": price,
            "currency": "USD",
            "original_price": round(price * random.uniform(1.0, 1.25), 2) if random.random() > 0.7 else price,
            "discount_percent": 0,
            "color": attrs.get("color", "Black"),
            "size": attrs.get("size", "One Size"),
            "material": attrs.get("material", "Premium"),
            "attributes": json.dumps(attrs),
            "tags": f"{cat}|{sector}|{brand}",
            "in_stock": random.random() > 0.08,
            "stock_quantity": random.randint(5, 200),
            "installment_available": inst_avail,
            "installment_months": inst_months,
            "monthly_payment": round(price / inst_months, 2) if inst_months > 0 else 0,
            "avg_rating": round(random.uniform(3.8, 5.0), 1),
            "review_count": random.randint(15, 2500),
            "image_url": img,
            "sku": f"SKU-{brand[:3].upper()}-{random.randint(10000,99999)}",
            "weight_kg": round(random.uniform(0.1, 15), 2),
            "warranty_months": random.choice([0, 12, 24, 36]),
            "shipping_free": price > 50,
            "created_at": fake.date_time_between("-2y", "now").isoformat(),
            "updated_at": fake.date_time_between("-30d", "now").isoformat()
        }
        if prod["original_price"] > prod["price"]:
            prod["discount_percent"] = round((1 - prod["price"]/prod["original_price"]) * 100)
        
        prod["embedding"] = make_embed(f"{prod['name']} {cat} {sector} {desc}")
        prods.append(prod)
    
    # Stats
    sectors = {}
    for p in prods:
        sectors[p["sector"]] = sectors.get(p["sector"], 0) + 1
    print("   Distribution:", sectors)
    return prods

def gen_users(n):
    print(f"👤 Generating {n} users...")
    users = []
    tiers = [("budget", 300, 1000, "low"), ("mid-range", 1000, 3000, "medium"),
             ("premium", 3000, 8000, "high"), ("luxury", 8000, 20000, "high")]
    tier_weights = [0.30, 0.35, 0.25, 0.10]  # More realistic distribution
    sectors = list(set(c["sector"] for c in CATS.values()))
    
    for i in range(n):
        tier = random.choices(tiers, weights=tier_weights)[0]
        budget = round(random.uniform(tier[1], tier[2]), 2)
        methods = random.sample(PAYMENT, random.randint(2, 5))
        pref_sectors = random.sample(sectors, random.randint(2, 4))
        
        user = {
            "id": str(uuid.uuid4()),
            "user_id": f"USER-{i+1:05d}",
            "email": fake.email(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "age": random.randint(18, 70),
            "gender": random.choice(["Male", "Female", "Other"]),
            "phone": fake.phone_number()[:15],
            "city": fake.city(),
            "country": fake.country()[:30],
            "postal_code": fake.postcode()[:10],
            "budget_tier": tier[0],
            "total_budget": budget,
            "monthly_limit": round(budget * random.uniform(0.15, 0.35), 2),
            "currency": "USD",
            "risk_tolerance": tier[3],
            "credit_score": random.choice(["excellent", "good", "fair"]),
            "prefers_installments": random.random() > 0.4,
            "payment_methods": "|".join(methods),
            "preferred_payment": random.choice(methods),
            "preferred_sectors": "|".join(pref_sectors),
            "price_sensitivity": random.choice(["high", "medium", "low"]),
            "eco_conscious": random.random() > 0.5,
            "loyalty_points": random.randint(0, 15000),
            "total_orders": random.randint(0, 150),
            "lifetime_value": round(random.uniform(100, 75000), 2),
            "created_at": fake.date_time_between("-5y", "-3m").isoformat(),
            "last_login": fake.date_time_between("-30d", "now").isoformat()
        }
        user["full_name"] = f"{user['first_name']} {user['last_name']}"
        user["embedding"] = make_embed(f"{tier[0]} {' '.join(pref_sectors)}")
        users.append(user)
    return users

def gen_behaviors(n, prods, users):
    print(f"🖱️ Generating {n} behaviors...")
    behaviors = []
    events = ["search", "view", "click", "add_to_cart", "purchase", "wishlist"]
    weights = [0.28, 0.35, 0.17, 0.12, 0.05, 0.03]
    queries = ["laptop for work", "wireless headphones", "running shoes", "red wine gift",
               "skincare routine", "home office chair", "summer dress", "protein powder",
               "smart watch fitness", "organic coffee", "gaming laptop", "yoga mat"]
    
    for i in range(n):
        user = random.choice(users)
        evt = random.choices(events, weights=weights)[0]
        prod = random.choice(prods)
        
        beh = {
            "id": str(uuid.uuid4()),
            "event_id": f"EVT-{i+1:06d}",
            "user_id": user["user_id"],
            "event_type": evt,
            "timestamp": fake.date_time_between("-90d", "now").isoformat(),
            "session_id": f"SES-{uuid.uuid4().hex[:8]}",
            "device": random.choice(["mobile", "desktop", "tablet"]),
            "browser": random.choice(["Chrome", "Safari", "Firefox", "Edge"]),
            "source": random.choice(["organic", "paid", "social", "email", "direct"]),
            "product_id": "" if evt == "search" else prod["product_id"],
            "product_name": "" if evt == "search" else prod["name"],
            "product_category": "" if evt == "search" else prod["category"],
            "product_sector": "" if evt == "search" else prod["sector"],
            "product_price": 0 if evt == "search" else prod["price"],
            "search_query": random.choice(queries) if evt == "search" else "",
            "time_on_page_sec": random.randint(10, 600) if evt in ["view", "click"] else 0,
            "quantity": random.randint(1, 3) if evt in ["add_to_cart", "purchase"] else 0,
            "order_total": 0,
            "payment_method": ""
        }
        if evt == "purchase":
            beh["order_total"] = round(beh["product_price"] * beh["quantity"], 2)
            beh["payment_method"] = random.choice(user["payment_methods"].split("|"))
        
        beh["embedding"] = make_embed(beh["search_query"] if evt == "search" else f"{evt} {prod['category']}")
        behaviors.append(beh)
    return behaviors

def gen_reviews(n, prods, users):
    print(f"⭐ Generating {n} reviews...")
    reviews = []
    pos = ["Excellent quality!", "Best purchase ever!", "Highly recommend!", "Exceeded expectations!", "Love it!"]
    neg = ["Disappointed.", "Not worth the price.", "Poor quality.", "Would not recommend."]
    neu = ["Decent product.", "Gets the job done.", "As expected.", "Average quality."]
    
    for i in range(n):
        prod = random.choice(prods)
        user = random.choice(users)
        rating = random.choices([1, 2, 3, 4, 5], weights=[0.03, 0.07, 0.15, 0.35, 0.40])[0]
        
        if rating >= 4:
            title = random.choice(pos)
            sentiment = "positive"
            body = f"{title} The {prod['brand']} {prod['model']} is exactly what I needed. Great {random.choice(['quality', 'value', 'design', 'performance'])}. Would definitely buy again."
        elif rating <= 2:
            title = random.choice(neg)
            sentiment = "negative"
            body = f"{title} The {prod['brand']} {prod['model']} did not meet my expectations. {random.choice(['Overpriced', 'Broke quickly', 'Poor materials'])}. Looking for alternatives."
        else:
            title = random.choice(neu)
            sentiment = "neutral"
            body = f"{title} The {prod['brand']} {prod['model']} is okay for the price. {random.choice(['Nothing special', 'Does the job', 'Average experience'])}."
        
        rev = {
            "id": str(uuid.uuid4()),
            "review_id": f"REV-{i+1:06d}",
            "product_id": prod["product_id"],
            "product_name": prod["name"],
            "product_category": prod["category"],
            "product_sector": prod["sector"],
            "user_id": user["user_id"],
            "user_name": user["full_name"],
            "rating": rating,
            "title": title,
            "body": body,
            "sentiment": sentiment,
            "helpful_votes": random.randint(0, 200),
            "verified_purchase": random.random() > 0.15,
            "created_at": fake.date_time_between("-1y", "now").isoformat()
        }
        rev["embedding"] = make_embed(f"{title} {body}")
        reviews.append(rev)
    return reviews

def save_csv(data, name, out_dir):
    df = pd.DataFrame([{k: v for k, v in d.items() if k != "embedding"} for d in data])
    path = os.path.join(out_dir, f"{name}.csv")
    df.to_csv(path, index=False)
    print(f"   ✓ {name}.csv ({len(data)} rows)")

def main():
    print("="*60)
    print("  FinCommerce Engine - Database Generator v2")
    print("="*60)
    
    Path(OUT_DIR).mkdir(exist_ok=True)
    
    # Generate data
    prods = gen_products(NUM_PRODUCTS)
    users = gen_users(NUM_USERS)
    behs = gen_behaviors(NUM_BEHAVIORS, prods, users)
    revs = gen_reviews(NUM_REVIEWS, prods, users)
    
    # Save CSVs
    print("\n📄 Saving CSV files...")
    save_csv(prods, "products", OUT_DIR)
    save_csv(users, "users", OUT_DIR)
    save_csv(behs, "behaviors", OUT_DIR)
    save_csv(revs, "reviews", OUT_DIR)
    
    # Stats CSV
    stats = []
    for sector in set(p["sector"] for p in prods):
        sp = [p for p in prods if p["sector"] == sector]
        stats.append({
            "sector": sector,
            "product_count": len(sp),
            "min_price": min(p["price"] for p in sp),
            "max_price": max(p["price"] for p in sp),
            "avg_price": round(sum(p["price"] for p in sp) / len(sp), 2),
            "avg_rating": round(sum(p["avg_rating"] for p in sp) / len(sp), 2)
        })
    save_csv(stats, "sector_stats", OUT_DIR)
    
    # Qdrant (optional)
    if QDRANT_OK:
        print("\n🗄️ Loading to Qdrant...")
        Path(DB_PATH).mkdir(exist_ok=True)
        client = QdrantClient(path=DB_PATH)
        for coll in ["products", "users", "behaviors", "reviews"]:
            try: client.delete_collection(coll)
            except: pass
            client.create_collection(coll, vectors_config=VectorParams(size=384, distance=Distance.COSINE))
        
        def load(coll, data):
            pts = [PointStruct(id=i, vector=d["embedding"], payload={k:v for k,v in d.items() if k!="embedding"}) for i,d in enumerate(data)]
            for j in range(0, len(pts), 100):
                client.upsert(coll, pts[j:j+100])
        
        load("products", prods)
        load("users", users)
        load("behaviors", behs)
        load("reviews", revs)
        print("   ✓ Qdrant loaded")
    
    print(f"\n{'='*60}")
    print("✅ COMPLETE!")
    print(f"{'='*60}")
    print(f"\nFiles: {OUT_DIR}/")
    print(f"  • products.csv ({NUM_PRODUCTS} products)")
    print(f"  • users.csv ({NUM_USERS} users)")
    print(f"  • behaviors.csv ({NUM_BEHAVIORS} events)")
    print(f"  • reviews.csv ({NUM_REVIEWS} reviews)")
    print(f"  • sector_stats.csv (7 sectors)")
    if QDRANT_OK:
        print(f"\nQdrant: {DB_PATH}/")

if __name__ == "__main__":
    main()
