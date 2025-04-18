document.addEventListener("DOMContentLoaded", () => {
  const registerForm = document.getElementById("register-form");
  if (registerForm) {
    registerForm.addEventListener("submit", (event) => {
      event.preventDefault();
      const username = document.getElementById("register-username").value.trim();
      const password = document.getElementById("register-password").value.trim();
      const smoke = document.getElementById("register-smoke").value === "true";
      const exercise = parseInt(document.getElementById("register-exercise").value);
      const msg = document.getElementById("register-message");

      if (!username || !password || isNaN(exercise)) {
        msg.textContent = "Please fill all fields correctly.";
        msg.style.color = "orange";
        return;
      }

      const userDB = JSON.parse(localStorage.getItem("userDatabase")) || [];
      const exists = userDB.some(user => user.username === username);

      if (exists) {
        msg.textContent = "Username already exists.";
        msg.style.color = "darkorange";
      } else {
        userDB.push({ username, password, smoke, exercise });
        localStorage.setItem("userDatabase", JSON.stringify(userDB));
        msg.textContent = "✅ Registered successfully! You may now log in.";
        msg.style.color = "green";
      }
    });
  }
});