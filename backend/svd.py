import json
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer

def reduce_reviews(grouped_reviews, num_topics=100):
    output = []
    vectorizer = TfidfVectorizer(stop_words="english")

    for product in grouped_reviews:
        # Extract review titles and filter out empty titles
        reviews_text = [review["review_title"] for review in product["reviews"] if review["review_title"]]

        # Ensure that we are not only left with stop words or empty titles
        reviews_text = [title for title in reviews_text if len(title.split()) > 1]  # Titles with at least 2 words

        # If no valid review titles, initialize an empty list for important terms
        if not reviews_text:
            important_terms = []
        else:
            try:
                # Create the TF-IDF matrix
                tfidf_matrix = vectorizer.fit_transform(reviews_text)

                # Get the number of features (terms) in the TF-IDF matrix
                num_features = tfidf_matrix.shape[1]

                if num_features > 1:
                    # Set n_components to the minimum of num_topics or (num_features - 1)
                    n_components = min(num_topics, num_features - 1)

                    # Apply SVD to reduce dimensionality
                    svd = TruncatedSVD(n_components=n_components)
                    svd.fit(tfidf_matrix)

                    # Extract top terms from each component
                    terms = []
                    feature_names = vectorizer.get_feature_names()

                    for i in range(svd.components_.shape[0]):
                        top_terms = [feature_names[i] for i in svd.components_[i].argsort()[-n_components:]]  # Get top terms for this component
                        terms.extend(top_terms)

                    # Remove duplicates and limit to top 100 terms
                    important_terms = list(set(terms))[:100]
                else:
                    # If only 1 feature exists, no SVD can be performed, assign an empty list
                    important_terms = []

            except ValueError as e:
                # Handle empty vocabulary or other fitting issues
                print(f"Skipping product {product['product_name']} due to error: {e}")
                important_terms = []

        # Add the product with its important terms (even if empty)
        output.append({
            "brand_name": product["brand_name"],
            "product_name": product["product_name"],
            "important_terms": important_terms
        })

    return output

# Example usage
grouped_reviews = json.load(open("grouped_reviews.json"))
reduced_reviews = reduce_reviews(grouped_reviews, num_topics=100)

# Save output
with open("reduced_reviews.json", "w") as outfile:
    json.dump(reduced_reviews, outfile, indent=4)
