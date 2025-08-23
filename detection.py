import os, json, glob, joblib
from underthesea import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from deep_translator import GoogleTranslator
from langdetect import detect

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_FILE = os.path.join(MODEL_DIR, "rf_model_vi.pkl")
VECTORIZER_FILE = os.path.join(MODEL_DIR, "tfidf_vectorizer_vi.pkl")
EVAL_FILE = os.path.join(MODEL_DIR, "metrics_vi.json")

def translate_to_vietnamese(text):
    try:
        lang = detect(text)
        if lang != 'vi':
            text = GoogleTranslator(source='auto', target='vi').translate(text)
    except:
        pass
    return text

def load_data_from_folder(folder, label):
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

texts_real, labels_real = load_data_from_folder("Real", "real")
texts_fake, labels_fake = load_data_from_folder("Fake", "fake")

texts = texts_real + texts_fake
labels = labels_real + labels_fake

print(f"Load {len(texts)} mẫu dữ liệu (Real={len(texts_real)}, Fake={len(texts_fake)})")

texts_tok = [" ".join(word_tokenize(t)) for t in texts]

vectorizer = TfidfVectorizer(max_features=5000)
X = vectorizer.fit_transform(texts_tok)

X_train, X_test, y_train, y_test = train_test_split(
    X, labels, test_size=0.2, random_state=42, stratify=labels
)

rf = RandomForestClassifier(n_estimators=200, random_state=42)
rf.fit(X_train, y_train)

y_pred = rf.predict(X_test)
acc = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred, output_dict=True)
cm = confusion_matrix(y_test, y_pred, labels=rf.classes_).tolist()

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

print("Training xong. Mô hình và vectorizer đã lưu vào thư mục models/")
