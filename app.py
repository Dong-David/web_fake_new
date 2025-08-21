import os, joblib, json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

MODEL_DIR = "models"
model = joblib.load(os.path.join(MODEL_DIR, "model.pkl"))
vectorizer = joblib.load(os.path.join(MODEL_DIR, "vectorizer.pkl"))

@app.route("/check", methods=["POST"])
def check_text():
    data = request.get_json()
    text = data.get("text", "")

    if not text.strip():
        return jsonify({"error": "Empty text"}), 400

    X = vectorizer.transform([text])
    proba = model.predict_proba(X)[0]
    pred = model.classes_[proba.argmax()]
    confidence = float(proba.max())

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

@app.route("/metrics", methods=["GET"])
def get_metrics():
    try:
        with open(os.path.join(MODEL_DIR, "metrics.json"), "r") as f:
            metrics = json.load(f)
        return jsonify(metrics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
