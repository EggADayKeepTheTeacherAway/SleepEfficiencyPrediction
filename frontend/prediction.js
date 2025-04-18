document.addEventListener("DOMContentLoaded", () => {
  const username = localStorage.getItem("currentUser");
  const userDB = JSON.parse(localStorage.getItem("userDatabase")) || [];

  const fallbackMap = {
    riccardo: 1,
    rattanan: 2
  };

  const userId = fallbackMap[username] || 1;

  const predictBtn = document.getElementById("predict-btn");
  const resultSection = document.getElementById("prediction-result");
  const predictedEfficiency = document.getElementById("predicted-efficiency");
  const userSmoke = document.getElementById("user-smoke");
  const userExercise = document.getElementById("user-exercise");

  predictBtn.addEventListener("click", async () => {
    const selectedDate = document.getElementById("predict-date").value;
    if (!selectedDate) return alert("Please select a date.");

    try {
      const response = await fetch("http://localhost:3000/graphql", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify({
          query: `{
            efficiency(userId: ${userId}) {
              light
              rem
              deep
              efficiency
              smoke
              exercise
            }
            log(userId: ${userId}) {
              ts
              temperature
              humidity
              heartrate
            }
          }`
        })
      });

      const json = await response.json();
      const efficiency = json?.data?.efficiency;
      const logs = json?.data?.log;

      if (!efficiency || !logs) {
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