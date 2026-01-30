from flask import Flask, request, jsonify
from flask_cors import CORS
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)

class TechnicalSupportChatbot:
    def __init__(self):
        self.chat_history = []
        
    def process_message(self, user_message, user_data=None):
        """Process user message and return bot response"""
        msg = user_message.lower()
        
        # Store message in history
        self.chat_history.append({
            'type': 'user',
            'message': user_message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Process the message and get response
        response = self._get_response(msg, user_data)
        
        # Store bot response in history
        self.chat_history.append({
            'type': 'bot',
            'message': response['text'],
            'timestamp': datetime.now().isoformat()
        })
        
        return response
    
    def _get_response(self, msg, user_data):
        """Determine appropriate response based on message content"""
        
        # ===== HOW TO SEARCH =====
        if any(keyword in msg for keyword in ['search', 'find product', 'how to find']):
            return {
                'text': """🔍 **How to Search Products:**

**1. Text Search:**
- Type keywords in the search bar (top of page)
- Search by product name, brand, or category
- Results show with explanations why they match

**2. Image Search:**
- Click the 📷 camera icon in search bar
- Upload a photo of any product
- We'll find similar items automatically

**3. Browse by Category:**
- Go to Shop page
- Use sector buttons (Electronics, Fashion, etc.)
- Apply filters on the left panel""",
                'suggestions': ['How to filter?', 'Image search help', 'How to checkout?']
            }
        
        # ===== HOW TO FILTER =====
        if any(keyword in msg for keyword in ['filter', 'sort', 'narrow']):
            return {
                'text': """🎯 **How to Filter Products:**

**On the Shop Page:**
- **Price Range:** Set min/max price
- **In Stock Only:** Show available items
- **Free Shipping:** Filter free delivery
- **Installment:** Show pay-monthly options
- **Budget Mode:** Only show what you can afford
- **Rating:** Filter by star rating

**Tip:** Enable "Show Affordable Only" to see products within your remaining budget!""",
                'suggestions': ['How to search?', 'Budget settings', 'How to checkout?']
            }
        
        # ===== CART HELP =====
        if any(keyword in msg for keyword in ['cart', 'add to cart', 'basket']):
            return {
                'text': """🛒 **Cart Guide:**

**Adding Products:**
- Click the + button on any product card
- Or click "Add to Cart" in product details

**Managing Cart:**
- Click cart icon (top right) to open
- Use +/- buttons to change quantities
- Click × to remove items
- Your budget remaining is shown

**Proceed to Checkout:**
- Click "Checkout" button in cart
- Fill in shipping & payment details""",
                'suggestions': ['How to checkout?', 'Payment methods', 'Shipping info']
            }
        
        # ===== CHECKOUT HELP =====
        if any(keyword in msg for keyword in ['checkout', 'pay', 'purchase', 'buy']):
            return {
                'text': """💳 **Checkout Process:**

**Step 1:** Open cart and click "Checkout"

**Step 2:** Fill in your details:
- Contact info (name, email, phone)
- Shipping address
- Payment details (card number, expiry, CVV)

**Step 3:** Review order summary
- Items count
- Subtotal + Tax (10%)
- Free shipping on all orders!

**Step 4:** Click "Pay" to complete

🔒 Your payment is secured with 256-bit SSL encryption""",
                'suggestions': ['Payment methods', 'Return policy', 'Track order']
            }
        
        # ===== PAYMENT HELP =====
        if any(keyword in msg for keyword in ['payment', 'card', 'visa', 'mastercard']):
            return {
                'text': """💳 **Payment Information:**

**Accepted Cards:**
- Visa
- Mastercard

**Card Details Required:**
- Card number (16 digits)
- Expiry date (MM/YY)
- CVV (3 digits on back)
- Cardholder name

**Security:**
🔒 All transactions are encrypted
🔒 We never store your full card number
🔒 PCI DSS compliant checkout""",
                'suggestions': ['Installment options', 'Return policy', 'How to checkout?']
            }
        
        # ===== RETURNS & REFUNDS =====
        if any(keyword in msg for keyword in ['return', 'refund', 'exchange']):
            return {
                'text': """🔄 **Returns & Refunds Policy:**

**Return Window:** 30 days from delivery

**Conditions:**
- Item must be unused
- Original packaging required
- Tags still attached

**Process:**
1. Go to your Orders
2. Select item to return
3. Print return label (free)
4. Drop off at any carrier

**Refund:**
- Processed in 3-5 business days
- Credited to original payment method""",
                'suggestions': ['Start a return', 'Track refund', 'Contact support']
            }
        
        # ===== ACCOUNT HELP =====
        if any(keyword in msg for keyword in ['account', 'profile', 'password', 'login', 'settings']):
            return {
                'text': """👤 **Account Settings:**

**Your Profile:**
- Click your avatar (top right)
- View/edit your information

**Budget Settings:**
- Your monthly budget is set at registration
- Budget resets each month
- Track spending in the budget bar

**Security:**
- Change password in Settings
- Enable 2FA for extra security

**Logout:**
- Click avatar → Logout""",
                'suggestions': ['Change budget', 'Order history', 'How to search?']
            }
        
        # ===== BUDGET HELP =====
        if any(keyword in msg for keyword in ['budget', 'spending', 'afford', 'limit']):
            if user_data:
                monthly_budget = user_data.get('monthly_budget', 2000)
                current_budget = user_data.get('current_budget', 2000)
                cart_total = user_data.get('cart_total', 0)
                total_spent = user_data.get('total_spent', 0)
                available_budget = current_budget - cart_total
                
                return {
                    'text': f"""💰 **Budget Feature Guide:**

**Your Current Status:**
- Monthly Budget (Fixed): ${monthly_budget:.2f}
- Current Budget (Remaining): ${current_budget:.2f}
- In Cart (Pending): ${cart_total:.2f}
- Available Now: ${available_budget:.2f}
- Total Spent This Month: ${total_spent:.2f}

**How It Works:**
- Monthly Budget is set at registration (never changes)
- Current Budget decreases when you complete purchases
- Budget resets to Monthly Budget on the 1st of each month
- Click the budget box in navbar for detailed view

**Tip:** Enable "Budget Mode" in filters to only see affordable items!""",
                    'suggestions': ['Budget mode filter', 'How to filter?', 'View budget details']
                }
            else:
                return {
                    'text': """💰 **Budget Feature Guide:**

**How It Works:**
- Set your monthly budget at registration
- Budget resets each month automatically
- Track spending in real-time
- Get alerts when running low

**Features:**
- Budget-aware product filtering
- Spending analytics
- Monthly reset on 1st of month

**Tip:** Enable "Budget Mode" in filters to only see affordable items!""",
                    'suggestions': ['How to filter?', 'Account settings', 'How to search?']
                }
        
        # ===== WISHLIST HELP =====
        if any(keyword in msg for keyword in ['wishlist', 'favorite', 'save for later']):
            return {
                'text': """❤️ **Wishlist Guide:**

**Adding to Wishlist:**
- Click the heart icon on any product
- Or click ❤️ in product details

**Viewing Wishlist:**
- Click heart icon in navigation bar
- See all saved items
- Move items to cart when ready

**Features:**
- Items saved across sessions
- Quick add to cart from wishlist
- Remove items anytime""",
                'suggestions': ['How to search?', 'Cart guide', 'How to checkout?']
            }
        
        # ===== IMAGE SEARCH HELP =====
        if any(keyword in msg for keyword in ['image', 'photo', 'picture', 'camera']):
            return {
                'text': """📷 **Image Search Guide:**

**How to Use:**
1. Click the camera icon 📷 in search bar
2. Select an image from your device
3. Wait for AI analysis (~2 seconds)
4. Browse similar products!

**What It Detects:**
- Product category (Electronics, Fashion, etc.)
- Colors and patterns
- Similar styles

**Tips:**
- Use clear, well-lit photos
- Single product works best
- Try screenshots from other sites!""",
                'suggestions': ['Text search help', 'How to filter?', 'Browse categories']
            }
        
        # ===== SHIPPING INFO =====
        if any(keyword in msg for keyword in ['shipping', 'delivery', 'track']):
            return {
                'text': """📦 **Shipping Information:**

**Delivery Options:**
- Standard: 5-7 business days (FREE)
- Express: 2-3 business days ($9.99)
- Same Day: Select cities ($19.99)

**Tracking:**
- Check order status in your account
- Tracking number sent via email
- Real-time updates available

**International:**
- Available to 50+ countries
- Duties may apply at customs""",
                'suggestions': ['Return policy', 'Track order', 'Contact support']
            }
        
        # ===== CONTACT / HELP =====
        if any(keyword in msg for keyword in ['contact', 'support', 'help', 'human', 'agent']):
            return {
                'text': """📞 **Contact Support:**

**This Chat:**
- Technical guidance & how-to help
- Available 24/7

**Email Support:**
- support@smart9adhya.com
- Response within 24 hours

**Phone Support:**
- 1-800-SMART9A
- Mon-Fri 9AM-6PM EST

**FAQ:**
- Visit our Help Center for common questions""",
                'suggestions': ['Return policy', 'Payment help', 'Shipping info']
            }
        
        # ===== PRODUCT QUESTIONS (redirect to search) =====
        if any(keyword in msg for keyword in ['show me', 'recommend', 'best', 'cheap', 'deal']):
            return {
                'text': """🔍 **Looking for Products?**

I'm your **technical support** assistant, so I help with how to use the website.

**To find products:**
- Use the **search bar** at the top
- Browse the **Shop page**
- Check **Home page** for recommendations

**Need help searching?** Ask me "how to search" or "how to filter"!""",
                'suggestions': ['How to search?', 'How to filter?', 'Image search help']
            }
        
        # ===== DEFAULT GREETING =====
        if any(keyword in msg for keyword in ['hi', 'hello', 'hey', 'start', 'begin']):
            user_name = user_data.get('name', 'there') if user_data else 'there'
            return {
                'text': f"""👋 Hi {user_name}! I'm your Smart9adhya **Technical Support** assistant.

I can help you with:
- 🔧 How to use the website
- 🛒 Cart & checkout guidance
- 🔍 Search & filter tips
- 👤 Account settings
- 🔄 Returns & refunds info
- ❓ FAQ & troubleshooting

How can I assist you today?""",
                'suggestions': ['How to search?', 'How to checkout?', 'Budget help', 'Return policy']
            }
        
        # ===== DEFAULT =====
        return {
            'text': """🤖 **Technical Support Assistant**

I can help you navigate Smart9adhya:

- **"How to search"** - Find products
- **"How to filter"** - Narrow results
- **"Cart guide"** - Manage your cart
- **"How to checkout"** - Complete purchase
- **"Return policy"** - Returns & refunds
- **"Account help"** - Profile settings
- **"Budget help"** - Spending limits
- **"Image search"** - Search by photo

What do you need help with?""",
            'suggestions': ['How to search?', 'How to checkout?', 'Return policy', 'Budget help']
        }
    
    def get_history(self):
        """Get chat history"""
        return self.chat_history
    
    def clear_history(self):
        """Clear chat history"""
        self.chat_history = []


# Global chatbot instance
chatbot = TechnicalSupportChatbot()


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    data = request.json
    user_message = data.get('message', '')
    user_data = data.get('user_data', {})
    
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400
    
    response = chatbot.process_message(user_message, user_data)
    
    return jsonify({
        'success': True,
        'response': response['text'],
        'suggestions': response.get('suggestions', []),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/chat/history', methods=['GET'])
def get_history():
    """Get chat history"""
    return jsonify({
        'success': True,
        'history': chatbot.get_history()
    })


@app.route('/api/chat/clear', methods=['POST'])
def clear_history():
    """Clear chat history"""
    chatbot.clear_history()
    return jsonify({
        'success': True,
        'message': 'Chat history cleared'
    })


@app.route('/api/chat/quick', methods=['POST'])
def quick_chat():
    """Handle quick chat suggestions"""
    data = request.json
    suggestion = data.get('suggestion', '')
    user_data = data.get('user_data', {})
    
    if not suggestion:
        return jsonify({'error': 'Suggestion is required'}), 400
    
    response = chatbot.process_message(suggestion, user_data)
    
    return jsonify({
        'success': True,
        'response': response['text'],
        'suggestions': response.get('suggestions', []),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/chat/init', methods=['POST'])
def init_chat():
    """Initialize chat with greeting"""
    data = request.json
    user_data = data.get('user_data', {})
    
    response = chatbot.process_message('hello', user_data)
    
    return jsonify({
        'success': True,
        'response': response['text'],
        'suggestions': response.get('suggestions', []),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Smart9adhya Technical Support Chatbot',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)