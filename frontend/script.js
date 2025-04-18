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
