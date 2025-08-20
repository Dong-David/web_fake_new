document.addEventListener("DOMContentLoaded", () => {
  const checkBtn = document.getElementById("check-btn");
  const logoutBtn = document.getElementById("logout-btn");
  const newsInput = document.getElementById("news-input");
  const resultBox = document.getElementById("result-box");
  const metricsBox = document.getElementById("metrics-box");

  const params = new URLSearchParams(window.location.search);
  const username = params.get("user") || "Guest";

  const welcomeEl = document.getElementById("welcome");
  if (welcomeEl) {
    welcomeEl.textContent = `Welcome, ${username}!`;
  }

  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      alert("Logging out...");
      localStorage.removeItem("username");
      window.location.href = "HomePage.html";
    });
  }

  checkBtn.addEventListener("click", async () => {
    const text = newsInput.value.trim();
    if (!text) {
      resultBox.textContent = "Please enter some news content.";
      return;
    }

    resultBox.textContent = "Checking...";
    metricsBox.innerHTML = "";

    try {
      const response = await fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      const data = await response.json();

      const label = data.prediction === "FAKE" ? "Fake News" : "Real News";
      const conf = (data.confidence * 100).toFixed(2);

      resultBox.innerHTML = `<strong>${label}</strong><br>Confidence: ${conf}%`;

      if (data.metrics) {
        const { accuracy, precision, recall, f1, confusion_matrix } =
          data.metrics;

        let html = `
          <h3>Model Evaluation Metrics</h3>
          <p>Accuracy: ${(accuracy * 100).toFixed(2)}%</p>
          <p>Precision: ${(precision * 100).toFixed(2)}%</p>
          <p>Recall: ${(recall * 100).toFixed(2)}%</p>
          <p>F1 Score: ${(f1 * 100).toFixed(2)}%</p>
          <h4>Confusion Matrix</h4>
          <table>
            <tr><th></th><th>Pred Real</th><th>Pred Fake</th></tr>
            <tr><th>Actual Real</th><td>${confusion_matrix[0][0]}</td><td>${
          confusion_matrix[0][1]
        }</td></tr>
            <tr><th>Actual Fake</th><td>${confusion_matrix[1][0]}</td><td>${
          confusion_matrix[1][1]
        }</td></tr>
          </table>
        `;
        metricsBox.innerHTML = html;
      }
    } catch (err) {
      resultBox.textContent =
        "Error: Unable to check news. Please try again later.";
      console.error("Backend error:", err);
    }
  });
});
