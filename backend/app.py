from flask import Flask, render_template, request, jsonify
import json
import os
import pandas as pd
import nltk
from flask_cors import CORS


# ROOT_PATH for linking with all your files. 
os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..", os.curdir))

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Specify the path to the JSON file relative to the current script
json_file_path = os.path.join(current_directory, 'sephora_product_df.json')

# Load the JSON data into a DataFrame
with open(json_file_path, 'r') as file:
    dat = json.load(file)
    df = pd.DataFrame(dat)

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    # Render the main search page
    return render_template('base.html')

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
    brand_name = data.get("brand_name", "Any").lower().strip()
    price_range = data.get("price_range", [0, 200])
    price_min = float(price_range[0])
    price_max = float(price_range[1])
    exact_product_search = data.get("user_search_input", "").lower().strip()

    # Determine what elements to use in search
    use_price = (price_min != 0) or (price_max != 200)
    use_brand = brand_name != "any"
    use_exact_product_search = exact_product_search != ""

    # Filter the DataFrame based on user inputs
    filtered_df = df.copy()

    # Filter by price range
    if use_price:
        filtered_df = filtered_df[
            (filtered_df['price_usd'] >= price_min) & (filtered_df['price_usd'] <= price_max)
        ]

    # Filter by brand name
    if use_brand:
        filtered_df = filtered_df[filtered_df['brand_name'].str.lower().str.strip() == brand_name]

    # Find most relevant products according to free-text query
    relevant_doc_inds = []
    if use_exact_product_search:
        for i in range(len(filtered_df['product_name'])):
            sim = nltk.edit_distance(exact_product_search, filtered_df["product_name"].iloc[i])
            relevant_doc_inds.append((
                filtered_df["product_name"].iloc[i],
                sim,
                filtered_df["price_usd"].iloc[i],
                filtered_df["brand_name"].iloc[i]
            ))

        # Sort by similarity and return top 5 matches
        top_5_relevant_docs = sorted(relevant_doc_inds, key=lambda x: x[1])[:5]  # Lower edit distance is better
    else:
        
        # If no search query, return all filtered products
        top_5_relevant_docs = filtered_df[["product_name", "price_usd", "brand_name"]].values.tolist()[:5]
    
    return jsonify({"results": top_5_relevant_docs})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5012)