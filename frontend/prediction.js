import { fetchEfficiency, fetchUserLog } from './api.js';

document.addEventListener("DOMContentLoaded", () => {
  const currentUser = localStorage.getItem("currentUser");
  const userDB = JSON.parse(localStorage.getItem("userDatabase"));
  const match = userDB?.find(user => user.username === currentUser);
  const userId = match?.user_id || 1; // fallback to 1 if not found

  const predictBtn = document.getElementById("predict-btn");
  const resultSection = document.getElementById("prediction-result");
  const predictedEfficiency = document.getElementById("predicted-efficiency");
  const userSmoke = document.getElementById("user-smoke");
  const userExercise = document.getElementById("user-exercise");

  predictBtn?.addEventListener("click", async () => {
    const selectedDate = document.getElementById("predict-date").value;
    if (!selectedDate) return alert("Please select a date.");

    try {
      // Fetch efficiency data directly from FastAPI
      const efficiency = await fetchEfficiency(userId);
      const logs = await fetchUserLog(userId);

      if (!efficiency || !logs || logs.length === 0) {
        alert("Prediction failed. Try again later.");
        return;
      }

      resultSection.style.display = "block";
      predictedEfficiency.textContent = (efficiency.efficiency * 100).toFixed(2);
      userSmoke.textContent = efficiency.smoke ? "Yes" : "No";
      userExercise.textContent = efficiency.exercise;

      const timestamps = logs.map(row => new Date(row.ts).toLocaleTimeString());
      const temps = logs.map(row => row.temperature);
      const hums = logs.map(row => row.humidity);
      const hrates = logs.map(row => row.heartrate);

      Plotly.newPlot("predictionTrendChart", [
        {
          x: timestamps,
          y: temps,
          name: "🌡️ Temp (°C)",
          type: "scatter"
        },
        {
          x: timestamps,
          y: hums,
          name: "💧 Humidity (%)",
          type: "scatter"
        },
        {
          x: timestamps,
          y: hrates,
          name: "❤️ Heart Rate (bpm)",
          type: "scatter"
        }
      ], {
        title: "Environmental Trends During Sleep",
        margin: { t: 40 },
        xaxis: { title: "Time" },
        yaxis: { title: "Value" },
        legend: { orientation: "h" }
      });

    } catch (error) {
      console.error("Prediction error:", error);
      alert("Prediction failed. Please check your connection or server.");
    }
  });
});