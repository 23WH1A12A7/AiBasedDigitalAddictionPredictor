function showAuthMessage(target, message, type = "error") {
  if (!target) return;
  target.textContent = message;
  target.dataset.state = type;
  target.style.display = "flex";
}

function setLoading(button, loadingText, isLoading) {
  if (!button) return;
  button.disabled = isLoading;
  button.dataset.originalText = button.dataset.originalText || button.textContent.trim();
  button.textContent = isLoading ? loadingText : button.dataset.originalText;
}

async function handleLoginForm(form) {
  return form;
}

async function handleSignupForm(form) {
  return form;
}

function wireLogoutLinks() {
  document.querySelectorAll("[data-logout-link]").forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      localStorage.removeItem("authToken");
      window.location.href = "/logout";
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  wireLogoutLinks();
  const loginForm = document.getElementById("loginForm");
  const signupForm = document.getElementById("signupForm");

  if (loginForm) {
    handleLoginForm(loginForm);
  }

  if (signupForm) {
    handleSignupForm(signupForm);
  }
});
