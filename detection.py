import os, json
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib

try:
    from underthesea import word_tokenize
except ImportError:
    def word_tokenize(x):
        return str(x).split()

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_FILE = os.path.join(MODEL_DIR, "rf_model_vi.pkl")
VECTORIZER_FILE = os.path.join(MODEL_DIR, "tfidf_vectorizer_vi.pkl")
EVAL_FILE = os.path.join(MODEL_DIR, "metrics_vi.json")

if os.path.exists(MODEL_FILE) and os.path.exists(VECTORIZER_FILE):
    rf = joblib.load(MODEL_FILE)
    vectorizer = joblib.load(VECTORIZER_FILE)
else:
    rf = None
    vectorizer = None
    print("Warning: Model hoặc vectorizer chưa tồn tại, /check sẽ không hoạt động.")

def predict_news(text):
    if rf is None or vectorizer is None:
        return None, None
    text_vec = vectorizer.transform([" ".join(word_tokenize(text))])
    probs = rf.predict_proba(text_vec)[0]
    idx = probs.argmax()
    return rf.classes_[idx], float(probs[idx])

@app.route("/check", methods=["POST"])
def check_news():
    if rf is None or vectorizer is None:
        return jsonify({"error": "Model chưa được load"}), 500

    data = request.get_json() or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400

    label, confidence = predict_news(text)
    return jsonify({"result": label, "confidence": round(confidence, 4)})

@app.route("/metrics", methods=["GET"])
def get_metrics():
    if not os.path.exists(EVAL_FILE):
        return jsonify({"error": "Metrics file not found"}), 404
    with open(EVAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
