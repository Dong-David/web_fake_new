const params = new URLSearchParams(window.location.search);
const username = params.get("user") || "Guest";

const welcomeEl = document.getElementById("welcome");
if (welcomeEl) {
  welcomeEl.textContent = `Welcome, ${username}!`;
}

const logoutBtn = document.getElementById("logout-btn");
if (logoutBtn) {
  logoutBtn.addEventListener("click", () => {
    localStorage.removeItem("username");
    window.location.href = "HomePage.html";
  });
}

const checkBtn = document.getElementById("check-btn");
if (checkBtn) {
  checkBtn.addEventListener("click", async () => {
    const input = document.getElementById("news-input").value.trim();
    const resultBox = document.getElementById("result-box");

    if (!input) {
      resultBox.innerHTML = `<p style="color:yellow;">⚠ Please enter news content to check!</p>`;
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:5000/check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: input }),
      });
      const data = await response.json();

      if (data.result && data.result.toLowerCase() === "fake") {
        resultBox.innerHTML = `
          <p style="color:red;">This news might be fake!</p>
          <p><strong>Confidence:</strong> ${(data.confidence * 100).toFixed(
            2
          )}%</p>
        `;
      } else {
        resultBox.innerHTML = `
          <p style="color:lightgreen;">This news seems reliable.</p>
          <p><strong>Confidence:</strong> ${(data.confidence * 100).toFixed(
            2
          )}%</p>
        `;
      }
    } catch (err) {
      resultBox.innerHTML = `<p style="color:orange;">Error checking news.</p>`;
    }
  });
}
