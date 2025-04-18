document.addEventListener("DOMContentLoaded", async () => {
  await seedUsers();

  const currentUser = localStorage.getItem("currentUser");
  if (currentUser) {
    document.getElementById("logged-user").textContent = currentUser;
    showLogoutButton();
  }

  // Login
  const loginForm = document.getElementById("login-form");
  if (loginForm) {
    loginForm.addEventListener("submit", validateLogin);
  }

  // Register
  const registerForm = document.getElementById("register-form");
  if (registerForm) {
    registerForm.addEventListener("submit", registerUser);
  }
});

async function seedUsers() {
  if (!localStorage.getItem("userDatabase")) {
    try {
      const res = await fetch("users.json");
      const users = await res.json();
      localStorage.setItem("userDatabase", JSON.stringify(users));
    } catch (err) {
      console.error("Failed to load users.json:", err);
    }
  }
}

function validateLogin(event) {
  event.preventDefault();
  const username = document.getElementById("login-username").value.trim();
  const password = document.getElementById("login-password").value.trim();
  const msg = document.getElementById("login-message");

  const userDB = JSON.parse(localStorage.getItem("userDatabase")) || [];
  const match = userDB.find(user => user.username === username && user.password === password);

  if (match) {
    localStorage.setItem("currentUser", username);
    document.getElementById("logged-user").textContent = username;
    msg.textContent = `Welcome, ${username}!`;
    msg.style.color = "green";
    showLogoutButton();
  } else {
    msg.textContent = "Invalid username or password.";
    msg.style.color = "red";
  }
}

function registerUser(event) {
  event.preventDefault();
  const username = document.getElementById("register-username").value.trim();
  const password = document.getElementById("register-password").value.trim();
  const smoke = document.getElementById("register-smoke").value === "true";
  const exercise = parseInt(document.getElementById("register-exercise").value, 10);
  const msg = document.getElementById("register-message");

  if (!username || !password || isNaN(exercise)) {
    msg.textContent = "All fields are required.";
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
    msg.textContent = "✅ Registered successfully! Now you can log in.";
    msg.style.color = "green";
  }
}

function showLogoutButton() {
  const profileBox = document.getElementById("profile-box");
  if (!document.getElementById("logout-btn")) {
    const btn = document.createElement("button");
    btn.id = "logout-btn";
    btn.textContent = "Logout";
    btn.style.marginLeft = "1rem";
    btn.onclick = () => {
      localStorage.removeItem("currentUser");
      document.getElementById("logged-user").textContent = "None";
      location.reload();
    };
    profileBox.appendChild(btn);
  }
}