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

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    let errorMsg = "";

    if (!userValue || !emailValue || !passValue || !confirmPassValue) {
      errorMsg = "Vui lòng điền đầy đủ tất cả các trường.";
    } else if (!emailPattern.test(emailValue)) {
      errorMsg = "Email không hợp lệ.";
    } else if (passValue !== confirmPassValue) {
      errorMsg = "Mật khẩu không khớp.";
    }

    if (errorMsg) {
      alert(errorMsg);
      form.classList.add("shake");
      setTimeout(() => form.classList.remove("shake"), 300);
      return;
    }

    alert(`Đăng ký thành công! Chào mừng ${userValue}`);
    window.location.href = "LoginPage.html";
  });
});
