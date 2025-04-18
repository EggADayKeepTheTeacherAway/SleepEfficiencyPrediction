// dashboard.js

async function fetchEfficiency(userId = 1) {
  const response = await fetch('http://localhost:3000/graphql', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify({
      query: `
        {
          efficiency(userId: ${userId}) {
            light
            rem
            deep
            smoke
            exercise
            efficiency
          }
        }
      `
    })
  });

  const result = await response.json();
  return result?.data?.efficiency;
}

export async function renderSleepStageChart() {
  const data = await fetchEfficiency();

  if (!data) {
    document.getElementById("sleepStageChart").innerText = "Failed to fetch efficiency data.";
    return;
  }

  const chartData = [{
    values: [data.light, data.rem, data.deep],
    labels: ['Light Sleep', 'REM Sleep', 'Deep Sleep'],
    type: 'pie',
    hole: 0.4,
    textinfo: 'label+percent',
    textposition: 'inside',
  }];

  const layout = {
    title: `Sleep Stage Breakdown - Efficiency Score: ${data.efficiency.toFixed(2)}%`,
    height: 400,
    width: 500,
  };

  Plotly.newPlot("sleepStageChart", chartData, layout);
}

// Call it on DOMContentLoaded if needed
document.addEventListener("DOMContentLoaded", () => {
  renderSleepStageChart();
});

async function drawEnvironmentalTrends() {
  const resp = await fetch("http://localhost:3000/graphql", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json"
    },
    body: JSON.stringify({
      query: `
        {
          log(userId: 1) {
            ts
            temperature
            humidity
            heartrate
          }
        }
      `
    })
  });

  const result = await resp.json();
  const logs = result?.data?.log;

  if (!logs) {
    document.getElementById("timeSeriesChart").innerText = "Failed to load logs.";
    return;
  }

  const timestamps = logs.map(row => new Date(row.ts).toLocaleTimeString());
  const temp = logs.map(row => row.temperature);
  const humidity = logs.map(row => row.humidity);
  const heartRate = logs.map(row => row.heartrate);

  const traces = [
    { x: timestamps, y: temp, name: "🌡️ Temp (°C)", type: "scatter" },
    { x: timestamps, y: humidity, name: "💧 Humidity (%)", type: "scatter" },
    { x: timestamps, y: heartRate, name: "❤️ Heart Rate (bpm)", type: "scatter" }
  ];

  Plotly.newPlot("timeSeriesChart", traces, {
    title: "Environmental & Heart Rate Trends",
    xaxis: { title: "Timestamp" },
    yaxis: { title: "Value" },
    legend: { orientation: "h" }
  });
}

drawEnvironmentalTrends();
