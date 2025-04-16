import json

with open("sephora_product_df.json", "r") as f:
    data = json.load(f)

# Filter: exclude primary_category == 'Fragrance' or 'Hair'
filtered_data = [
    entry for entry in data
    if entry.get("primary_category", "").lower() not in ["fragrance", "hair", "Mini Size"]
]


with open("filtered_sephora_products.json", "w") as f:
    json.dump(filtered_data, f, indent=4)

