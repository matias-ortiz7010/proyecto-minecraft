const searchInput = document.getElementById('search');
const result = document.getElementById('resultado');
const searchButton = document.getElementById('search-button');
const endpoints = window.MSH_ENDPOINTS || {};

function addLine(label, value) {
  const p = document.createElement('p');
  const strong = document.createElement('strong');
  strong.textContent = `${label}: `;
  p.append(strong, document.createTextNode(value ?? '—'));
  result.appendChild(p);
}

async function buscar() {
  const value = searchInput.value.trim();
  result.replaceChildren();

  if (!value) {
    result.textContent = 'Escribí el nombre de un jugador.';
    return;
  }

  searchButton.disabled = true;
  searchButton.textContent = 'Buscando...';
  result.textContent = 'Consultando Django...';

  try {
    const response = await fetch(`${endpoints.playerSearch}?q=${encodeURIComponent(value)}`);
    const data = await response.json();
    result.replaceChildren();

    if (!response.ok || !data.ok) {
      result.textContent = data.error || 'No se pudo buscar el jugador.';
      return;
    }

    const player = data.jugador;
    const title = document.createElement('h3');
    title.textContent = player.nombre;
    result.appendChild(title);
    addLine('UUID', player.uuid || 'Sin datos');
    if (player.pais) addLine('País', player.pais);

    if (player.pvp) {
      addLine('PvP', `${player.pvp.victorias} victorias · ${player.pvp.derrotas} derrotas · ${player.pvp.winrate}% winrate`);
      addLine('Kills / racha', `${player.pvp.kills} / ${player.pvp.racha}`);
    }

    if (player.mejor_speedrun) {
      addLine('Mejor speedrun', `${player.mejor_speedrun.tiempo} · ${player.mejor_speedrun.categoria} · ${player.mejor_speedrun.version || 'versión sin datos'}`);
    }
  } catch (error) {
    result.textContent = 'No se pudo conectar con el backend de Django.';
  } finally {
    searchButton.disabled = false;
    searchButton.textContent = 'Buscar';
  }
}

searchButton?.addEventListener('click', buscar);
searchInput?.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') buscar();
});

const chartElement = document.getElementById('chart');
if (chartElement && window.Chart) {
  const labelsElement = document.getElementById('chart-labels');
  const valuesElement = document.getElementById('chart-values');
  const labels = labelsElement ? JSON.parse(labelsElement.textContent) : [];
  const values = valuesElement ? JSON.parse(valuesElement.textContent) : [];

  new Chart(chartElement, {
    type: 'bar',
    data: {
      labels,
      datasets: [{ label: 'Tiempo (segundos)', data: values }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { title: { display: true, text: 'Segundos' } }
      }
    }
  });
}

async function refreshSummary() {
  if (!endpoints.summary) return;
  try {
    const response = await fetch(endpoints.summary, { cache: 'no-store' });
    if (!response.ok) return;
    const data = await response.json();
    document.getElementById('record-value').textContent = data.record?.tiempo || '—';
    document.getElementById('player-value').textContent = data.jugador_top || '—';
    document.getElementById('server-value').textContent = data.servidor_top || '—';
    document.getElementById('mod-value').textContent = data.mod_top || '—';
  } catch (_) {
    // Si el servidor está momentáneamente caído, conservamos lo último mostrado.
  }
}

async function refreshServers() {
  if (!endpoints.servers) return;
  const body = document.getElementById('servers-body');
  const status = document.getElementById('server-refresh-status');
  if (!body) return;

  try {
    const response = await fetch(endpoints.servers, { cache: 'no-store' });
    if (!response.ok) throw new Error('HTTP error');
    const data = await response.json();

    body.replaceChildren();
    if (!data.servidores.length) {
      const row = document.createElement('tr');
      const cell = document.createElement('td');
      cell.colSpan = 4;
      cell.textContent = 'Todavía no hay servidores cargados.';
      row.appendChild(cell);
      body.appendChild(row);
    } else {
      for (const server of data.servidores) {
        const row = document.createElement('tr');
        for (const value of [server.nombre, server.ip, server.jugadores, server.online ? '🟢 Online' : '🔴 Offline']) {
          const cell = document.createElement('td');
          cell.textContent = value;
          row.appendChild(cell);
        }
        body.appendChild(row);
      }
    }
    if (status) status.textContent = `Actualizado ${new Date().toLocaleTimeString()}`;
  } catch (_) {
    if (status) status.textContent = 'No se pudo actualizar';
  }
}

setInterval(() => {
  refreshSummary();
  refreshServers();
}, 30000);
