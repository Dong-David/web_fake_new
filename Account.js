document.addEventListener("DOMContentLoaded", () => {
  const checkBtn = document.getElementById("check-btn");
  const logoutBtn = document.getElementById("logout-btn");
  const newsInput = document.getElementById("news-input");
  const resultBox = document.getElementById("result-box");
  const metricsBox = document.getElementById("metrics-box");

  const params = new URLSearchParams(window.location.search);
  const username = params.get("user") || "Guest";

  const welcomeEl = document.getElementById("welcome");
  if (welcomeEl) welcomeEl.textContent = `Welcome, ${username}!`;

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
      const response = await fetch("http://127.0.0.1:5000/check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      if (!response.ok) throw new Error("Check API failed");
      const data = await response.json();

      const label = data.result === "fake" ? "Fake News" : "Real News";
      const conf = (data.confidence * 100).toFixed(2);

      resultBox.innerHTML = `<strong>${label}</strong><br>Confidence: ${conf}%`;

      const metricsResp = await fetch("http://127.0.0.1:5000/metrics");
      if (!metricsResp.ok) throw new Error("Metrics API failed");
      const metrics = await metricsResp.json();

      const cm = metrics.confusion_matrix.matrix;

      let html = `
        <h3>Confusion Matrix</h3>
        <table border="1">
          <tr><th></th><th>Pred Real</th><th>Pred Fake</th></tr>
          <tr><th>Actual Real</th><td>${cm[1][1]}</td><td>${cm[1][0]}</td></tr>
          <tr><th>Actual Fake</th><td>${cm[0][1]}</td><td>${cm[0][0]}</td></tr>
        </table>
      `;
      metricsBox.innerHTML = html;
    } catch (err) {
      resultBox.textContent =
        "Error: Unable to check news. Please try again later.";
      console.error("Backend error:", err);
    }
  });
});
