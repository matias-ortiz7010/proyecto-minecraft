document.addEventListener("DOMContentLoaded", () => {
  const el = document.getElementById("pvp-local-datos");
  const chart = document.getElementById("pvp-chart");
  if (!el || !chart || typeof Chart === "undefined") return;
  let data;
  try { data = JSON.parse(el.textContent); } catch (_) { return; }
  if (!data.nombres?.length) return;
  new Chart(chart, {
    type: "bar",
    data: {
      labels: data.nombres,
      datasets: [
        {label: "Victorias", data: data.victorias, backgroundColor: "#8bdd17"},
        {label: "Derrotas", data: data.derrotas, backgroundColor: "#596b5e"},
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {legend: {labels: {color: "#ecf6eb"}}},
      scales: {x: {ticks: {color: "#c9dac6"}, grid: {color: "#1e2e24"}},
               y: {beginAtZero: true, ticks: {color: "#c9dac6", precision: 0}, grid: {color: "#27382c"}}},
    },
  });
});
