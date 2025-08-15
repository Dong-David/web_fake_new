const users = [
  { username: "admin", password: "123" },
  { username: "linhdan", password: "123" },
  { username: "khaidong", password: "123" },
  { username: "phuongthao", password: "123" },
  { username: "minhtoan", password: "123" },
  { username: "nhatminh", password: "123" },
];

document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");
  const username = document.querySelector("#username");
  const password = document.querySelector("#password");

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const userValue = username.value.trim();
    const passValue = password.value.trim();

    const validUser = users.find(
      (u) => u.username === userValue && u.password === passValue
    );

    if (!validUser) {
      form.classList.add("shake");
      setTimeout(() => {
        form.classList.remove("shake");
        username.value = "";
        password.value = "";
        username.focus();
      }, 300);
    } else {
      window.location.href = `account.html?user=${encodeURIComponent(
        validUser.username
      )}`;
    }
  });
});

const forgotModal = document.getElementById("forgotModal");
const forgotBtn = document.querySelector(".remember-forgot a");
const closeBtn = document.querySelector(".close");
const forgotForm = document.getElementById("forgotForm");

forgotBtn.addEventListener("click", function (e) {
  e.preventDefault();
  forgotModal.style.display = "block";
});

closeBtn.addEventListener("click", function () {
  forgotModal.style.display = "none";
});

window.addEventListener("click", function (e) {
  if (e.target == forgotModal) {
    forgotModal.style.display = "none";
  }
});

forgotForm.addEventListener("submit", function (e) {
  e.preventDefault();

  const forgotEmail = document.getElementById("forgotEmail");
  const emailValue = forgotEmail.value.trim();

  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (emailValue === "" || !emailPattern.test(emailValue)) {
    forgotForm.classList.add("shake");
    setTimeout(() => {
      forgotForm.classList.remove("shake");
      forgotEmail.value = "";
      forgotEmail.focus();
    }, 300);
    return;
  }

  alert(`Check your email (${emailValue}) (demo).`);
  forgotModal.style.display = "none";
  forgotForm.reset();
});
