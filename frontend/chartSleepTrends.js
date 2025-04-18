import { fetchUserLog } from './api.js';

async function drawTimeSeriesChart() {
  const logs = await fetchUserLog(1); // Default to user 1
  if (!logs || logs.length === 0) {
    document.getElementById("timeSeriesChart").innerText = "No sleep data available.";
    return;
  }

  const timestamps = logs.map(log => new Date(log.ts).toLocaleTimeString());
  const temps = logs.map(log => log.temperature);
  const hums = logs.map(log => log.humidity);
  const hr = logs.map(log => log.heartrate);

  const traces = [
    {
      x: timestamps,
      y: temps,
      name: 'Temperature (°C)',
      type: 'scatter',
      line: { shape: 'spline' }
    },
    {
      x: timestamps,
      y: hums,
      name: 'Humidity (%)',
      type: 'scatter',
      line: { shape: 'spline' }
    },
    {
      x: timestamps,
      y: hr,
      name: 'Heart Rate (bpm)',
      type: 'scatter',
      line: { shape: 'spline' }
    }
  ];

  const layout = {
    title: 'Environmental Metrics Over Time',
    xaxis: { title: 'Time' },
    yaxis: { title: 'Value' },
    legend: { orientation: 'h' }
  };

  Plotly.newPlot('timeSeriesChart', traces, layout);
}

// Initialize the chart
drawTimeSeriesChart();