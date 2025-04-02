/* global Chart, fetch */
document.addEventListener("DOMContentLoaded", function () {
  fetch("/api/summary/")
    .then((response) => response.json())
    .then((data) => {
      renderPieChart(data);
      renderBarChart(data);
    })
    .catch((error) => {
      console.error("Error loading analytics data:", error);
    });
});

function renderPieChart(data) {
  const ctx = document.getElementById("budgetPieChart").getContext("2d");

  const filtered = data.filter((item) => item.spent_amount > 0);
  const labels = filtered.map((item) => item.category);
  const spentData = filtered.map((item) => item.spent_amount);

  new Chart(ctx, {
    type: "pie",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Spent per Category",
          data: spentData,
          backgroundColor: [
            "#3498db", "#1abc9c", "#9b59b6", "#f39c12", "#e74c3c", "#2ecc71", "#34495e",
          ],
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: "Spending Distribution (Pie Chart)",
        },
        legend: {
          position: "bottom",
        },
      },
    },
  });
}

function renderBarChart(data) {
  const ctx = document.getElementById("budgetBarChart").getContext("2d");

  const labels = data.map((item) => item.category);
  const allocated = data.map((item) => item.allocated_amount);
  const spent = data.map((item) => item.spent_amount);

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Allocated",
          data: allocated,
          backgroundColor: "#3498db",
        },
        {
          label: "Spent",
          data: spent,
          backgroundColor: "#e74c3c",
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: "Allocated vs Spent (Bar Chart)",
        },
      },
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });
}
