# 🔥 Smart9adhya

<div align="center">

![Smart9adhya Banner](https://img.shields.io/badge/Smart9adhya-AI%20Powered%20E--Commerce-F59E0B?style=for-the-badge&logo=shopify&logoColor=white)

**An AI-Powered E-Commerce Platform with RAG-Based Recommendations and Computer Vision**

[![Qdrant](https://img.shields.io/badge/Vector%20DB-Qdrant-24A7FA?logo=data:image/png;base64,iVBORw0KGgo=)](https://qdrant.tech/)

[Features](#-features) • [Architecture](#-architecture) • [Installation](#-installation) • [Usage](#-usage) • [Documentation](#-documentation)

</div>

---
## 😎Overfitters team :
- Mahmoud Kannou 
- Mohamed Arbi Ben Lakhal 
- Ahmed Karmous Jedaa 
- Rayen Dahmen 
## 📋 Overview

**Smart9adhya** is a next-generation fincommerce platform that combines **Retrieval-Augmented Generation (RAG)** with **Computer Vision** to deliver intelligent, budget-aware product recommendations. Unlike traditional search systems, Smart9adhya understands user intent, analyzes images, and provides transparent explanations for every recommendation.

### 🎯 Problem Statement

Traditional e-commerce platforms suffer from:
- **Keyword-based search** fails to understand semantic intent
- **Image search** lacks intelligent category detection
- **No budget awareness** in recommendations
- **Black-box recommendations** without explanations

### 💡 Our Solution

Smart9adhya addresses these challenges through:
- **Semantic Search** that understands what you mean, not just what you type
- **Computer Vision** that analyzes images at pixel-level for accurate matching
- **Budget-First Design** that respects your financial constraints
- **Explainable AI** that tells you why products are recommended

---

## ✨ Features

### 🧠 RAG-Based Recommendation Engine
- Semantic product indexing across multiple dimensions
- Multi-factor similarity scoring (category, keywords, colors, materials)
- Intent detection (budget, premium, trending, healthy, tech)
- Real-time query understanding

### 👁️ Computer Vision System
- **Color Extraction**: 13 color families with RGB-based detection
- **Texture Analysis**: Smoothness, patterns, and fabric detection
- **Structure Analysis**: Edge density, brightness, contrast
- **Category Detection**: Fashion, Electronics, Furniture, Food, Cosmetics

### 💰 Budget-Aware Shopping
- Automatic product filtering based on budget constraints
- Separate monthly and current budget tracking
- Budget alerts and spending analytics
- Products priced above budget are hidden automatically

### 🎮 XP & Rewards System
- Earn XP points on every purchase (10 XP per $1)
- Bonus XP for large orders
- Refund system with XP compensation
- Use XP as discount on future purchases

### 👤 User Profile Management
- Payment methods (multiple cards)
- Delivery addresses with instructions
- Shopping preferences
- Order history

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                             │
│         [Search Bar]  [Image Upload]  [Filters]                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    QUERY PROCESSING LAYER                       │
│  ┌─────────────────┐              ┌─────────────────────┐       │
│  │  Text Analyzer  │              │  Vision Analyzer    │       │
│  │  - Intent Det.  │              │  - Color Extract.   │       │
│  │  - Keyword Ext. │              │  - Shape Analysis   │       │
│  │  - Semantic Emb.│              │  - Texture Detect.  │       │
│  └────────┬────────┘              └──────────┬──────────┘       │
└───────────┼──────────────────────────────────┼──────────────────┘
            │                                  │
            ▼                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RAG MATCHING ENGINE                          │
│         Semantic Similarity + Budget Filter + Ranking           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    QDRANT VECTOR DATABASE                       │
│              2000+ Product Embeddings with Metadata             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RESPONSE GENERATION                          │
│         Ranked Results + Match Scores + Explanations            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Vanilla JavaScript + HTML5 | UI and interactions |
| **Vision** | PIL | Image processing |
| **Styling** | CSS3 + CSS Variables | Dark theme, responsive |
| **Vector DB** | Qdrant | Product embeddings |
| **Search** | Custom RAG Engine | Semantic matching |
| **Storage** | LocalStorage | User data persistence |

---

## 📦 Installation

### Prerequisites
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Node.js (optional, for local server)
- Python 3.8+ (for backend features)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/smart9adhya.git
   cd smart9adhya
   ```

2. **Open in browser**
   ```bash
   # Option 1: Direct file opening
   open index.html
   
   # Option 2: Local server (recommended)
   python -m http.server 8000
   # Then visit http://localhost:8000
   # option3: using python manage.py runserver
   Notice: you should open the smart9adhya-django folder
   ```

3. **Or use with Node.js**
   ```bash
   npx serve .
   ```

---

## 🚀 Usage

### Text Search
```
Enter keywords in the search bar:
- "affordable wireless headphones" → Budget-aware tech search
- "premium organic skincare" → Intent-detected search
- "red dress for party" → Color + occasion matching
```

### Image Search
1. Click the 📷 camera icon in the search bar
2. Upload a product image
3. Watch the 4-step analysis:
   - 🔍 Visual feature extraction
   - 🏷️ Image analysis
   - 🎨 Color and shape detection
   - 🔗 RAG matching
4. View matched products with confidence scores

### Budget Management
- Set your monthly budget during registration
- Budget automatically filters all product displays
- View detailed breakdown: Monthly | Spent | Remaining

---

## 📊 RAG Implementation Details

### Product Embedding Structure
```javascript
{
    category: "Fashion",           // Main sector
    subcategory: "T-Shirts",       // Sub-category
    brand: "Nike",                 // Brand name
    priceRange: "mid-range",       // budget/mid/premium/luxury
    keywords: ["casual", "cotton"],// Extracted terms
    colors: ["blue", "white"],     // Detected colors
    materials: ["cotton"],         // Material types
    useCases: ["casual", "sports"] // Usage contexts
}
```

### Similarity Scoring
| Factor | Points | Description |
|--------|--------|-------------|
| Category Match | +40 | Same product sector |
| Subcategory Match | +20 | Same category |
| Price Range Match | +10 | Similar tier |
| Keyword Overlap | up to +30 | Jaccard similarity |
| Color Match | +15 | Matching colors |
| Use Case Match | +10 | Similar context |

### Intent Detection
| Intent | Keywords | Effect |
|--------|----------|--------|
| 💰 Budget | cheap, affordable | Prioritize lower prices |
| ✨ Premium | best, luxury, quality | Prioritize ratings |
| 🔥 Trending | popular, hot, new | Prioritize popularity |
| 🌿 Healthy | organic, natural, vitamin | Filter health products |
| 📱 Tech | smart, wireless, bluetooth | Filter electronics |

---

## 📁 Project Structure

```
smart9adhya/
├── index.html              # Main application
├── products_data.js        # Product catalog (2000+ items)
├── README.md               # This file
├── docs/
│   └── technical_report.pdf # Detailed documentation
├── qdrant_db/
│   └── meta.json      #metadata
│   └── Collections
│      └──behaviors
│      │   └──storage.sqlite
│      └──products
│      │   └──storage.sqlite       
│      └──reviews   
│      │   └──storage.sqlite
│      └──users
│          └──storage.sqlite
├──assets           #4 synthetic datasets
│                   # Product images
│
├──smart9adhya-django # the django environment for the website (with local database)
│
└── src/# Extrait du code des fonctionalités principales
    ├── make_qdrant_collection/              # make_qdrant collections
    │   └── Embedding.py       
    ├── rag+explanation/                  # RAG engine
    │   └── Fetching.py
    └── chatbot_Ai_assistant/                   #based on natural language
        └──chatbot_technical.py

The smart9adhya-django folder architecture
smart9adhya-django/
├── smart9adhya/              # Main project config
│   ├── settings.py           # Django settings
│   ├── urls.py               # URL routing
│   ├── templates/base.html   # Base template
│   └── static/               # CSS, JS files
├── users/                    # User authentication & profiles
│   ├── models.py             # User, PaymentCard, Address
│   ├── views.py              # Login, Register, Profile
│   └── forms.py              # User forms
├── products/                 # Product catalog
│   ├── models.py             # Product, Cart, Wishlist
│   ├── views.py              # Home, Shop, Detail, Cart
│   └── templates/            # Product templates
├── orders/                   # Order management
│   ├── models.py             # Order, OrderItem, Refund
│   └── views.py              # Checkout, Order history
├── search/                   # RAG Search engine
│   ├── qdrant_service.py     # Qdrant integration
│   └── views.py              # Search views
├── api/                      # REST API
│   ├── views.py              # API endpoints
│   └── serializers.py        # DRF serializers
├── scripts/
│   └── seed_products.py      # Database seeder
├── requirements.txt
└── manage.py
```
```

---

## 🗓️ Roadmap

### ✅ Completed (Phase 1-2)
- [x] User authentication system
- [x] Budget management (monthly/current)
- [x] Computer vision image analysis
- [x] Intent detection
- [x] XP rewards system
- [x] Refund system with pending status
- [x] User profile management
- [x] RAG-based semantic search
- [x] Astonishing web interface for better user experience
- [x] Linking all the workflow
- [x] Ai assistant chatbot based on natural language for technical problems



---

## 📖 Documentation

- [Technical Report (PDF)](docs/Smart9adhya_Technical_Report.pdf)
---

---

## 🙏 Acknowledgments

- [Qdrant](https://qdrant.tech/) for vector database technology
- RAG concepts inspired by modern LLM research

---

<div align="center">

**Built with ❤️ for smarter shopping**

[⬆ Back to top](#-smart9adhya)

</div>
