from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def buildRetriever(historical_pairs):
    """historical_pairs: list of (customer_message, amazon_reply) tuples"""
    messages = [p[0] for p in historical_pairs]
    vectorizer = TfidfVectorizer(max_features=3000)
    matrix = vectorizer.fit_transform(messages)

    def retrieveSimilar(new_message, k=3):
        new_vec = vectorizer.transform([new_message])
        sims = cosine_similarity(new_vec, matrix)[0]
        top_k_idx = sims.argsort()[-k:][::-1]
        return [historical_pairs[i] for i in top_k_idx]

    return retrieveSimilar