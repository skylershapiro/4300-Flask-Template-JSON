#This script handle's the information retrieval component of this project. 
#User queries will be sent from the frontend ---> the backend.
#This script will find a set of relevant documents in our dataset using this query
    #As we add complexity to the kinds of queries our system tolerates, we should build 
    #a "parse_query.py" that smoothly passes Frontend output into this retrieval system in the backend

#SIMPLIFIED IMPLEMENTATION for TA meeting on 3/19

def parse_json():
    '''This function recieves JSON output from frontend and parses into suitable format to conduct information retrieval'''
    pass


tags = ["moisturizer"] 
'''
Type: List of strings
Currently written as 'Skin Concerns' in frontend. '''

price_range = (0,200) 
'''
Type: Tuple(int1, int2) with int1 <= int2
WHEN NOT SET BY USER, default will be 0-200, 
If this is the case, maybe we can just ignore price-range during retrieval? '''

exact_product_search = 'CeraVe Daily Moisturizing Lotion for Dry Skin, Body Lotion & Face Moisturizer with Hyaluronic Acid and Ceramides'
'''
Type: String
User looking for specific product, free-text search term
Should be able to tolerate miss-spellings and near-perfect hits (fuzzy match). '''

# logic to determine how to conduct retrieval


#Determine how to build search criteria
import nltk
import pandas as pd

use_tags = False
use_price_range = False
use_exact_product_search = False

if tags != "": use_tags = True
if price_range != (1,200): use_price_range = True
if exact_product_search != "": use_exact_product_search = True

# find 3 most relevant documents using levenshtein edit distance between user free-text queries and product names

# read in data
df = pd.read_csv("/Users/skylershapiro/cs4300/skincare_products_clean.csv")
df = df[["product_name", "product_type", "price"]]

relevant_doc_inds = []
i = 0
for d in df['product_name']:
   i += 1 
   sim = nltk.edit_distance(exact_product_search, d.split()) # calculate similiarty between query and product name
   if sim > 0.6: # throw out obvious poor matches
       relevant_doc_inds.append((d, sim)) # store document and similarity score

# return top 20 matches
top_3_relevant_docs = sorted(relevant_doc_inds,  key=lambda x: x[1])[-3:]
print(top_3_relevant_docs)
       

