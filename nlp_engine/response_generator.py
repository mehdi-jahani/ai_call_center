import pandas as pd
import os
import re
from collections import Counter

# مسیر فایل CSV
PRODUCTS_CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/products.csv')

# بارگذاری اطلاعات محصولات از CSV
products_df = pd.DataFrame() # مقداردهی اولیه برای جلوگیری از خطا
try:
    products_df = pd.read_csv(PRODUCTS_CSV_PATH)
    print(f"Products loaded successfully from: {PRODUCTS_CSV_PATH}")
    # تبدیل نام ستون ها به lowercase و snake_case
    products_df.columns = [col.lower().replace(' ', '_') for col in products_df.columns]

except FileNotFoundError:
    print(f"Error: products.csv not found at {PRODUCTS_CSV_PATH}. Please ensure the file exists.")
except Exception as e:
    print(f"An error occurred while loading products.csv: {e}")

def get_keywords_from_text(text):
    """Extracs alphanumeric words from a string and converts to lowercase."""
    if pd.isna(text):
        return []
    return re.findall(r'\b\w+\b', str(text).lower())

def generate_response(message: str) -> str:
    message_lower = message.lower()
    message_words = get_keywords_from_text(message_lower)

    # General messages
    if "hello" in message_lower or "hi" in message_lower:
        return "Hello! How can I assist you with our products today?"
    if "bye" in message_lower or "goodbye" in message_lower:
        return "Goodbye! Feel free to ask if you have more questions later."
    if "what do you sell" in message_lower or "what products" in message_lower or "list products" in message_lower:
        if not products_df.empty:
            categories = products_df['category'].dropna().unique().tolist()
            if categories:
                return f"We sell a variety of products, including items in categories like: {', '.join(categories)}. What are you interested in?"
            else:
                return "I don't have categories defined, but I can tell you about specific products if you ask."
        else:
            return "I'm sorry, I don't have product information available at the moment."

    best_match_product = None
    max_score = 0

    # 1. Prioritize exact ID match
    id_match = re.search(r'\b(\d{4,})\b', message_lower)
    if id_match:
        product_id = int(id_match.group(1))
        found_by_id = products_df[products_df['id'] == product_id]
        if not found_by_id.empty:
            best_match_product = found_by_id.iloc[0]
            max_score = 1000 # Give a very high score for exact ID match
            # Proceed to generate response directly since ID is highly specific
            return format_product_response(best_match_product, message_lower)


    # 2. Score based on keyword overlap (Title, Description, Variation)
    for index, row in products_df.iterrows():
        current_score = 0
        product_keywords = []

        if pd.notna(row.get('title')):
            # Prioritize full title match
            if str(row['title']).lower() in message_lower:
                current_score += 100 # High score for exact title match
            product_keywords.extend(get_keywords_from_text(row['title']))

        if pd.notna(row.get('description')):
            product_keywords.extend(get_keywords_from_text(row['description']))

        if pd.notna(row.get('variation')):
            # Prioritize full variation match
            if str(row['variation']).lower() in message_lower:
                current_score += 50 # Good score for exact variation match
            product_keywords.extend(get_keywords_from_text(row['variation']))
        
        # Calculate overlap of individual words
        overlap_words = set(message_words) & set(product_keywords)
        current_score += len(overlap_words) * 10 # Each overlapping keyword adds 10 points

        if current_score > max_score:
            max_score = current_score
            best_match_product = row

    # 3. Handle found product or category search
    if best_match_product is not None and max_score > 0: # Ensure at least some match occurred
        return format_product_response(best_match_product, message_lower)
    
    # Search by Category (if no specific product found)
    for category in products_df['category'].dropna().unique():
        if category.lower() in message_lower:
            category_products = products_df[products_df['category'].str.lower() == category.lower()]
            if not category_products.empty:
                titles = ", ".join(category_products['title'].tolist())
                return f"In the '{category}' category, we have: {titles}. What specific item are you looking for?"
    
    # Fallback if no match
    return "I'm sorry, I couldn't find information about that product or category. Can you please specify what you are looking for?"

def format_product_response(product_row, message_lower):
    """Helper function to format the response for a found product."""
    response = f"Regarding '{product_row['title']}' (ID: {product_row['id']}). "
    
    # Check for price
    if "price" in message_lower or "cost" in message_lower:
        response += f"Its price is ${product_row['price']}. "
    
    # Check for description
    if "description" in message_lower or "about" in message_lower or "what is" in message_lower:
        if pd.notna(product_row.get('description')):
            response += f"Description: {product_row['description']}. "
        else:
            response += "No specific description is available. "
    
    # Check for variation
    if "variation" in message_lower or "type" in message_lower:
        if pd.notna(product_row.get('variation')):
            response += f"It has a variation: '{product_row['variation']}'. "
        else:
            response += "No specific variation is mentioned. "
    
    # Check for category
    if "category" in message_lower or "which category" in message_lower:
        response += f"It belongs to the '{product_row['category']}' category. "
        
    # If no specific keyword, provide general info
    if not ("price" in message_lower or "cost" in message_lower or \
            "description" in message_lower or "about" in message_lower or \
            "variation" in message_lower or "type" in message_lower or \
            "category" in message_lower):
        response += f"It costs ${product_row['price']} and is in the '{product_row['category']}' category."
    
    return response.strip()