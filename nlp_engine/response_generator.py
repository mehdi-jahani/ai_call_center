import pandas as pd
import os
import re
import random

PRODUCTS_CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/products.csv')
products_df = pd.DataFrame()

try:
    products_df = pd.read_csv(PRODUCTS_CSV_PATH)
    print(f"Products loaded successfully from: {PRODUCTS_CSV_PATH}")
    products_df.columns = [col.lower().replace(' ', '_') for col in products_df.columns]
    if 'id' in products_df.columns:
        products_df['id'] = pd.to_numeric(products_df['id'], errors='coerce').fillna(0).astype(int)

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

    # --- 1. Handle General Greetings and Farewell messages ---
    if "hello" in message_lower or "hi" in message_lower or "hey" in message_lower:
        return "Hello! How can I assist you with our products today?"
    if "bye" in message_lower or "goodbye" in message_lower or "see you" in message_lower:
        return "Goodbye! Feel free to ask if you have more questions later."

    # --- 2. Handle simple Conversational / Non-Product-Related messages (prioritize these) ---
    if "thank you" in message_lower or "thanks" in message_lower or "i appreciate it" in message_lower:
        return "You're most welcome! Is there anything else I can help you with regarding our products?"
    if "how are you" in message_lower or "what's up" in message_lower:
        return "I'm just a bot, but I'm ready to help you with product information! How can I assist you today!"
    if "tell me a joke" in message_lower or "make me laugh" in message_lower:
        return "Why don't scientists trust atoms? Because they make up everything!"
    if "what is your name" in message_lower or "who are you" in message_lower:
        return "I am an AI Assistant designed to help you with product inquiries. How can I assist you today?"
    if "what can you do" in message_lower or "how can you help" in message_lower:
        return "I can provide information about our products, including their prices, categories, descriptions, images, and links. Just ask me about a product!"
    if "weather" in message_lower:
        return "I'm sorry, I don't have access to real-time weather information. My focus is on product assistance."
    if "news" in message_lower:
        return "I don't have access to current news. I'm here to help with our products. Is there anything I can assist you with?"
    if "ok" in message_lower or "okay" in message_lower or "alright" in message_lower or "sure" in message_lower or "fine" in message_lower:
        return "Okay. Is there something specific you're looking for?"

    # --- 3. Handle explicit "list products" requests ---
    if "what do you sell" in message_lower or "what products" in message_lower or "list products" in message_lower:
        if not products_df.empty:
            categories = products_df['category'].dropna().unique().tolist()
            if categories:
                return f"We sell a variety of products, including items in categories like: {', '.join(categories)}. What are you interested in?"
            else:
                return "I don't have categories defined, but I can tell you about specific products if you ask."
        else:
            return "I'm sorry, I don't have product information available at the moment."
    
    # --- 4. Handle Specific "I want/need a [Product Name]" Intent (Title Only Search with Best Match) ---
    product_request_phrases = ["i want a ", "i need a ", "i'm looking for a ", "find me a "] # Expanded phrases
    is_specific_title_search_intent = False
    requested_product_name = ""

    for phrase in product_request_phrases:
        if message_lower.startswith(phrase):
            # Remove the phrase and then strip leading/trailing whitespace and punctuation
            requested_product_name = message_lower.split(phrase, 1)[1].strip()
            # NEW: Remove trailing punctuation from the requested product name
            requested_product_name = re.sub(r'[.,!?;:]+$', '', requested_product_name).strip()
            is_specific_title_search_intent = True
            break
    
    if is_specific_title_search_intent and requested_product_name:
        common_nouns_that_could_be_product_names = {"item", "product", "device", "thing", "something", "any"} # Expanded
        if requested_product_name in common_nouns_that_could_be_product_names:
            return "Could you please be more specific about the product you are looking for?"

        best_title_match_product = None
        highest_title_match_score = -1

        escaped_requested_name = re.escape(requested_product_name)
        # Try to find the best match based on title
        for index, row in products_df.iterrows():
            product_title_lower = str(row.get('title', '')).lower()
            current_score = 0

            # 1. Exact title match (highest score)
            if product_title_lower == requested_product_name:
                current_score = 1000
            # 2. Starts with the requested name
            elif product_title_lower.startswith(requested_product_name):
                current_score = 500 + (len(requested_product_name) / max(1, len(product_title_lower))) * 100 # Closer to full title is better
            # 3. Contains as a whole word
            elif re.search(r'\b' + escaped_requested_name + r'\b', product_title_lower):
                current_score = 300 + (len(requested_product_name) / max(1, len(product_title_lower))) * 50 # Longer match in shorter title
            # 4. Contains as a substring
            elif requested_product_name in product_title_lower:
                current_score = 100 + (len(requested_product_name) / max(1, len(product_title_lower))) * 20 # Basic substring match

            if current_score > highest_title_match_score:
                highest_title_match_score = current_score
                best_title_match_product = row
            # If scores are equal, prefer shorter title (often more direct)
            elif current_score == highest_title_match_score and best_title_match_product is not None:
                if len(product_title_lower) < len(str(best_title_match_product.get('title', '')).lower()):
                    best_title_match_product = row


        if best_title_match_product is not None and highest_title_match_score >= 100: # Minimum score to consider a good title match
            # If a best match is found, use the standard product formatting function
            return format_product_response(best_title_match_product, products_df, message_lower)
        else:
            # If no good title match found, provide a specific fallback
            return f"I'm sorry, I couldn't find a direct match for '{requested_product_name}' in our product titles. Please try a different name or a more general search, or specify an ID if you know it."

    # --- 5. General Knowledge Query Check (with rule-based fallback) ---
    general_knowledge_phrases = [
        "what is the capital of", "tell me about", "who is", "what is", "where is", "when is",
        "define", "explain", "meaning of", "about", "information about", "general knowledge",
        "history of", "how does", "why does", "what are", "how do i", "can you tell me",
        "tell me something about", "can you explain", "give me details on", "facts about",
        "meaning of life", "universe", "science", "mathematics", "philosophy", "art", "music",
        "geography", "politics", "current events", "celebrity", "biography", "recipe", "tutorial",
        "how to make", "what should i do", "advice", "opinion on", "what about", "is it true",
        "how far", "how many", "what year", "what kind of animal", "who invented", "what's the weather", "latest news"
    ]
    is_general_knowledge_query = any(phrase in message_lower for phrase in general_knowledge_phrases)

    product_indicators = [
        "product", "item", "device", "gadget", "appliance", "tool", "accessory", "component", "part",
        "shaver", "watch", "lamp", "chair", "speaker", "earbuds", "headphone", "charger", "cable",
        "monitor", "keyboard", "mouse", "camera", "tablet", "phone", "tv", "router", "printer",
        "console", "game", "software", "application", "program", "operating system",
        "subscription", "service", "plan", "membership", "license",
        "price", "cost", "value", "rate", "fee", "buy", "sell", "purchase", "order", "acquire", "obtain", "checkout",
        "available", "stock", "in stock", "out of stock", "shipping", "delivery", "return", "refund", "exchange",
        "category", "section", "department", "type of", "kind of", "line of", "collection",
        "electronics", "beauty", "health", "smart home", "furniture", "audio", "video", "computing", "gaming",
        "apparel", "clothing", "shoes", "jewelry", "fashion", "accessories", "wearable",
        "home goods", "kitchen", "outdoor", "sports", "fitness", "books", "media", "entertainment",
        "show me", "looking for", "need a", "do you have", "find me", "recommend", "suggest",
        "details about", "information on", "specifications", "features", "description", "dimensions", "weight", "material", "color", "size",
        "how much", "what is the price", "can I buy", "where can I find", "want to buy", "looking to buy",
        "model", "brand", "version", "series", "type", "compatible with", "warranty", "guarantee", "support"
    ]
    has_strong_product_indicator = any(indicator in message_lower for indicator in product_indicators)

    # If it's a general knowledge query AND lacks strong product indicators, provide rule-based fallback
    if is_general_knowledge_query and not has_strong_product_indicator:
        # Fallback to a rule-based response for general knowledge questions
        return "I'm sorry, I specialize in providing information about our products and services. I cannot answer general knowledge questions. Is there anything product-related I can assist you with?"


    # --- 6. General Product Search (by ID, Title, Description, Variation scoring) ---
    best_match_product = None
    max_score = 0

    # Prioritize exact ID match
    id_match = re.search(r'\b(\d{4,})\b', message_lower)
    if id_match:
        try:
            product_id = int(id_match.group(1))
            found_by_id = products_df[products_df['id'] == product_id]
            if not found_by_id.empty:
                best_match_product = found_by_id.iloc[0]
                max_score = 1000 # Very high score for exact ID match
        except ValueError:
            pass

    # Score based on keyword overlap (Title, Description, Variation) if no strong ID match yet
    if best_match_product is None:
        for index, row in products_df.iterrows():
            current_score = 0
            product_keywords_for_scoring = []

            if pd.notna(row.get('title')):
                title_lower = str(row['title']).lower()
                if title_lower in message_lower:
                    current_score += 100
                product_keywords_for_scoring.extend(get_keywords_from_text(title_lower))

            if pd.notna(row.get('description')):
                product_keywords_for_scoring.extend(get_keywords_from_text(row['description']))

            if pd.notna(row.get('variation')):
                variation_lower = str(row['variation']).lower()
                if variation_lower in message_lower:
                    current_score += 50
                product_keywords_for_scoring.extend(get_keywords_from_text(variation_lower))
            
            overlap_words = set(message_words) & set(product_keywords_for_scoring)
            current_score += len(overlap_words) * 10

            if current_score > max_score:
                max_score = current_score
                best_match_product = row

    # --- Generate response based on found product or related products from general search ---
    if best_match_product is not None and max_score >= 20: # Adjusted threshold for stronger product relevance
        return format_product_response(best_match_product, products_df, message_lower)
    
    # --- 7. Search by Category (if no specific product found with high score) ---
    for category in products_df['category'].dropna().unique():
        if category.lower() in message_lower:
            category_products = products_df[products_df['category'].str.lower() == category.lower()]
            if not category_products.empty:
                top_category_products = category_products.head(6) # Display up to 6 products
                response_html_parts = [f"<p class='category-heading'>In the '{category}' category, we have several items. Here are a few:</p>"]
                response_html_parts.append("<div class='product-list'>")
                for i, prod in top_category_products.iterrows():
                    prod_title_html = ""
                    if pd.notna(prod.get('url')):
                        prod_title_html = f"<a href='{prod['url']}' target='_blank' class='product-item-title'>{prod['title']}</a>"
                    else:
                        prod_title_html = f"<span class='product-item-title'>{prod['title']}</span>"
                    
                    prod_image_html = ""
                    if pd.notna(prod.get('image-url')): # Changed from 'image-url' to 'image-url'
                        prod_image_html = f"<img src='{prod['image-url']}' alt='{prod['title']}' class='product-thumbnail'>"
                    else:
                        prod_image_html = f"<img src='https://placehold.co/90x90/E0E0E0/6C757D?text=No+Image' alt='No image' class='product-thumbnail'>"
                    
                    prod_info_html = (
                        f"<div class='product-item'>"
                        f"{prod_image_html}"
                        f"{prod_title_html}"
                        f"<p class='product-item-price'>${prod['price']}</p>"
                        f"</div>"
                    )
                    response_html_parts.append(prod_info_html)
                response_html_parts.append("</div>")
                return "\n".join(response_html_parts).strip()
    
    # --- 8. Final Fallback for unhandled queries ---
    return "I'm sorry, I don't have information about that. I can help with product-related questions. Can you tell me what product you're interested in?"


def format_product_response(product_row, all_products_df, message_lower):
    """Helper function to format the response for a found product."""
    response_html_parts = []
    
    # Product Card for the main found product
    response_html_parts.append("<div class='product-card-container'>")
    response_html_parts.append("<p class='product-card-main-heading'>We found:</p>")
    response_html_parts.append("<div class='product-main-details'>")

    if pd.notna(product_row.get('image-url')): # Changed from 'image-url' to 'image-url'
        response_html_parts.append(f"<img src='{product_row['image-url']}' alt='{product_row['title']}' class='product-main-image'>")
    else:
        response_html_parts.append(f"<img src='https://placehold.co/120x120/E0E0E0/6C757D?text=No+Image' alt='No image' class='product-main-image'>")

    response_html_parts.append("<div class='main-product-info'>")
    
    if pd.notna(product_row.get('url')):
        response_html_parts.append(f"<a href='{product_row['url']}' target='_blank' class='product-title-link'>{product_row['title']}</a>")
    else:
        response_html_parts.append(f"<span class='product-title-text'>{product_row['title']}</span>")
    
    response_html_parts.append(f"<p class='product-price'>${product_row['price']}</p>")
    response_html_parts.append(f"<p class='product-category'>Category: {product_row['category']}</p>")
    response_html_parts.append("</div></div></div>")

    # Find related products
    related_products = find_related_products(product_row, all_products_df, num_results=6) # Display up to 6 related products
    
    if related_products:
        response_html_parts.append("<p class='related-products-heading'>Perhaps you'd also be interested in these related items:</p>")
        response_html_parts.append("<div class='product-list'>")
        
        for i, prod in enumerate(related_products):
            prod_title_html = ""
            if pd.notna(prod.get('url')):
                prod_title_html = f"<a href='{prod['url']}' target='_blank' class='product-item-title'>{prod['title']}</a>"
            else:
                prod_title_html = f"<span class='product-item-title'>{prod['title']}</span>"
            
            prod_image_html = ""
            if pd.notna(prod.get('image-url')): # Changed from 'image-url' to 'image-url'
                prod_image_html = f"<img src='{prod['image-url']}' alt='{prod['title']}' class='product-thumbnail'>"
            else:
                prod_image_html = f"<img src='https://placehold.co/90x90/E0E0E0/6C757D?text=No+Image' alt='No image' class='product-thumbnail'>"
            
            prod_info_html = (
                f"<div class='product-item'>"
                f"{prod_image_html}"
                f"{prod_title_html}"
                f"<p class='product-item-price'>${prod['price']}</p>"
                f"</div>"
            )
            response_html_parts.append(prod_info_html)
        response_html_parts.append("</div>")
    
    return "\n".join(response_html_parts).strip()


def find_related_products(main_product, all_products_df, num_results=6): # Adjusted num_results to 6
    """
    Finds related products based on category, and then by shared keywords.
    Excludes the main_product itself.
    """
    related = []
    
    # Try to find products in the same category first
    if pd.notna(main_product.get('category')):
        same_category_products = all_products_df[
            (all_products_df['category'].str.lower() == main_product['category'].lower()) &
            (all_products_df['id'] != main_product['id'])
        ]
        related.extend(same_category_products.head(num_results).to_dict('records'))

    # If not enough, try to find based on shared keywords in title/description/variation
    if len(related) < num_results:
        main_product_keywords = set()
        if pd.notna(main_product.get('title')):
            main_product_keywords.update(get_keywords_from_text(main_product['title']))
        if pd.notna(main_product.get('description')):
            main_product_keywords.update(get_keywords_from_text(main_product['description']))
        if pd.notna(main_product.get('variation')):
            main_product_keywords.update(get_keywords_from_text(main_product['variation']))
        
        common_words = {'a', 'an', 'the', 'is', 'it', 'for', 'with', 'and', 'or', 'of', 'in', 'on', 'to', 'from', 'by', 'as', 'are'}
        main_product_keywords = {word for word in main_product_keywords if word not in common_words and len(word) > 2}

        if main_product_keywords:
            scored_products = []
            for index, row in all_products_df.iterrows():
                if row['id'] == main_product['id']:
                    continue
                
                product_keywords = set()
                if pd.notna(row.get('title')):
                    product_keywords.update(get_keywords_from_text(row['title']))
                if pd.notna(row.get('description')):
                    product_keywords.update(get_keywords_from_text(row['description']))
                if pd.notna(row.get('variation')):
                    product_keywords.update(get_keywords_from_text(row['variation']))
                
                overlap_score = len(main_product_keywords.intersection(product_keywords))
                if overlap_score > 0:
                    scored_products.append((overlap_score, row))
            
            scored_products.sort(key=lambda x: x[0], reverse=True)
            for score, prod in scored_products:
                if len(related) < num_results and prod['id'] not in [p['id'] for p in related]:
                    unique_related.append(prod)
                    # Add to related list only if not already there, to avoid duplicates
                    # This check is actually handled by 'seen_ids' at the end, but keeping here for clarity
                    # related.append(prod.to_dict())

    unique_related = []
    seen_ids = set()
    for prod in related:
        if prod['id'] not in seen_ids:
            unique_related.append(prod)
            seen_ids.add(prod['id'])
            if len(unique_related) >= num_results:
                break
    
    return unique_related