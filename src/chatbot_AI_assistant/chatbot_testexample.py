# test_chatbot.py
import requests
import json

BASE_URL = 'http://localhost:5000/api'

def test_chat(message, user_data=None):
    """Send a message to the chatbot"""
    response = requests.post(
        f'{BASE_URL}/chat',
        json={
            'message': message,
            'user_data': user_data or {}
        }
    )
    return response.json()

def test_init_chat(user_data=None):
    """Initialize chat"""
    response = requests.post(
        f'{BASE_URL}/chat/init',
        json={'user_data': user_data or {}}
    )
    return response.json()

def test_quick_chat(suggestion, user_data=None):
    """Test quick chat suggestion"""
    response = requests.post(
        f'{BASE_URL}/chat/quick',
        json={
            'suggestion': suggestion,
            'user_data': user_data or {}
        }
    )
    return response.json()

def get_chat_history():
    """Get chat history"""
    response = requests.get(f'{BASE_URL}/chat/history')
    return response.json()


if __name__ == '__main__':
    # Example user data
    user_data = {
        'name': 'Ahmed',
        'monthly_budget': 2000,
        'current_budget': 1500,
        'cart_total': 150,
        'total_spent': 350
    }
    
    print("=== Testing Chatbot ===\n")
    
    # Initialize chat
    print("1. Initialize Chat:")
    result = test_init_chat(user_data)
    print(f"Response: {result['response']}\n")
    print(f"Suggestions: {result['suggestions']}\n")
    
    # Test search help
    print("2. Ask about search:")
    result = test_chat("How to search for products?", user_data)
    print(f"Response: {result['response']}\n")
    print(f"Suggestions: {result['suggestions']}\n")
    
    # Test budget help
    print("3. Ask about budget:")
    result = test_chat("Tell me about my budget", user_data)
    print(f"Response: {result['response']}\n")
    print(f"Suggestions: {result['suggestions']}\n")
    
    # Test checkout help
    print("4. Ask about checkout:")
    result = test_chat("How to checkout?", user_data)
    print(f"Response: {result['response']}\n")
    print(f"Suggestions: {result['suggestions']}\n")
    
    # Get chat history
    print("5. Chat History:")
    history = get_chat_history()
    print(f"Total messages: {len(history['history'])}\n")