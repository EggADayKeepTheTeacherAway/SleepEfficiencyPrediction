document.addEventListener("DOMContentLoaded", async () => {
  await seedUsers();

  const currentUser = localStorage.getItem("currentUser");
  if (currentUser) {
    document.getElementById("logged-user").textContent = currentUser;
    showLogoutButton();
  }

  // Login handler
  const loginForm = document.getElementById("login-form");
  if (loginForm) {
    loginForm.addEventListener("submit", validateLogin);
  }

  // Register handler
  const registerForm = document.getElementById("register-form");
  if (registerForm) {
    registerForm.addEventListener("submit", registerUser);
  }
});

// Load default users if localStorage is empty
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

// Login logic
async function validateLogin(event) {
  event.preventDefault();
  const username = document.getElementById("login-username").value.trim();
  const password = document.getElementById("login-password").value.trim();
  const msg = document.getElementById("login-message");

  try {
    const response = await fetch("http://127.0.0.1:8080/sleep-api/user/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username,
        password
      })
    });
    
    const data = await response.json();
    
    if (data.message === "Success") {
      localStorage.setItem("currentUser", username);
      document.getElementById("logged-user").textContent = username;
      msg.textContent = `Welcome, ${username}!`;
      msg.style.color = "green";
      showLogoutButton();
    } else {
      msg.textContent = "Invalid username or password.";
      msg.style.color = "red";
    }
  } catch (error) {
    console.error("Login error:", error);
    msg.textContent = "Login failed. Please check your connection.";
    msg.style.color = "red";
  }
}

// Register logic
async function registerUser(event) {
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

  try {
    const response = await fetch("http://127.0.0.1:8080/sleep-api/user/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username,
        password,
        age: 25, // Default value since not in form
        gender: "male", // Default value since not in form
        smoke,
        exercise
      })
    });
    
    const data = await response.json();
    
    if (data.message === "User Registered") {
      msg.textContent = "✅ Registered successfully! Now you can log in.";
      msg.style.color = "green";
    } else {
      msg.textContent = data.detail || "Registration failed.";
      msg.style.color = "darkorange";
    }
  } catch (error) {
    console.error("Registration error:", error);
    msg.textContent = "Registration failed. Please check your connection.";
    msg.style.color = "red";
  }
}

// Add logout button if not exists
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