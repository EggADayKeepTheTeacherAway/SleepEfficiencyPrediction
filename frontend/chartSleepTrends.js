async function fetchSleepLog(userId = 1) {
  const res = await fetch('http://localhost:3000/graphql', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify({
      query: `
        {
          log(userId: ${userId}) {
            ts
            temperature
            humidity
            heartrate
          }
        }
      `
    })
  });

  const result = await res.json();
  return result.data.log;
}

async function drawTimeSeriesChart() {
  const logs = await fetchSleepLog();
  if (!logs || logs.length === 0) return;

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