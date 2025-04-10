import json
from collections import defaultdict

# Step 1: Load the original JSON
with open("filtered_sephora_reviews.json", "r") as f:
    data = json.load(f)

# Step 2: Group reviews by product (using a tuple of product_name and brand_name as the key)
grouped_reviews = defaultdict(list)
for review in data["results"]:
    product_key = (review["product_name"], review["brand_name"])
    
    # Step 3: Copy review and remove unwanted keys
    review_copy = review.copy()
    del review_copy["product_name"]
    del review_copy["brand_name"]
    
    grouped_reviews[product_key].append(review_copy)

# Step 4: Prepare final structure (nested structure)
output = []
for (product_name, brand_name), reviews in grouped_reviews.items():
    output.append({
        "brand_name": brand_name,
        "product_name": product_name,
        "reviews": reviews
    })

# Step 5: Save as JSON
with open("grouped_reviews.json", "w") as f:
    json.dump(output, f, indent=2)
