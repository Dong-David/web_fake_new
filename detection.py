import os, glob, json
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import joblib

try:
    from underthesea import word_tokenize
except Exception:
    def word_tokenize(x): 
        return str(x).split()

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_FILE = os.path.join(MODEL_DIR, "rf_model_vi.pkl")
VECTORIZER_FILE = os.path.join(MODEL_DIR, "tfidf_vectorizer_vi.pkl")
METRICS_FILE = os.path.join(MODEL_DIR, "metrics_vi.json")

def build_text_from_obj(obj):
    """
    Ghép Title + Content nếu có; fallback qua các key khác/viết thường.
    Trả về '' nếu không có gì dùng được.
    """
    keys = {k.lower(): k for k in obj.keys()}
    get = lambda name: obj.get(keys[name], "") if name in keys else ""

    title = get("title")
    content = get("content")
    text = " ".join([str(title).strip(), str(content).strip()]).strip()

    if not text:
        for alt in ["text", "body", "article", "article_body"]:
            if alt in keys:
                text = str(obj.get(keys[alt], "")).strip()
                if text:
                    break
    return text

def load_json_folder(folder_path, label):
    rows = []
    for fp in glob.glob(os.path.join(folder_path, "*.json")):
        try:
            with open(fp, "r", encoding="utf-8") as f:
                obj = json.load(f)
            text = build_text_from_obj(obj)
            if text:
                rows.append({"text": text, "label": label})
        except Exception as e:
            print(f"⚠️ Lỗi đọc {fp}: {e}")
    return pd.DataFrame(rows)

def save_metrics(acc, y_true, y_pred, labels=("fake","true")):
    cm = confusion_matrix(y_true, y_pred, labels=list(labels)).tolist()
    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    metrics = {
        "accuracy": acc,
        "confusion_matrix": {"labels": list(labels), "matrix": cm},
        "report": report
    }
    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    return metrics

def load_metrics():
    if os.path.exists(METRICS_FILE):
        with open(METRICS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

metrics_cache = None
if os.path.exists(MODEL_FILE) and os.path.exists(VECTORIZER_FILE):
    rf = joblib.load(MODEL_FILE)
    vectorizer = joblib.load(VECTORIZER_FILE)
    metrics_cache = load_metrics()
else:
    fake_dir = os.path.join(BASE_DIR, "Fake", "Article_Contents")
    real_dir = os.path.join(BASE_DIR, "Real", "Article_Contents")
    fake_df = load_json_folder(fake_dir, "fake") if os.path.isdir(fake_dir) else pd.DataFrame(columns=["text","label"])
    real_df = load_json_folder(real_dir, "true") if os.path.isdir(real_dir) else pd.DataFrame(columns=["text","label"])

    if len(fake_df) == 0 and len(real_df) == 0:
        raise RuntimeError("Không tìm thấy dữ liệu trong Fake/Article_Contents và Real/Article_Contents")

    data = pd.concat([fake_df, real_df], ignore_index=True)
    data["text"] = data["text"].astype(str)
    data = data[data["text"].str.len() > 50]
    data = data[data["text"].str.len() < 10000]

    data["text"] = data["text"].apply(lambda x: " ".join(word_tokenize(x)))

    X_train, X_test, y_train, y_test = train_test_split(
        data["text"], data["label"], test_size=0.2, random_state=42, stratify=data["label"]
    )

    vietnamese_stopwords = [
        "và","của","là","có","trên","cho","một","những","được","khi","này","với","để","ra","tại",
        "theo","vì","như","cũng","từ","sẽ","họ","nên","các","tôi","anh","chị","ông","bà","đã","đang","trong"
    ]
    vectorizer = TfidfVectorizer(
        max_features=5000, stop_words=vietnamese_stopwords,
        ngram_range=(1,2), min_df=5, max_df=0.8
    )
    X_train_vec = vectorizer.fit_transform(X_train)

    rf = RandomForestClassifier(
        n_estimators=100, max_depth=30, random_state=42, n_jobs=-1,
        class_weight="balanced"   
    )
    print("Training RandomForest…")
    rf.fit(X_train_vec, y_train)

    X_test_vec = vectorizer.transform(X_test)
    y_pred = rf.predict(X_test_vec)
    acc = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {acc:.4f}")
    metrics_cache = save_metrics(acc, y_test.tolist(), y_pred.tolist())

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(rf, MODEL_FILE)
    joblib.dump(vectorizer, VECTORIZER_FILE)

def predict_news(text):
    text = " ".join(word_tokenize(str(text)))
    vec = vectorizer.transform([text])
    return rf.predict(vec)[0]

@app.route("/check", methods=["POST"])
def check_news():
    data = request.get_json() or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400
    result = predict_news(text)
    print(f"[CHECK] text={text[:60]}..., result={result}")
    return jsonify({"result": result})

@app.route("/metrics", methods=["GET"])
def get_metrics():
    global metrics_cache
    if metrics_cache is None:
        return jsonify({"message": "metrics not available yet"}), 404
    return jsonify(metrics_cache)

if __name__ == "__main__":
    app.run(debug=True)
