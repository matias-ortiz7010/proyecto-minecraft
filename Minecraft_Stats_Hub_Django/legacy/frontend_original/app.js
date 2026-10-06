const demo = {
  dream: { name: 'Dream', uuid: 'ec70bcaf...', stats: '540 victorias PvP' },
  lowk3y_: { name: 'lowk3y_', uuid: 'demo-uuid', stats: 'Récord mundial' }
};

const searchInput = document.getElementById('search');
const result = document.getElementById('resultado');
const searchButton = document.getElementById('search-button');
const logo = document.getElementById('site-logo');

// El logo del ZIP original está vacío. Cuando pongas una imagen real en
// assets/logo.png aparecerá automáticamente. Mientras tanto se oculta.
logo.addEventListener('error', () => {
  logo.hidden = true;
});

function buscar() {
  const rawValue = searchInput.value.trim();
  const key = rawValue.toLowerCase();
  const player = demo[key];

  result.replaceChildren();

  const name = document.createElement('p');
  const strong = document.createElement('b');
  strong.textContent = rawValue || 'Sin jugador';
  name.appendChild(strong);

  const uuid = document.createElement('p');
  uuid.textContent = `UUID: ${player?.uuid ?? 'Sin datos'}`;

  const stats = document.createElement('p');
  stats.textContent = player?.stats ?? 'No encontrado';

  result.append(name, uuid, stats);
}

searchButton.addEventListener('click', buscar);
searchInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') buscar();
});

const chartElement = document.getElementById('chart');
if (chartElement && window.Chart) {
  new Chart(chartElement, {
    type: 'line',
    data: {
      labels: ['2021', '2022', '2023', '2024', '2025'],
      datasets: [{ data: [576, 495, 465, 432, 410] }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } }
    }
  });
}
