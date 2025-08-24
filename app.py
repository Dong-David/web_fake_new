import os, joblib, json
from flask import Flask, request, jsonify
from flask_cors import CORS
from underthesea import word_tokenize

app = Flask(__name__)
CORS(app)

MODEL_DIR = "models"
model = joblib.load(os.path.join(MODEL_DIR, "rf_model_vi.pkl"))
vectorizer = joblib.load(os.path.join(MODEL_DIR, "tfidf_vectorizer_vi.pkl"))

@app.route("/check", methods=["POST"])
def check_text():
    try:
        data = request.get_json(force=True)
        text = data.get("text", "").strip()
        if not text:
            return jsonify({"error": "Empty text"}), 400

        text_tok = " ".join(word_tokenize(text))
        X = vectorizer.transform([text_tok])

        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(X)[0]
            pred = model.classes_[proba.argmax()]
            confidence = float(proba.max())
        else:
            pred = model.predict(X)[0]
            confidence = None

        if "_" in pred:
            fake_real, subject = pred.split("_", 1)
        else:
            fake_real, subject = pred, ""

        return jsonify({
            "label": pred,
            "fake_real": fake_real,
            "subject": subject,
            "confidence": confidence
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/metrics", methods=["GET"])
def get_metrics():
    try:
        with open(os.path.join(MODEL_DIR, "metrics_vi.json"), "r", encoding="utf-8") as f:
            metrics = json.load(f)
        return jsonify(metrics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
