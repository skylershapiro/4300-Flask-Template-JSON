#This script handle's the information retrieval component of this project. 
#User queries will be sent from the frontend ---> the backend.
#This script will find a set of relevant documents in our dataset using this query
    #As we add complexity to the kinds of queries our system tolerates, we should build 
    #a "parse_query.py" that smoothly passes Frontend output into this retrieval system in the backend

#SIMPLIFIED IMPLEMENTATION for TA meeting on 3/19
#Determine how to build search criteria
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


# tags = ["moisturizer"] 
# '''
# Type: List of strings
# Currently written as 'Skin Concerns' in frontend. '''

# price_range = (0,200) 
# '''
# Type: Tuple(int1, int2) with int1 <= int2
# WHEN NOT SET BY USER, default will be 0-200, 
# If this is the case, maybe we can just ignore price-range during retrieval? '''

# exact_product_search = 'CeraVe Daily Moisturizing Lotion for Dry Skin, Body Lotion & Face Moisturizer with Hyaluronic Acid and Ceramides'
# '''
# Type: String
# User looking for specific product, free-text search term
# Should be able to tolerate miss-spellings and near-perfect hits (fuzzy match). '''

# logic to determine how to conduct retrieval
last_user_query = parse_json()[-1]
price_range = last_user_query["price_range"]
brand_name = last_user_query["brand_name"]
exact_product_search = last_user_query["query"]
tags = last_user_query["skin_concerns"]
print(last_user_query)
print("price range", price_range, type(price_range))

use_tags = False
use_price_range = False
use_brand = False
use_exact_product_search = False

if tags: use_tags = True
if price_range != (0,200): use_price_range = True
if brand_name: use_brand = True
if exact_product_search != "": use_exact_product_search = True


#Perform retreival using criteria
#df = pd.read_csv("/Users/skylershapiro/cs4300/4300-Flask-Template-JSON/sephora_product_df.csv")
df = pd.read_csv("sephora_product_df.csv")
print("PRICE RANGE LOWER0000000000000000", price_range[0])
print("pricerangeuper00000000000000", price_range[1])
print("first price usd0000000000", df['price_usd'][0])
print("second price usd0000000000", df['price_usd'][1])

if use_price_range: # drop products that don't fit price range
    df = df[(df['price_usd'] >= price_range[0]) & (df['price_usd'] <= price_range[1])]
if use_brand: #drop products that don't fit brand name
    df = df[df['brand_name'] == brand_name] 

# find most relevant products according to free-text query
relevant_doc_inds = []
i = 0
for d in df['product_name']:
   #print("document name", d) 
   i += 1 
   sim = nltk.edit_distance(exact_product_search, d) # calculate similarity between query and product name
   #print("similarity", sim)
   if sim > 0.6: # throw out obvious poor matches
       relevant_doc_inds.append((d, sim, df.loc[df['product_name'] == d, 'price_usd'].values[0])) # store document and similarity score

# return top 20 matches
top_5_relevant_docs = sorted(relevant_doc_inds, key=lambda x: x[1], reverse=True)[:5]
#print(top_5_relevant_docs)



# # find 3 most relevant documents using levenshtein edit distance between user free-text queries and product names
# # read in data
# df = pd.read_csv("skincare_products_clean.csv")
# df = df[["product_name", "product_type", "price"]]

# relevant_doc_inds = []
# i = 0
# for d in df['product_name']:
#    i += 1 
#    sim = nltk.edit_distance(exact_product_search, d.split()) # calculate similiarty between query and product name
#    if sim > 0.6: # throw out obvious poor matches
#        relevant_doc_inds.append((d, sim)) # store document and similarity score

# # return top 20 matches
# top_3_relevant_docs = sorted(relevant_doc_inds,  key=lambda x: x[1])[-3:]
# #print(top_3_relevant_docs)
       

