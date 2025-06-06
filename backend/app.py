from flask import Flask, render_template, request, jsonify
import json
import os
import pandas as pd
import ast
import numpy as np
from flask_cors import CORS

# Paths
current_directory = os.path.dirname(os.path.abspath(__file__))
json_file_path_sephora = os.path.join(current_directory, 'filtered_sephora_products.json')
json_file_path_reviews = os.path.join(current_directory, 'review_terms_per_product.json')

# Load data
with open(json_file_path_sephora, 'r') as file:
    dat_sephora = json.load(file)
    df_sephora = pd.DataFrame(dat_sephora)

with open(json_file_path_reviews, 'r') as file:
    dat_reviews = json.load(file)
    df_reviews = pd.DataFrame(dat_reviews)

# Initialize app
app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('base.html')

@app.route('/ingredients', methods=['GET'])
def get_ingredients():
    try:
        flat_list = [item for sublist in df_sephora.ingredients_clean.dropna() for item in sublist]
        ingredients = list(set(flat_list))
        ingredients = sorted(ingredients)
        return jsonify({"ingredients": ingredients})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/brands', methods=['GET'])
def get_brands():
    try:
        brands = sorted(df_sephora['brand_name'].dropna().unique().tolist())
        return jsonify({"brands": brands})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Helper functions
def jaccard_similarity(a, b):
    set_a = set(a.lower().split())
    set_b = set(b.lower().split())
    return len(set_a & set_b) / len(set_a | set_b) if len(set_a | set_b) > 0 else 0

def highlight_matches_skin_type(row, user_skin_type):
    highlights = row.get('highlights')
    if highlights == "":
        return True
    if isinstance(highlights, str):
        try:
            highlights = ast.literal_eval(highlights)
        except (ValueError, SyntaxError):
            return True
    found_best_for = False
    for h in highlights:
        if isinstance(h, str) and "best for" in h.lower():
            found_best_for = True
            try:
                tag_section = h.lower().split("best for", 1)[1].strip()
                if user_skin_type.lower() in tag_section:
                    return True
            except IndexError:
                continue
    return not found_best_for

def highlight_matches_skin_concerns(row, user_skin_concerns):
    highlights = row.get('highlights')
    if highlights == "":
        return True
    if isinstance(highlights, str):
        try:
            highlights = ast.literal_eval(highlights)
        except (ValueError, SyntaxError):
            return True
    found_good_for = False
    for h in highlights:
        if isinstance(h, str) and "good for" in h.lower():
            found_good_for = True
            tag_section = h.lower().split("good for", 1)[1].strip(": ").lower()
            for concern in user_skin_concerns:
                if concern.lower() in tag_section:
                    return True
    return not found_good_for

def highlight_matches_restrictions(row, restrictions):
    highlights = row.get("highlights", "")
    if highlights == "":
        return True
    if isinstance(highlights, str):
        try:
            highlights = ast.literal_eval(highlights)
        except (ValueError, SyntaxError):
            return True
    highlights = [h.lower() for h in highlights if isinstance(h, str)]
    restrictions_lower = [r.lower() for r in restrictions]
    for restriction in restrictions_lower:
        if not any(restriction in h for h in highlights):
            return False
    return True

def filter_by_ingredients(row, selected_ingredients, exclude=False):
    ingredients_raw = row.get("ingredients_clean", "")
    if not selected_ingredients or ingredients_raw == "":
        return True
    try:
        product_ings = (
            ingredients_raw
            if isinstance(ingredients_raw, list)
            else ast.literal_eval(ingredients_raw)
        )
    except Exception:
        return True
    product_ings = [i.lower().strip() for i in product_ings]
    sel = [i.lower().strip() for i in selected_ingredients]
    if exclude:
        # keep only those WITHOUT any of the selected ingredients
        return all(i not in product_ings for i in sel)
    else:
        # keep only those WITH *all* of the selected ingredients
        return all(i in product_ings for i in sel)

def category_match_or_in_name(row, user_query):  # <-- modified
    categories = []
    if isinstance(row.get("primary_category"), str):
        categories.append(row["primary_category"])
    if isinstance(row.get("secondary_category"), str):
        categories.append(row["secondary_category"])
    if isinstance(row.get("tertiary_category"), str):
        categories.append(row["tertiary_category"])

    product_name = row.get("product_name", "").lower()
    query_lower = user_query.lower()

    # Exception: if query appears in product name, don't filter out
    if query_lower in product_name:
        return True

    if not categories:
        return True

    category_words = " ".join(categories).lower().split()
    query_words = query_lower.split()

    for q_word in query_words:
        if q_word in category_words:
            return True

    return False

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    # Extract user inputs
    skin_concerns = data.get("skin_concerns", [])
    skin_type = data.get("skin_type", "normal").lower().strip()
    brand_names = data.get("brand_names", [])
    price_range = data.get("price_range", [0, 200])
    restrictions = data.get("restrictions", [])
    ingredients = data.get("ingredients", [])
    exact_product_search = data.get("user_search_input", "").lower().strip()
   
    exclude_ingredients = data.get("exclude_ingredients", False)
    exclude_brands = data.get("exclude_brands", False)


    price_min = float(price_range[0])
    price_max = float(price_range[1])

    use_price = (price_min != 0) or (price_max != 200)
    use_brand = brand_names != []
    use_restrictions = restrictions != []
    use_ingredients = ingredients != []
    use_exact_product_search = exact_product_search != ""

    filtered_df = df_sephora.copy()

    if use_price:
        filtered_df = filtered_df[(filtered_df['price_usd'] >= price_min) & (filtered_df['price_usd'] <= price_max)]


    if use_brand:
        bn_lower = [b.lower().strip() for b in brand_names]
        if exclude_brands:
            filtered_df = filtered_df[
                ~filtered_df['brand_name'].str.lower().str.strip().isin(bn_lower)
            ]
        else:
            filtered_df = filtered_df[
                filtered_df['brand_name'].str.lower().str.strip().isin(bn_lower)
            ]

    filtered_df = filtered_df[
        filtered_df.apply(
            lambda row: filter_by_ingredients(row, ingredients, exclude_ingredients),
            axis=1
        )
    ]



    if use_restrictions:
        filtered_df = filtered_df[filtered_df.apply(lambda row: highlight_matches_restrictions(row, restrictions), axis=1)]

    if skin_type:
        filtered_df = filtered_df[filtered_df.apply(lambda row: highlight_matches_skin_type(row, skin_type), axis=1)]

    if skin_concerns:
        filtered_df = filtered_df[filtered_df.apply(lambda row: highlight_matches_skin_concerns(row, skin_concerns), axis=1)]

    if use_exact_product_search:
        filtered_df = filtered_df[filtered_df.apply(lambda row: category_match_or_in_name(row, exact_product_search), axis=1)]  # <-- modified

    relevant_doc_inds = []
    if use_exact_product_search:
        for i in range(len(filtered_df['product_name'])):
            row = filtered_df.iloc[i]
            product_name = row['product_name']
            rating = row['rating']
            highlights = row['highlights']
            ingredients_clean = row['ingredients_clean']

            sim_name = jaccard_similarity(exact_product_search, product_name)
            sim_highlights = 0
            if isinstance(highlights, str):
                try:
                    highlights_list = ast.literal_eval(highlights)
                    highlights_text = " ".join(highlights_list)
                    sim_highlights = jaccard_similarity(exact_product_search, highlights_text)
                except (ValueError, SyntaxError):
                    pass

            sim_ingredients = 0
            if isinstance(ingredients_clean, list):
                ingredients_text = " ".join(ingredients_clean)
                sim_ingredients = jaccard_similarity(exact_product_search, ingredients_text)

            rating_normalized = rating / 5 if not np.isnan(rating) else 0

            # New term: 10% if product has non-empty product_terms
            has_terms = 0
            review_row = df_reviews[df_reviews['product_name'] == product_name]
            if not review_row.empty:
                terms = review_row['important_terms'].iloc[0]
                if isinstance(terms, list) and len(terms) > 0:
                    has_terms = 1

            final_score = (
                0.55 * sim_name +
                0.15 * sim_highlights +
                0.10 * sim_ingredients +
                0.10 * rating_normalized +
                0.10 * has_terms
            )

            relevant_doc_inds.append((product_name, round(final_score, 4), float(row["price_usd"]), row["brand_name"]))
        
        top_5_relevant_docs = sorted(relevant_doc_inds, key=lambda x: x[1], reverse=True)[:5]
    else:
        top_5_relevant_docs = [
            [row["product_name"], 0, row["price_usd"], row["brand_name"]]
            for _, row in filtered_df.head(5).iterrows()
        ]

    # Add review info
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
            highlights_list = ast.literal_eval(highlights_str)
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
    port = int(os.environ.get("PORT", 5225))
    app.run(host="0.0.0.0", port=port)
