import os, json, glob, joblib
from underthesea import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_FILE = os.path.join(MODEL_DIR, "rf_model_vi.pkl")
VECTORIZER_FILE = os.path.join(MODEL_DIR, "tfidf_vectorizer_vi.pkl")
EVAL_FILE = os.path.join(MODEL_DIR, "metrics_vi.json")

# =============================
# HÀM LOAD DỮ LIỆU
# =============================
def load_data_from_folder(folder, label_name):
    texts, labels = [], []
    for file in glob.glob(os.path.join(folder, "*.json")):
        try:
            with open(file, "r", encoding="utf-8") as f:
                article = json.load(f)
            # Ghép title + text/description thành 1 đoạn văn
            text = (article.get("title", "") + " " + 
                    article.get("text", article.get("description", ""))).strip()
            if text:
                texts.append(text)
                labels.append(label_name)   # gán nhãn theo thư mục
        except Exception as e:
            print(f"⚠️ Lỗi đọc {file}: {e}")
    return texts, labels

# =============================
# LOAD CẢ HAI THƯ MỤC
# =============================
texts_real, labels_real = load_data_from_folder("Real", "real")
texts_fake, labels_fake = load_data_from_folder("Fake", "fake")

texts = texts_real + texts_fake
labels = labels_real + labels_fake

print(f"Load {len(texts)} mẫu dữ liệu (Real={len(texts_real)}, Fake={len(texts_fake)})")

# =============================
# TIỀN XỬ LÝ & VECTOR HÓA
# =============================
texts_tok = [" ".join(word_tokenize(t)) for t in texts]
vectorizer = TfidfVectorizer(max_features=5000)
X = vectorizer.fit_transform(texts_tok)

# =============================
# TRAIN RANDOM FOREST
# =============================
rf = RandomForestClassifier(n_estimators=200, random_state=42)
rf.fit(X, labels)

# =============================
# ĐÁNH GIÁ
# =============================
y_pred = rf.predict(X)
acc = accuracy_score(labels, y_pred)
report = classification_report(labels, y_pred, output_dict=True)
cm = confusion_matrix(labels, y_pred, labels=["real","fake"]).tolist()

metrics = {
    "accuracy": acc,
    "report": report,
    "confusion_matrix": {
        "labels": ["real", "fake"],
        "matrix": cm
    }
}

# =============================
# LƯU MODEL + VECTORIZER + METRICS
# =============================
joblib.dump(rf, MODEL_FILE)
joblib.dump(vectorizer, VECTORIZER_FILE)
with open(EVAL_FILE, "w", encoding="utf-8") as f:
    json.dump(metrics, f, ensure_ascii=False, indent=2)

print("Đã train lại mô hình Fake vs Real và lưu vào thư mục models/")
