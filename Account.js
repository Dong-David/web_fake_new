const username = localStorage.getItem("username") || "User";
const welcomeTextEl = document.getElementById("welcome-text");

if (welcomeTextEl) {
  welcomeTextEl.textContent = `Welcome, ${username}!`;
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
  checkBtn.addEventListener("click", () => {
    const input = document.getElementById("news-input").value.trim();
    const resultBox = document.getElementById("result-box");

    if (!input) {
      resultBox.innerHTML = `<p style="color:yellow;">⚠ Please enter news content to check!</p>`;
      return;
    }

    const random = Math.random();
    if (random > 0.5) {
      resultBox.innerHTML = `<p style="color:lightgreen;">This news seems reliable.</p>`;
    } else {
      resultBox.innerHTML = `<p style="color:red;">This news might be fake!</p>`;
    }
  });
}
