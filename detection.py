import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import joblib
from flask import Flask, request, jsonify
from flask_cors import CORS
from underthesea import word_tokenize

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILE = os.path.join(BASE_DIR, "models", "rf_model_vi.pkl")
VECTORIZER_FILE = os.path.join(BASE_DIR, "models", "tfidf_vectorizer_vi.pkl")

if os.path.exists(MODEL_FILE) and os.path.exists(VECTORIZER_FILE):
    rf = joblib.load(MODEL_FILE)
    vectorizer = joblib.load(VECTORIZER_FILE)
else:
    fake_news = pd.read_csv(os.path.join(BASE_DIR, "Fake.csv"), encoding="utf-8")
    true_news = pd.read_csv(os.path.join(BASE_DIR, "True.csv"), encoding="utf-8")

    fake_news['text'] = fake_news['text'].apply(lambda x: " ".join(word_tokenize(str(x))))
    true_news['text'] = true_news['text'].apply(lambda x: " ".join(word_tokenize(str(x))))

    fake_news['label'] = 'fake'
    true_news['label'] = 'true'

    data = pd.concat([fake_news, true_news], axis=0).sample(frac=1, random_state=42).reset_index(drop=True)

    X = data['text']
    y = data['label']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    vietnamese_stopwords = [
        "và","của","là","có","trên","cho","một","những","được","khi","này","với","để","ra","tại",
        "theo","vì","như","cũng","từ","sẽ","họ","nên","các","tôi","anh","chị","ông","bà"
    ]

    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words=vietnamese_stopwords,
        ngram_range=(1,2),
        min_df=5,
        max_df=0.8
    )
    X_train_vec = vectorizer.fit_transform(X_train)

    rf = RandomForestClassifier(n_estimators=100, max_depth=30, random_state=42, n_jobs=-1)
    rf.fit(X_train_vec, y_train)

    os.makedirs(os.path.join(BASE_DIR, "models"), exist_ok=True)
    joblib.dump(rf, MODEL_FILE)
    joblib.dump(vectorizer, VECTORIZER_FILE)

    X_test_vec = vectorizer.transform(X_test)
    y_pred = rf.predict(X_test_vec)

    acc = accuracy_score(y_test, y_pred)
    print(f"Accuracy trên tập test: {acc:.4f}")

    cm = confusion_matrix(y_test, y_pred)
    print("Confusion matrix:")
    print(cm)

    report = classification_report(y_test, y_pred)
    print("Classification report:")
    print(report)

def predict_news(text):
    try:
        text = " ".join(word_tokenize(str(text)))
        vec = vectorizer.transform([text])
        return rf.predict(vec)[0]
    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/check", methods=["POST"])
def check_news():
    data = request.get_json()
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "No text provided"}), 400

    result = predict_news(text)
    print(f"[CHECK] text={text[:60]}..., result={result}")
    return jsonify({"result": result})

if __name__ == "__main__":
    app.run(debug=True)
