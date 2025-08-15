document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("registerForm");
  const username = document.getElementById("username");
  const email = document.getElementById("email");
  const password = document.getElementById("password");
  const confirmPassword = document.getElementById("confirmPassword");

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const userValue = username.value.trim();
    const emailValue = email.value.trim();
    const passValue = password.value.trim();
    const confirmPassValue = confirmPassword.value.trim();

    if (
      !userValue ||
      !emailValue ||
      !passValue ||
      !confirmPassValue ||
      passValue !== confirmPassValue
    ) {
      form.classList.add("shake");
      setTimeout(() => form.classList.remove("shake"), 300);
    } else {
      alert("Đăng ký thành công!");
      window.location.href = "LoginPage.html";
    }
  });
});
