import json
import os
from flask import Flask, render_template, request
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler
import pandas as pd

# ROOT_PATH for linking with all your files. 
# Feel free to use a config.py or settings.py with a global export variable
os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..",os.curdir))

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Specify the path to the JSON file relative to the current script
json_file_path = os.path.join(current_directory, 'sephora_product_df.json')
#print(json_file_path)

# Assuming your JSON data is stored in a file named 'init.json'
with open(json_file_path, 'r') as file:
    dat = json.load(file)
    df = pd.DataFrame(dat)
    #print(df.iloc[1])

app = Flask(__name__)
CORS(app)

####### Recieve user input from frontend
#@app.route?

#######

import nltk
import pandas as pd
import json
import os

def parse_json():
    '''This function recieves JSON output from frontend and parses into suitable format to conduct information retrieval'''
    with open("user_data.json", "r", encoding="utf-8") as file:
        user_data = json.load(file) 
    # Convert to structured format
    parsed_data = []
    for entry in user_data:
        parsed_data.append({
            "skin_concerns": entry.get("skin_concerns", []),  # Default to empty list if missing
            "brand_name": entry.get("brand_name", ""),
            "price_range": tuple(entry.get("price_range", [0, 0])),  # Convert to tuple for immutability
            "query": entry.get("user_search_input", "").lower()  # Normalize search input
        })
    
    return parsed_data


price_range = (0,200) 
brand_name = "Sephora Collection"
exact_product_search = "moisturizer"



# determine what elements to use in search
if price_range == (0,200): use_price = False
if brand_name == "any": use_brand = False
if exact_product_search == "": use_exact_product_search = False

brand_name = brand_name.lower().strip() # process brand name from user
df['brand_name'] = df['brand_name'].str.lower().str.strip() # normalize brand_name column

# print("brand_name: ", brand_name)
# print("use_brand: ", use_brand)
# print("price_range", price_range)
# print("exact_product_search: ", exact_product_search)

if use_price: # drop products that don't fit price range
    df = df[(df['price_usd'] >= price_range[0]) & (df['price_usd'] <= price_range[1])]
    print(df.shape)
if use_brand: #drop products that don't fit brand name
    df = df[df['brand_name'] == brand_name] 
# find most relevant products according to free-text query
relevant_doc_inds = []
i = 0
for i in range(len(df['product_name'])):
   #print("document name", d) 
   sim = nltk.edit_distance(exact_product_search, df["product_name"].iloc[i]) # calculate similarity between query and product name
   #print("similarity", sim)
   #if sim > 0.6: # throw out obvious poor matches 
   relevant_doc_inds.append((df["product_name"].iloc[i], 
                             sim, 
                             #"brand_name: "+df["brand_name"].iloc[i], 
                             df["price_usd"].iloc[i])) # store document and similarity score
# return top 20 matches
top_5_relevant_docs = sorted(relevant_doc_inds, key=lambda x: x[1], reverse=True)[:5]
print(top_5_relevant_docs)
## Retrieval code using users search criteria






# # Sample search using json with pandas
# def json_search(query):
#     matches = []
#     merged_df = pd.merge(episodes_df, reviews_df, left_on='id', right_on='id', how='inner')
#     matches = merged_df[merged_df['title'].str.lower().str.contains(query.lower())]
#     matches_filtered = matches[['title', 'descr', 'imdb_rating']]
#     matches_filtered_json = matches_filtered.to_json(orient='records')
#     return matches_filtered_json

# @app.route("/")
# def home():
#     return render_template('base.html',title="sample html")

# @app.route("/episodes")
# def episodes_search():
#     text = request.args.get("title")
#     return json_search(text)

# if 'DB_NAME' not in os.environ:
#     app.run(debug=True,host="0.0.0.0",port=5000)