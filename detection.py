import os, glob, json, gzip, random
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
from tqdm import tqdm

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
EVAL_FILE = os.path.join(MODEL_DIR, "evaluation.json")

def load_json_folder(folder_path, label, min_len=50, max_len=10000):
    for fp in tqdm(glob.glob(os.path.join(folder_path, "*.json.gz")), desc=f"Loading {label}"):
        try:
            with gzip.open(fp, "rt", encoding="utf-8") as f:
                obj = json.load(f)
            title = obj.get("title", "")
            content = obj.get("text", "") or obj.get("description", "")
            text = f"{title} {content}".strip()
            if min_len <= len(text) <= max_len:
                yield {"text": text, "label": label}
        except Exception:
            continue

def evaluate_model(model, vectorizer, texts, labels, save_path=None):
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    model.fit(X_train_vec, y_train)
    y_pred = model.predict(X_test_vec)

    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    cm = confusion_matrix(y_test, y_pred).tolist()

    results = {
        "accuracy": round(acc, 4),
        "report": report,
        "confusion_matrix": cm
    }

    if save_path:
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    return results

if os.path.exists(MODEL_FILE) and os.path.exists(VECTORIZER_FILE):
    rf = joblib.load(MODEL_FILE)
    vectorizer = joblib.load(VECTORIZER_FILE)
else:
    fake_gen = load_json_folder(os.path.join(BASE_DIR, "Fake"), "fake")
    real_gen = load_json_folder(os.path.join(BASE_DIR, "Real"), "true")

    fake_data = list(fake_gen)
    real_data = list(real_gen)

    if not fake_data or not real_data:
        raise RuntimeError("Không tìm thấy dữ liệu Fake hoặc Real")

    fake_data = fake_data[:9000]
    real_data = real_data[:9000]
    data = fake_data + real_data
    random.shuffle(data)

    print(f"Total articles: {len(data)}")

    texts = [" ".join(word_tokenize(d["text"])) for d in tqdm(data, desc="Tokenizing")]
    labels = [d["label"] for d in data]

    vietnamese_stopwords = [
        "và","của","là","có","trên","cho","một","những","được","khi","này","với","để","ra","tại",
        "theo","vì","như","cũng","từ","sẽ","họ","nên","các","tôi","anh","chị","ông","bà","đã","đang","trong"
    ]

    vectorizer = TfidfVectorizer(
        max_features=10000,
        stop_words=vietnamese_stopwords,
        ngram_range=(1,2),
        min_df=5,
        max_df=0.8
    )

    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=30,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1
    )

    results = evaluate_model(rf, vectorizer, texts, labels, save_path=EVAL_FILE)

    joblib.dump(rf, MODEL_FILE, compress=3)
    joblib.dump(vectorizer, VECTORIZER_FILE, compress=3)
    print("Model, vectorizer và evaluation đã được lưu.")

def predict_news(text):
    text_vec = vectorizer.transform([" ".join(word_tokenize(text))])
    probs = rf.predict_proba(text_vec)[0]
    idx = probs.argmax()
    return rf.classes_[idx], float(probs[idx])

@app.route("/check", methods=["POST"])
def check_news():
    data = request.get_json() or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400
    label, confidence = predict_news(text)
    return jsonify({"result": label, "confidence": round(confidence, 4)})

@app.route("/metrics", methods=["GET"])
def get_metrics():
    if not os.path.exists(EVAL_FILE):
        return jsonify({"error": "Evaluation results not found"}), 404
    with open(EVAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
