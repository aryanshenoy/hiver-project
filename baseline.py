from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

def most_frequent_baseline(train_labels):
    most_common = Counter(train_labels).most_common(1)[0][0]
    return lambda message: most_common

def train_tfidf_baseline(train_messages, train_labels):
    vectorizer = TfidfVectorizer(max_features=2000)
    X = vectorizer.fit_transform(train_messages)
    clf = LogisticRegression(max_iter=1000)
    clf.fit(X, train_labels)
    def predict(message):
        X_new = vectorizer.transform([message])
        return clf.predict(X_new)[0]
    return predict