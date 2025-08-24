import os, joblib, json
from flask import Flask, request, jsonify
from flask_cors import CORS
from underthesea import word_tokenize
from langdetect import detect
from deep_translator import GoogleTranslator

# Khởi tạo Flask app
app = Flask(__name__)
CORS(app)

# Đường dẫn thư mục chứa model + vectorizer + metrics
MODEL_DIR = "models"

# Load model và vectorizer
model = joblib.load(os.path.join(MODEL_DIR, "rf_model_vi.pkl"))
vectorizer = joblib.load(os.path.join(MODEL_DIR, "tfidf_vectorizer_vi.pkl"))

# ============================
# API: POST /check
# ============================
@app.route("/check", methods=["POST"])
def check_text():
    try:
        # Lấy dữ liệu từ request
        data = request.get_json(force=True)
        text = data.get("text", "").strip()

        if not text:
            return jsonify({"error": "Empty text"}), 400

        # Phát hiện ngôn ngữ và dịch sang tiếng Việt nếu cần
        try:
            lang = detect(text)
            if lang != "vi":
                text = GoogleTranslator(source="auto", target="vi").translate(text)
        except Exception:
            pass  # Nếu detect/translate lỗi thì vẫn dùng text gốc

        # Tokenize tiếng Việt
        text_tok = " ".join(word_tokenize(text))

        # Vector hóa
        X = vectorizer.transform([text_tok])

        # Dự đoán
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(X)[0]
            pred = model.classes_[proba.argmax()]
            confidence = float(proba.max())
        else:
            pred = model.predict(X)[0]
            confidence = None

        # Chuẩn hóa output (fake/real + subject)
        if "_" in pred:
            fake_real, subject = pred.split("_", 1)
        else:
            fake_real, subject = pred, ""  

        return jsonify({
            "label": pred,           # nhãn đầy đủ
            "fake_real": fake_real,  # fake / real
            "subject": subject,      # chủ đề (trống nếu chưa có)
            "confidence": confidence # độ tin cậy
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================
# API: GET /metrics
# ============================
@app.route("/metrics", methods=["GET"])
def get_metrics():
    try:
        with open(os.path.join(MODEL_DIR, "metrics_vi.json"), "r", encoding="utf-8") as f:
            metrics = json.load(f)
        return jsonify(metrics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================
# Run server
# ============================
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
