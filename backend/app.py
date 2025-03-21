import json
import os
from flask import Flask, render_template, request
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler
import pandas as pd
import retrieval

# # ROOT_PATH for linking with all your files. 
# # Feel free to use a config.py or settings.py with a global export variable
# os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..",os.curdir))

# # Get the directory of the current script
# current_directory = os.path.dirname(os.path.abspath(__file__))

# # Specify the path to the JSON file relative to the current script
# json_file_path = os.path.join(current_directory, 'init.json')

# # Assuming your JSON data is stored in a file named 'init.json'
# with open(json_file_path, 'r') as file:
#     data = json.load(file)
#     episodes_df = pd.DataFrame(data['episodes'])
#     reviews_df = pd.DataFrame(data['reviews'])

# app = Flask(__name__)
# CORS(app)

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
#code for frontend
import streamlit as st
import pandas as pd
import json 
import os
from retrieval import top_5_relevant_docs, last_user_query

user_data = "user_data.json"
def load_data():
  if os.path.exists(user_data):
        with open(user_data, "r") as f:
            return json.load(f)
  return []  # Return empty list if file doesn't exist

# Function to save new data
def save_data(new_entry):
    data = load_data()  # Load existing data
    data.append(new_entry)  # Append new user input
    with open(user_data, "w") as f:
        json.dump(data, f, indent=4)  # Save back to file



st.title('Welcome to SmartSkin')
skin_concerns = st.multiselect("Skin Concerns", ["Acne", "Dry Skin", "Oily skin", "Sensitive Skin", "Wrinkles", "Large Pores", "Redness", "Dullness", "Scars", "Dark Circles", "Texture"])

#brand names
df = pd.read_csv("sephora_product_df.csv")
brands = sorted(df['brand_name'].dropna().unique().tolist())
brands.insert(0, "Any")

brand_name = st.selectbox("Brands", brands)
st.write("Selected Brand:", brand_name) 

price_range = st.slider(
    "Price Range",
    min_value=0,  
    max_value=200,  
    value=(0, 200) )


st.write(f"Price range: {price_range[0]} to {price_range[1]}")

user_search_input = st.text_input("Search for a product")

if st.button("Search SmartSkin!"):
    user_entry = {
        "skin_concerns": skin_concerns, 
        "price_range": price_range,  
        "brand_name": brand_name,
        "user_search_input" : user_search_input
    }
    save_data(user_entry)
    st.markdown("### Top 5 Relevant Products:")
    for product, sim, price in top_5_relevant_docs:
        st.markdown(f"**{product}**  \n💰 **Price:** ${price:.2f}  \n🔍 **Similarity Score:** {sim:.2f}")
        st.write("---")  # Adds a separator for readability
    st.write(last_user_query)
