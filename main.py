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

   