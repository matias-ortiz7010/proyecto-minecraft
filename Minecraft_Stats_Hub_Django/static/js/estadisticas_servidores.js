"use strict";
(function () {
  const el = document.getElementById("puntos-servidores");
  const canvas = document.getElementById("grafico-servidor");
  if (!el || !canvas) return;
  const error = document.getElementById("grafico-error");
  if (!window.Chart) {
    if (error) error.hidden = false;
    return;
  }
  let puntos;
  try { puntos = JSON.parse(el.textContent); }
  catch (_) { if (error) error.hidden = false; return; }
  if (!Array.isArray(puntos) || !puntos.length) return;
  const formatoFecha = new Intl.DateTimeFormat("es-AR", { day:"2-digit", month:"2-digit", hour:"2-digit", minute:"2-digit" });
  const etiquetas = puntos.map(p => formatoFecha.format(new Date(p.fecha)));
  const valores = puntos.map(p => p.online ? p.jugadores : null);
  new Chart(canvas, {
    type: "line",
    data: {
      labels: etiquetas,
      datasets: [{
        label: "Jugadores conectados",
        data: valores,
        borderColor: "#82d600",
        backgroundColor: "rgba(130,214,0,0.10)",
        pointRadius: puntos.length > 100 ? 0 : 3,
        pointHoverRadius: 5,
        borderWidth: 2,
        tension: 0.15,
        spanGaps: false,
        fill: true,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { intersect:false, mode:"index" },
      plugins: { legend:{ labels:{ color:"#e8f3e8" } }, tooltip:{ callbacks: {
        title: (items) => items.length ? new Date(puntos[items[0].dataIndex].fecha).toLocaleString("es-AR") : ""
      } } },
      scales: {
        x: { ticks:{ color:"#c7d3c9", maxTicksLimit:10 }, grid:{ color:"rgba(180,220,190,0.08)" } },
        y: { beginAtZero: true, ticks:{ color:"#c7d3c9", precision:0 }, grid:{ color:"rgba(180,220,190,0.08)" } }
      }
    }
  });
})();
