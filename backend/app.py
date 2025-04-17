from flask import Flask, render_template, request, jsonify
import json
import os
import pandas as pd
import nltk
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import ast
import re


# ROOT_PATH for linking with all your files. 
os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..", os.curdir))

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Specify the path to the JSON file relative to the current script
json_file_path_sephora = os.path.join(current_directory, 'filtered_sephora_products.json')
json_file_path_reviews = os.path.join(current_directory, 'review_terms_per_product.json')


# Load the JSON data into a DataFrame
with open(json_file_path_sephora, 'r') as file:
   dat_sephora = json.load(file)
   df_sephora = pd.DataFrame(dat_sephora)


with open(json_file_path_reviews, 'r') as file:
   dat_reviews = json.load(file)
   df_reviews = pd.DataFrame(dat_reviews)


app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    # Render the main search page
    return render_template('base.html')

@app.route('/ingredients', methods=['GET'])
def get_ingredients():
   """ Returns a list of unique ingredients from the dataset. """
   try:
       flat_list = [item for sublist in df_sephora.ingredients_clean.dropna() for item in sublist]
       ingredients = list(set(flat_list))
    #    ingredients = sorted(df_sephora['ingredients'].dropna().unique().tolist())  # Extract unique brands
       return jsonify({"ingredients": ingredients})
   except Exception as e:
       return jsonify({"error": str(e)}), 500

@app.route('/brands', methods=['GET'])
def get_brands():
   """ Returns a list of unique brand names from the dataset. """
   try:
       brands = sorted(df_sephora['brand_name'].dropna().unique().tolist())  # Extract unique brands
       return jsonify({"brands": brands})
   except Exception as e:
       return jsonify({"error": str(e)}), 500

def jaccard_similarity(a, b):
    """Calculate Jaccard similarity between two strings."""
    set_a = set(a.lower().split())
    set_b = set(b.lower().split())
    return len(set_a & set_b) / len(set_a | set_b) if len(set_a | set_b) > 0 else 0

def highlight_matches_skin_type(row, user_skin_type):
    highlights = row.get('highlights')
    product_name = row.get('product_name', 'Unknown')

    # If highlights are empty include the product
    if highlights == "":
        return True

    if isinstance(highlights, str):
        try:
            highlights = ast.literal_eval(highlights)
        except (ValueError, SyntaxError):
            print(f"[ERROR] Failed to parse highlights for {product_name}")
            return True  

    found_best_for = False
    for h in highlights:
        if isinstance(h, str) and "best for" in h.lower():
            found_best_for = True
            try:
                tag_section = h.lower().split("best for", 1)[1].strip()
                if user_skin_type.lower() in tag_section:
                    print(f"[MATCH] {product_name}: matched '{user_skin_type}' in → {h}")
                    return True
            except IndexError:
                continue

    # If no 'Best for' match and highlights exist, allow only if no 'Best for' was found
    return not found_best_for


def highlight_matches_skin_concerns(row, user_skin_concerns):
    highlights = row.get('highlights')
    product_name = row.get('product_name', 'Unknown')

    # If highlights are empty, include the product
    if highlights == "":
        print(f"✅ {product_name}: No highlights — keeping.")
        return True

    # Convert string representation to list
    if isinstance(highlights, str):
        try:
            highlights = ast.literal_eval(highlights)
        except (ValueError, SyntaxError):
            print(f"[ERROR] Could not parse highlights for {product_name}")
            return True

    found_good_for = False
    for h in highlights:
        if isinstance(h, str) and "good for" in h.lower():
            found_good_for = True
            tag_section = h.lower().split("good for", 1)[1].strip(": ").lower()
            for concern in user_skin_concerns:
                concern_lower = concern.lower()
                if concern_lower in tag_section:
                    print(f"[MATCH] {product_name}: matched '{concern}' in → '{tag_section}'")
                    return True

    if not found_good_for:
        print(f"✅ {product_name}: No 'Good for' tags — keeping.")
    else:
        print(f"⛔ {product_name}: No match for concerns → {user_skin_concerns}")

    return not found_good_for


@app.route('/search', methods=['POST'])
def search():
    # Extract user inputs from the form
    # skin_concerns = request.form.getlist("skin_concerns")  # Get list of selected skin concerns
    # brand_name = request.form.get("brand", "Any").lower().strip()
    # price_min = float(request.form.get("price_min", 0))
    # price_max = float(request.form.get("price_max", 200))
    # exact_product_search = request.form.get("query", "").lower().strip()

    data = request.get_json()
    print("Received JSON payload:", data)
    if not data:
        return jsonify({"error": "No JSON data received"}), 400
    skin_concerns = data.get("skin_concerns", [])
    skin_type = data.get("skin_type", "normal").lower().strip()
    brand_names = data.get("brand_names", [])
    price_range = data.get("price_range", [0, 200])
    restrictions = data.get("restrictions", [])
    ingredients = data.get("ingredients", [])
    price_min = float(price_range[0])
    price_max = float(price_range[1])
    exact_product_search = data.get("user_search_input", "").lower().strip()

    # Determine what elements to use in search
    use_price = (price_min != 0) or (price_max != 200)
    use_brand = brand_names != []
    use_restrictions = restrictions != []
    use_ingredients = ingredients != []
    use_exact_product_search = exact_product_search != ""

    # Filter the DataFrame based on user inputs
    filtered_df = df_sephora.copy()

    # Filter by price range
    if use_price:
        filtered_df = filtered_df[
            (filtered_df['price_usd'] >= price_min) & (filtered_df['price_usd'] <= price_max)
        ]

    # Filter by brand name
    if use_brand:
        brand_names = [name.lower().strip() for name in brand_names]  # normalize the list
        filtered_df = filtered_df[filtered_df['brand_name'].str.lower().str.strip().isin(brand_names)]
        # filtered_df = filtered_df[filtered_df['brand_name'].str.lower().str.strip() == brand_name]

    print(f"Skin type selected: {skin_type}")
    print("Applying highlight-based filtering...")

    if skin_type:
        filtered_df = filtered_df[
        filtered_df.apply(lambda row: highlight_matches_skin_type(row, skin_type), axis=1)
    ]
    
    if skin_concerns:
        print(f"📋 Filtering by concerns: {skin_concerns}")
        filtered_df = filtered_df[filtered_df.apply(lambda row: highlight_matches_skin_concerns(row, skin_concerns), axis=1)]

    relevant_doc_inds = []
    if use_exact_product_search:
        for i in range(len(filtered_df['product_name'])):
            product_name = filtered_df["product_name"].iloc[i]
            sim = jaccard_similarity(exact_product_search, product_name)
            relevant_doc_inds.append((
                product_name,
                round(sim, 4),
                float(filtered_df["price_usd"].iloc[i]),
                filtered_df["brand_name"].iloc[i]
            ))
            
        # Sort by similarity and return top 5 matches
        # top_5_relevant_docs = sorted(relevant_doc_inds, key=lambda x: x[1])[:5]  # Lower edit distance is better
        top_5_relevant_docs = sorted(relevant_doc_inds, key=lambda x: x[1], reverse=True)[:5]
    else:
        
        # If no search query, return all filtered products
        # top_5_relevant_docs = filtered_df[["product_name", "price_usd", "brand_name"]].values.tolist()[:5]
        top_5_relevant_docs = [
            [row["product_name"], 0, row["price_usd"], row["brand_name"]]
            for _, row in filtered_df.head(5).iterrows()
        ]
    
    top_5_relevant_docs_w_review = []
    for doc in top_5_relevant_docs:
       product_name = doc[0]
       product = df_sephora[df_sephora['product_name'] == product_name]
       if not product.empty and not np.isnan(product['rating'].iloc[0]):
        product_rating = "⭐ Rating: " + str(round(product['rating'].iloc[0], 2))
       else:
        product_rating = None


       if not product.empty and product['highlights'].iloc[0]:
        highlights_str = product['highlights'].iloc[0]
        highlights_list = ast.literal_eval(highlights_str)  # safely parse string to list
        product_highlights = "✨ Highlights: " + ", ".join(highlights_list)
       else:
        product_highlights = None
       
       reviews = df_reviews[df_reviews['product_name'] == product_name]


       if not reviews.empty and len(reviews['important_terms'].iloc[0]) > 0:
        product_terms = reviews['important_terms'].iloc[0][:3]
        product_terms = "🔑 What users think: " + ", ".join(product_terms)
       else:
        product_terms = None

       top_5_relevant_docs_w_review.append([
       product_name, doc[1], doc[2], doc[3], product_rating, product_terms, product_highlights
       ])

    return jsonify({"results": top_5_relevant_docs_w_review})

if __name__ == '__main__':
    # app.run(debug=True, host="0.0.0.0", port=5013)
    port = int(os.environ.get("PORT", 5225))  # Use PORT if set, otherwise default to 5000
    app.run(host="0.0.0.0", port=port)