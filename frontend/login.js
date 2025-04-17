document.addEventListener("DOMContentLoaded", async () => {
  await seedUsers();

  const sections = document.querySelectorAll(".content-section");
  sections.forEach((section, index) => {
    section.classList.toggle("active", index === 0);
  });

  const currentUser = localStorage.getItem("currentUser");
  if (currentUser) {
    document.getElementById("logged-user").textContent = currentUser;
    showLogoutButton();
  }

  const loginForm = document.getElementById("login-form");
  if (loginForm) loginForm.addEventListener("submit", validateLogin);

  const registerBtn = document.querySelector(".register-btn[type='button']");
  if (registerBtn) registerBtn.addEventListener("click", registerUser);
});

// Toggle section visibility
export function toggleSection(id) {
  document.querySelectorAll(".content-section").forEach((section) => {
    section.classList.remove("active");
  });
  document.getElementById(id).classList.add("active");
}

// Seed users from users.json only if not present in localStorage
export async function seedUsers() {
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

// Validate login from localStorage
export function validateLogin(event) {
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

// Register user into localStorage
export function registerUser() {
  const username = document.getElementById("login-username").value.trim();
  const password = document.getElementById("login-password").value.trim();
  const msg = document.getElementById("login-message");

  if (!username || !password) {
    msg.textContent = "Username and password required.";
    msg.style.color = "orange";
    return;
  }

  const userDB = JSON.parse(localStorage.getItem("userDatabase")) || [];
  const exists = userDB.some(user => user.username === username);

  if (exists) {
    msg.textContent = "Username already exists.";
    msg.style.color = "darkorange";
  } else {
    userDB.push({ username, password });
    localStorage.setItem("userDatabase", JSON.stringify(userDB));
    msg.textContent = "✅ Registered successfully! Now you can log in.";
    msg.style.color = "green";
  }
}

// Show logout button
export function showLogoutButton() {
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
