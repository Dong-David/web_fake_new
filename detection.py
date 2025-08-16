import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.tree import DecisionTreeClassifier
import joblib
from flask import Flask, request, jsonify

MODEL_FILE = 'decision_tree_model.pkl'
VECTORIZER_FILE = 'tfidf_vectorizer.pkl'

if os.path.exists(MODEL_FILE) and os.path.exists(VECTORIZER_FILE):
    dt = joblib.load(MODEL_FILE)
    vectorizer = joblib.load(VECTORIZER_FILE)
else:
    fake_news = pd.read_csv('final project/Fake.csv')
    true_news = pd.read_csv('final project/True.csv')

    fake_news['label'] = 'fake'
    true_news['label'] = 'true'

    data = pd.concat([fake_news, true_news], axis=0).sample(frac=1, random_state=42).reset_index(drop=True)

    X = data['text']
    y = data['label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
    X_train_vec = vectorizer.fit_transform(X_train)

    dt = DecisionTreeClassifier(max_depth=50, random_state=42)
    dt.fit(X_train_vec, y_train)

    joblib.dump(dt, MODEL_FILE)
    joblib.dump(vectorizer, VECTORIZER_FILE)

def predict_news(text):
    vec = vectorizer.transform([text])
    return dt.predict(vec)[0]

app = Flask(__name__)

@app.route("/check", methods=["POST"])
def check_news():
    data = request.get_json()
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "No text provided"}), 400

    result = predict_news(text)
    return jsonify({"result": result})

if __name__ == "__main__":
    app.run(debug=True)
