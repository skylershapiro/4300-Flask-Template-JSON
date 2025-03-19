#code for frontend
import streamlit as st
import json 
import os

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
        "user_search_input" : user_search_input
    }
    save_data(user_entry)
   