#This script handle's the information retrieval component of this project. 
#User queries will be sent from the frontend ---> the backend.
#This script will find a set of relevant documents in our dataset using this query
    #As we add complexity to the kinds of queries our system tolerates, we should build 
    #a "parse_query.py" that smoothly passes Frontend output into this retrieval system in the backend

#SIMPLIFIED IMPLEMENTATION for TA meeting on 3/19

def process_json():
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


