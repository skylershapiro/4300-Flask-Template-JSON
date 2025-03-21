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


tags = ["moisturizer"] 
# '''
# Type: List of strings
# Currently written as 'Skin Concerns' in frontend. '''
price_range = (0,200) 
brand_name = "Sephora Collection"
# '''
# Type: Tuple(int1, int2) with int1 <= int2
# WHEN NOT SET BY USER, default will be 0-200, 
# If this is the case, maybe we can just ignore price-range during retrieval? '''

exact_product_search = 'CeraVe Daily Moisturizing Lotion for Dry Skin, Body Lotion & Face Moisturizer with Hyaluronic Acid and Ceramides'
# '''
# Type: String
# User looking for specific product, free-text search term
# Should be able to tolerate miss-spellings and near-perfect hits (fuzzy match). '''

# logic to determine how to conduct retrieval
last_user_query = parse_json()[-1]
price_range = last_user_query["price_range"]
# print("this is the price_range", price_range[0])
# print("this is the price_range", price_range[1])
brand_name = last_user_query["brand_name"]
# print("this is the last_user_query", brand_name)
exact_product_search = last_user_query["query"]
# print("this is the exact_product_search", exact_product_search)
tags = last_user_query["skin_concerns"]
# print("this is the tag", tags)


# use_tags = False
# use_price_range = False
# use_brand = False
# use_exact_product_search = False

# if tags != []: use_tags = True
# if price_range != (0,200): use_price_range = True
if brand_name != "any": use_brand = False
# if exact_product_search != "": use_exact_product_search = True


#Perform retreival using criteria
#df = pd.read_csv("/Users/skylershapiro/cs4300/4300-Flask-Template-JSON/sephora_product_df.csv")
# tags = ["moisturizer"] 
# price_range = (0,200) 
# brand_name = "sephora collection"
# exact_product_search = "moisturizer"

#process brand_name column

brand_name = brand_name.lower().strip()
print("brand_name: ", brand_name)
print("use_brand: ", use_brand)
print("price_range", price_range)
print("exact_product_search: ", exact_product_search)

df = pd.read_csv("sephora_product_df.csv")
df['brand_name'] = df['brand_name'].str.lower().str.strip()
#print(df['brand_name'][:10])
#print(df['price_usd'].head(20))
# print(df[df['price_usd'] >= price_range[0]])
use_price_range = True
if use_price_range: # drop products that don't fit price range
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



