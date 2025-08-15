const params = new URLSearchParams(window.location.search);
const username = params.get("user") || "Guest";
document.getElementById("welcome").textContent = `Welcome, ${username}!`;
