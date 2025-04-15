document.addEventListener('DOMContentLoaded', () => {
  const sections = document.querySelectorAll('.content-section');
  sections.forEach((section, index) => {
    section.classList.toggle('active', index === 0);
  });

  // Sleep Duration vs Sleep Quality
  const sleepDurationCtx = document.getElementById('sleepDurationChart');
  new Chart(sleepDurationCtx, {
    type: 'line',
    data: {
      labels: ['Mar 9', 'Mar 10', 'Mar 11', 'Mar 12', 'Mar 13'],
      datasets: [
        {
          label: 'Sleep Duration (hrs)',
          data: [8.5, 8.2, 1.5, 8.5, 1.2],
          borderColor: '#4a90e2',
          fill: false
        },
        {
          label: 'Sleep Quality (%)',
          data: [100, 100, 69, 100, 60],
          borderColor: '#e24a90',
          fill: false
        }
      ]
    }
  });

  // Heart Rate
  const heartRateCtx = document.getElementById('heartRateChart');
  new Chart(heartRateCtx, {
    type: 'line',
    data: {
      labels: ['Mar 9', 'Mar 10', 'Mar 11', 'Mar 12', 'Mar 13'],
      datasets: [
        {
          label: 'Avg Heart Rate (bpm)',
          data: [71, 71, 70, 70, 71],
          borderColor: '#f39c12',
          fill: true
        }
      ]
    }
  });

  // Temperature and Humidity
  const envCtx = document.getElementById('envConditionsChart');
  new Chart(envCtx, {
    type: 'bar',
    data: {
      labels: ['Mar 9', 'Mar 10', 'Mar 11', 'Mar 12', 'Mar 13'],
      datasets: [
        {
          label: 'Humidity (%)',
          data: [89, 88, 81, 68, 68],
          backgroundColor: '#3498db'
        },
        {
          label: 'Temperature (°C)',
          data: [25, 35, 27, 31, 35],
          backgroundColor: '#e67e22'
        }
      ]
    }
  });

  // Quality by Day
  const qualityCtx = document.getElementById('qualityByDayChart');
  new Chart(qualityCtx, {
    type: 'bar',
    data: {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      datasets: [
        {
          label: 'Avg Sleep Quality (%)',
          data: [95, 97, 100, 80, 90, 85, 100],
          backgroundColor: '#2ecc71'
        }
      ]
    }
  });
});


function toggleSection(id) {
  document.querySelectorAll('.content-section').forEach(section => {
    section.classList.remove('active');
  });
  document.getElementById(id).classList.add('active');
}

// Seed users from users.json only if not present in localStorage
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

// Toggle section visibility
function toggleSection(id) {
  document.querySelectorAll(".content-section").forEach((section) => {
    section.classList.remove("active");
  });
  document.getElementById(id).classList.add("active");
}

// Validate login from localStorage
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

// Register user into localStorage
function registerUser() {
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

// Init everything on DOM load
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