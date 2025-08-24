import os, json, glob, joblib
from underthesea import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from deep_translator import GoogleTranslator
from langdetect import detect

# ================================
# Đường dẫn lưu mô hình + kết quả
# ================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_FILE = os.path.join(MODEL_DIR, "rf_model_vi.pkl")
VECTORIZER_FILE = os.path.join(MODEL_DIR, "tfidf_vectorizer_vi.pkl")
EVAL_FILE = os.path.join(MODEL_DIR, "metrics_vi.json")


# ================================
# Hàm tiện ích
# ================================
def translate_to_vietnamese(text: str) -> str:
    """Dịch văn bản sang tiếng Việt nếu ngôn ngữ khác 'vi'."""
    try:
        lang = detect(text)
        if lang != "vi":
            text = GoogleTranslator(source="auto", target="vi").translate(text)
    except Exception:
        pass
    return text


def load_data_from_folder(folder: str, label: str):
    """Đọc dữ liệu từ folder JSON, trả về texts + labels."""
    texts, labels = [], []
    for file in glob.glob(os.path.join(folder, "*.json")):
        try:
            with open(file, "r", encoding="utf-8") as f:
                article = json.load(f)

            text = (article.get("title", "") + " " +
                    article.get("text", article.get("description", ""))).strip()

            if text:
                text = translate_to_vietnamese(text)
                texts.append(text)
                labels.append(label)

        except Exception as e:
            print(f"Lỗi đọc {file}: {e}")
    return texts, labels


def predict_text(text: str, model, vectorizer):
    """Dự đoán nhãn (real/fake) cho văn bản mới."""
    text = translate_to_vietnamese(text)
    text_tok = " ".join(word_tokenize(text))
    X = vectorizer.transform([text_tok])
    return model.predict(X)[0]


# ================================
# Training
# ================================
if __name__ == "__main__":
    # 1. Load dữ liệu
    texts_real, labels_real = load_data_from_folder("Real", "real")
    texts_fake, labels_fake = load_data_from_folder("Fake", "fake")

    texts = texts_real + texts_fake
    labels = labels_real + labels_fake

    print(f"Load {len(texts)} mẫu dữ liệu (Real={len(texts_real)}, Fake={len(texts_fake)})")

    # 2. Tách từ
    texts_tok = [" ".join(word_tokenize(t)) for t in texts]

    # 3. Chia train/test TRƯỚC
    X_train_texts, X_test_texts, y_train, y_test = train_test_split(
        texts_tok, labels, test_size=0.2, random_state=42, stratify=labels
    )

    # 4. Fit TF-IDF trên train, transform cả train/test
    vectorizer = TfidfVectorizer(max_features=10000)
    X_train = vectorizer.fit_transform(X_train_texts)
    X_test = vectorizer.transform(X_test_texts)

    # 5. Train model
    rf = RandomForestClassifier(n_estimators=500, random_state=42)
    rf.fit(X_train, y_train)

    # 6. Đánh giá
    y_pred = rf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    cm = confusion_matrix(y_test, y_pred, labels=rf.classes_).tolist()

    metrics = {
        "accuracy": acc,
        "report": report,
        "confusion_matrix": {
            "labels": rf.classes_.tolist(),
            "matrix": cm,
        },
    }

    # 7. Lưu model + vectorizer + metrics
    joblib.dump(rf, MODEL_FILE)
    joblib.dump(vectorizer, VECTORIZER_FILE)
    with open(EVAL_FILE, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    print("Training xong. Mô hình và vectorizer đã lưu vào thư mục models/")
