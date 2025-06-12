import pandas as pd
import os
import re
import random

# مسیر فایل CSV
PRODUCTS_CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/products.csv')

# بارگذاری اطلاعات محصولات از CSV
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
    """Extracts alphanumeric words from a string and converts to lowercase."""
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

    # --- Find the best matching product ---
    best_match_product = None
    max_score = 0

    # 1. Prioritize exact ID match
    id_match = re.search(r'\b(\d{4,})\b', message_lower)
    if id_match:
        try:
            product_id = int(id_match.group(1))
            found_by_id = products_df[products_df['id'] == product_id]
            if not found_by_id.empty:
                best_match_product = found_by_id.iloc[0]
                max_score = 1000
        except ValueError:
            pass

    # 2. Score based on keyword overlap (Title, Description, Variation) if no strong ID match yet
    if best_match_product is None:
        for index, row in products_df.iterrows():
            current_score = 0
            product_keywords = []

            if pd.notna(row.get('title')):
                if str(row['title']).lower() in message_lower:
                    current_score += 100
                product_keywords.extend(get_keywords_from_text(row['title']))

            if pd.notna(row.get('description')):
                product_keywords.extend(get_keywords_from_text(row['description']))

            if pd.notna(row.get('variation')):
                if str(row['variation']).lower() in message_lower:
                    current_score += 50
                product_keywords.extend(get_keywords_from_text(row['variation']))
            
            overlap_words = set(message_words) & set(product_keywords)
            current_score += len(overlap_words) * 10

            if current_score > max_score:
                max_score = current_score
                best_match_product = row

    # --- Generate response based on found product or related products ---
    if best_match_product is not None and max_score > 0:
        response_html_parts = []
        
        # Product Card for the main found product
        response_html_parts.append("<div class='product-card-container'>")
        response_html_parts.append("<p class='product-card-main-heading'>We found:</p>")
        response_html_parts.append("<div class='product-main-details'>")

        if pd.notna(best_match_product.get('image-url')):
            response_html_parts.append(f"<img src='{best_match_product['image-url']}' alt='{best_match_product['title']}' class='product-main-image'>")
        else:
            # Fallback for no image - can use a placeholder image or simply omit
            response_html_parts.append(f"<img src='https://placehold.co/120x120/E0E0E0/6C757D?text=No+Image' alt='No image' class='product-main-image'>")

        response_html_parts.append("<div class='main-product-info'>")
        
        if pd.notna(best_match_product.get('url')):
            response_html_parts.append(f"<a href='{best_match_product['url']}' target='_blank' class='product-title-link'>{best_match_product['title']}</a>")
        else:
            response_html_parts.append(f"<span class='product-title-text'>{best_match_product['title']}</span>")
        
        response_html_parts.append(f"<p class='product-price'>${best_match_product['price']}</p>")
        response_html_parts.append(f"<p class='product-category'>Category: {best_match_product['category']}</p>")
        response_html_parts.append("</div></div></div>") # Close main-product-info, product-main-details, product-card-container

        # Find related products
        related_products = find_related_products(best_match_product, products_df, num_results=5)
        
        if related_products:
            response_html_parts.append("<p class='related-products-heading'>Perhaps you'd also be interested in these related items:</p>")
            response_html_parts.append("<div class='product-list'>") # Start related products grid
            
            for i, prod in enumerate(related_products):
                prod_title_html = ""
                if pd.notna(prod.get('url')):
                    prod_title_html = f"<a href='{prod['url']}' target='_blank' class='product-item-title'>{prod['title']}</a>"
                else:
                    prod_title_html = f"<span class='product-item-title'>{prod['title']}</span>"
                
                prod_image_html = ""
                if pd.notna(prod.get('image-url')):
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
            response_html_parts.append("</div>") # End related products grid
        
        return "\n".join(response_html_parts).strip()
    
    # Search by Category (if no specific product found with high score)
    for category in products_df['category'].dropna().unique():
        if category.lower() in message_lower:
            category_products = products_df[products_df['category'].str.lower() == category.lower()]
            if not category_products.empty:
                top_category_products = category_products.head(5)
                response_html_parts = [f"<p class='category-heading'>In the '{category}' category, we have several items. Here are a few:</p>"]
                response_html_parts.append("<div class='product-list'>")
                for i, prod in top_category_products.iterrows():
                    prod_title_html = ""
                    if pd.notna(prod.get('url')):
                        prod_title_html = f"<a href='{prod['url']}' target='_blank' class='product-item-title'>{prod['title']}</a>"
                    else:
                        prod_title_html = f"<span class='product-item-title'>{prod['title']}</span>"
                    
                    prod_image_html = ""
                    if pd.notna(prod.get('image-url')):
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
    
    # Fallback if no match at all
    return "I'm sorry, I couldn't find information about that product or category. Can you please specify what you are looking for?"

def find_related_products(main_product, all_products_df, num_results=5):
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
        # Add a few from the same category
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
                    related.append(prod.to_dict())

    unique_related = []
    seen_ids = set()
    for prod in related:
        if prod['id'] not in seen_ids:
            unique_related.append(prod)
            seen_ids.add(prod['id'])
            if len(unique_related) >= num_results:
                break
    
    return unique_related