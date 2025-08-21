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

def load_data_from_folder(folder, prefix_label):
    texts, labels = [], []
    for file in glob.glob(os.path.join(folder, "*.json")):
        try:
            with open(file, "r", encoding="utf-8") as f:
                article = json.load(f)

            text = (article.get("title", "") + " " +
                    article.get("text", article.get("description", ""))).strip()

            subject = article.get("subject", "").strip()
            if text and subject:
                label = f"{prefix_label}_{subject}"
                texts.append(text)
                labels.append(label)

        except Exception as e:
            print(f"⚠️ Lỗi đọc {file}: {e}")
    return texts, labels

texts_real, labels_real = load_data_from_folder("Real", "real")
texts_fake, labels_fake = load_data_from_folder("Fake", "fake")

texts = texts_real + texts_fake
labels = labels_real + labels_fake

print(f"Load {len(texts)} mẫu dữ liệu (Real={len(texts_real)}, Fake={len(texts_fake)})")

texts_tok = [" ".join(word_tokenize(t)) for t in texts]
vectorizer = TfidfVectorizer(max_features=5000)
X = vectorizer.fit_transform(texts_tok)

rf = RandomForestClassifier(n_estimators=200, random_state=42)
rf.fit(X, labels)

y_pred = rf.predict(X)
acc = accuracy_score(labels, y_pred)
report = classification_report(labels, y_pred, output_dict=True)
cm = confusion_matrix(labels, y_pred, labels=rf.classes_).tolist()

metrics = {
    "accuracy": acc,
    "report": report,
    "confusion_matrix": {
        "labels": rf.classes_.tolist(),
        "matrix": cm
    }
}

joblib.dump(rf, MODEL_FILE)
joblib.dump(vectorizer, VECTORIZER_FILE)
with open(EVAL_FILE, "w", encoding="utf-8") as f:
    json.dump(metrics, f, ensure_ascii=False, indent=2)

print("🎉 Đã train lại mô hình Fake/Real + Chủ đề và lưu vào thư mục models/")
