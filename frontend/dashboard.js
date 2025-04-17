<script type="module" src="dashboard.js"></script>

import { getSleepData } from './api.js';

document.addEventListener('DOMContentLoaded', async () => {
  const data = await getSleepData();

  // Format data by date and average per day
  const grouped = {};
  data.forEach(entry => {
    const date = entry.start_sleep.split(' ')[0];
    if (!grouped[date]) grouped[date] = { duration: 0, quality: 0, count: 0 };
    grouped[date].duration += parseFloat(entry.time_in_bed);
    grouped[date].quality += parseInt(entry.sleep_quality);
    grouped[date].count += 1;
  });

  const labels = Object.keys(grouped);
  const durations = labels.map(date => (grouped[date].duration / grouped[date].count).toFixed(2));
  const qualities = labels.map(date => (grouped[date].quality / grouped[date].count).toFixed(2));

  const ctx = document.getElementById('durationQualityChart').getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Sleep Duration (hrs)',
          data: durations,
          borderColor: '#3498db',
          backgroundColor: '#3498db33',
          yAxisID: 'y',
        },
        {
          label: 'Sleep Quality (%)',
          data: qualities,
          borderColor: '#2ecc71',
          backgroundColor: '#2ecc7133',
          yAxisID: 'y1',
        }
      ]
    },
    options: {
      responsive: true,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      stacked: false,
      scales: {
        y: {
          type: 'linear',
          position: 'left',
          title: {
            display: true,
            text: 'Duration (hrs)'
          }
        },
        y1: {
          type: 'linear',
          position: 'right',
          title: {
            display: true,
            text: 'Quality (%)'
          },
          grid: {
            drawOnChartArea: false,
          }
        }
      }
    }
  });
});