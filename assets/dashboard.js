const MASTER_INTEGRATED = 'data/communal_master/chile_digital_inclusion_communes_2026_integrated.csv';
const MASTER_BASE = 'data/communal_master/chile_digital_inclusion_communes_2026.csv';
const GEO_URL = 'geo/chile_communes.geojson';
const SECTOR_URL = 'data/subtel_sector_2026/sector_snapshot_2026q1.csv';

const indicators = {
  hogares_sin_internet_pct: { label: 'Hogares sin Internet', unit: '%', digits: 1, higherConcern: true },
  hogares_trampa_movil_pct: { label: 'Dependencia móvil', unit: '%', digits: 1, higherConcern: true },
  hogares_con_internet_fija_pct: { label: 'Internet fija', unit: '%', digits: 1, higherConcern: false },
  hogares_con_computador_pct: { label: 'Hogares con computador', unit: '%', digits: 1, higherConcern: false },
  hogares_rurales_pct: { label: 'Ruralidad de hogares', unit: '%', digits: 1, higherConcern: true },
  pct_hogares_con_mayores: { label: 'Hogares con personas mayores', unit: '%', digits: 1, higherConcern: true },
  pct_hogares_con_discapacidad: { label: 'Hogares con discapacidad', unit: '%', digits: 1, higherConcern: true },
  mobile_5g_operators_present_2025m03: { label: 'Operadores con registros 5G · mar 2025', unit: ' de 4', digits: 0, higherConcern: false },
  mobile_5g_point_records_2025m03: { label: 'Registros de red 5G · mar 2025', unit: '', digits: 0, higherConcern: false },
  mobile_4g_operators_present_2025m03: { label: 'Operadores con registros 4G · mar 2025', unit: ' de 4', digits: 0, higherConcern: false },
  mobile_4g_point_records_2025m03: { label: 'Registros de red 4G · mar 2025', unit: '', digits: 0, higherConcern: false },
  fixed_access_public_operators_present: { label: 'Operadores con trazado RedAcceso público', unit: '', digits: 0, higherConcern: false },
  subtel_fixed_residential_per_100_censo_households_2026m03: { label: 'Conexiones fijas residenciales por 100 hogares · mar 2026', unit: '', digits: 1, higherConcern: false },
  ookla_fixed_download_mbps_2026q1: { label: 'Ookla fijo Q1 2026 · descarga', unit: ' Mbps', digits: 1, higherConcern: false },
  ookla_mobile_download_mbps_2026q1: { label: 'Ookla móvil Q1 2026 · descarga', unit: ' Mbps', digits: 1, higherConcern: false },
  ookla_fixed_latency_ms_2026q1: { label: 'Ookla fijo Q1 2026 · latencia', unit: ' ms', digits: 1, higherConcern: true },
  ookla_mobile_latency_ms_2026q1: { label: 'Ookla móvil Q1 2026 · latencia', unit: ' ms', digits: 1, higherConcern: true },
};

const map = L.map('map', { zoomControl: true }).setView([-33.45, -70.65], 4);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 18,
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

let master = [];
let sector = [];
let byCode = new Map();
let geoLayer;
let selectedIndicator = 'hogares_sin_internet_pct';
let selectedCommuneCode = null;
let legend;

function n(v) {
  const x = Number(v);
  return Number.isFinite(x) ? x : null;
}

function sum(field) {
  return d3.sum(master, d => n(d[field]) || 0);
}

function pct(num, den) {
  return den ? (num / den * 100) : null;
}

function formatValue(value, spec = indicators[selectedIndicator]) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return 'N/D';
  return `${Number(value).toLocaleString('es-CL', { minimumFractionDigits: spec.digits, maximumFractionDigits: spec.digits })}${spec.unit}`;
}

function formatInt(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return 'N/D';
  return Math.round(Number(value)).toLocaleString('es-CL');
}

function formatCompact(value) {
  const x = n(value);
  if (x === null) return 'N/D';
  return new Intl.NumberFormat('es-CL', { notation: 'compact', maximumFractionDigits: 2 }).format(x);
}

async function loadMaster() {
  try {
    const rows = await d3.csv(MASTER_INTEGRATED);
    document.getElementById('data-status').textContent = 'Maestro integrado · Censo/Atlas + SUBTEL 4G/5G/RedAcceso + Mineduc + Ookla Q1 2026';
    return rows;
  } catch (err) {
    const rows = await d3.csv(MASTER_BASE);
    document.getElementById('data-status').textContent = 'Maestro base · capas territoriales complementarias no disponibles';
    return rows;
  }
}

async function loadSector() {
  try {
    return await d3.csv(SECTOR_URL);
  } catch (err) {
    console.warn('No se pudo cargar el snapshot sectorial SUBTEL', err);
    return [];
  }
}

function sectorValue(indicator) {
  const row = sector.find(d => d.indicator === indicator);
  return row ? n(row.value) : null;
}

function updateKPIs() {
  const households = sum('hogares_total');
  const validInternet = sum('hogares_validos_internet');
  const disconnected = sum('hogares_sin_internet_n');
  const fixed = sum('hogares_con_internet_fija_n');
  const computers = sum('hogares_con_computador_n');

  document.getElementById('kpi-households').textContent = formatInt(households);
  document.getElementById('kpi-disconnected').textContent = `${formatInt(disconnected)} · ${formatValue(pct(disconnected, validInternet), { digits: 1, unit: '%' })}`;
  document.getElementById('kpi-fixed').textContent = formatValue(pct(fixed, households), { digits: 1, unit: '%' });
  document.getElementById('kpi-computer').textContent = formatValue(pct(computers, households), { digits: 1, unit: '%' });
}

function updateSectorKPIs() {
  document.getElementById('kpi-sector-5g').textContent = formatCompact(sectorValue('accesses_5g'));
  document.getElementById('kpi-sector-fiber').textContent = formatValue(sectorValue('fiber_share_fixed_connections'), { digits: 1, unit: '%' });
  document.getElementById('kpi-sector-fixed-households').textContent = formatValue(sectorValue('fixed_household_penetration_national'), { digits: 1, unit: '%' });
  document.getElementById('kpi-sector-rural-fixed').textContent = formatValue(sectorValue('fixed_household_penetration_rural'), { digits: 1, unit: '%' });
}

function indicatorValues() {
  return master.map(d => n(d[selectedIndicator])).filter(v => v !== null);
}

function makeScale() {
  const values = indicatorValues();
  const extent = d3.extent(values);
  if (!Number.isFinite(extent[0]) || extent[0] === extent[1]) return () => '#d9dee5';
  const spec = indicators[selectedIndicator];
  const interpolator = spec.higherConcern ? d3.interpolateOrRd : d3.interpolateBlues;
  return d3.scaleSequential(interpolator).domain(extent);
}

function updateLegend(scale) {
  if (legend) legend.remove();
  legend = L.control({ position: 'bottomright' });
  legend.onAdd = function () {
    const div = L.DomUtil.create('div', 'legend');
    const values = indicatorValues();
    const [min, max] = d3.extent(values);
    const spec = indicators[selectedIndicator];
    const steps = d3.range(5).map(i => min + (max - min) * i / 4);
    div.innerHTML = `<strong>${spec.label}</strong>` + steps.map(v =>
      `<div class="legend-row"><span class="legend-swatch" style="background:${scale(v)}"></span><span>${formatValue(v, spec)}</span></div>`
    ).join('');
    return div;
  };
  legend.addTo(map);
}

function featureStyle(feature, scale) {
  const code = Number(feature.properties.commune_code);
  const row = byCode.get(code);
  const value = row ? n(row[selectedIndicator]) : null;
  return {
    color: '#ffffff',
    weight: code === selectedCommuneCode ? 2.4 : 0.55,
    opacity: 1,
    fillOpacity: value === null ? 0.18 : 0.78,
    fillColor: value === null ? '#cfd5dc' : scale(value),
  };
}

function popupHTML(code) {
  const d = byCode.get(Number(code));
  if (!d) return 'Sin datos comunales';
  const spec = indicators[selectedIndicator];
  return `
    <strong>${d.comuna_nombre}</strong><br>
    ${d.region_nombre}<br><br>
    ${spec.label}: <strong>${formatValue(n(d[selectedIndicator]), spec)}</strong><br>
    Hogares: ${formatInt(d.hogares_total)}<br>
    Sin Internet: ${formatValue(n(d.hogares_sin_internet_pct), indicators.hogares_sin_internet_pct)}<br>
    Internet fija: ${formatValue(n(d.hogares_con_internet_fija_pct), indicators.hogares_con_internet_fija_pct)}<br>
    Registros 5G: ${formatInt(d.mobile_5g_point_records_2025m03)} · operadores: ${formatValue(n(d.mobile_5g_operators_present_2025m03), indicators.mobile_5g_operators_present_2025m03)}<br>
    Aulas Conectadas 2025: ${formatInt(d.mineduc_aulas_selected_establishments_2025)} seleccionados<br>
    RedAcceso público: ${formatInt(d.fixed_access_public_operators_present)} operadores/entidades con trazado<br>
    Computador: ${formatValue(n(d.hogares_con_computador_pct), indicators.hogares_con_computador_pct)}
  `;
}

function renderMap(geojson) {
  const scale = makeScale();
  if (geoLayer) geoLayer.remove();
  geoLayer = L.geoJSON(geojson, {
    style: f => featureStyle(f, scale),
    onEachFeature: (feature, layer) => {
      const code = Number(feature.properties.commune_code);
      layer.on('click', () => {
        selectedCommuneCode = code;
        layer.bindPopup(popupHTML(code)).openPopup();
        updateDetail(code);
        geoLayer.setStyle(f => featureStyle(f, scale));
      });
      layer.on('mouseover', () => layer.setStyle({ weight: 2 }));
      layer.on('mouseout', () => geoLayer.resetStyle(layer));
    }
  }).addTo(map);
  updateLegend(scale);
}

function renderRanking() {
  const spec = indicators[selectedIndicator];
  const rows = master
    .map(d => ({ ...d, _v: n(d[selectedIndicator]) }))
    .filter(d => d._v !== null)
    .sort((a, b) => spec.higherConcern ? d3.descending(a._v, b._v) : d3.ascending(a._v, b._v))
    .slice(0, 15);

  document.getElementById('ranking-title').textContent = spec.higherConcern ? 'Mayor presión observada' : 'Menor desempeño / disponibilidad';
  document.getElementById('ranking-subtitle').textContent = spec.label;
  document.getElementById('ranking-body').innerHTML = rows.map((d, i) => `
    <tr data-code="${d.comuna}">
      <td>${i + 1}</td>
      <td>${d.comuna_nombre}<br><small>${d.region_nombre}</small></td>
      <td class="value-cell">${formatValue(d._v, spec)}</td>
    </tr>
  `).join('');

  document.querySelectorAll('#ranking-body tr').forEach(tr => {
    tr.addEventListener('click', () => focusCommune(Number(tr.dataset.code)));
  });
}

function updateDetail(code) {
  const d = byCode.get(Number(code));
  if (!d) return;
  document.getElementById('detail-title').textContent = `${d.comuna_nombre} · ${d.region_nombre}`;
  const items = [
    ['Hogares', formatInt(d.hogares_total)],
    ['Sin Internet', formatValue(n(d.hogares_sin_internet_pct), indicators.hogares_sin_internet_pct)],
    ['Dependencia móvil', formatValue(n(d.hogares_trampa_movil_pct), indicators.hogares_trampa_movil_pct)],
    ['Internet fija', formatValue(n(d.hogares_con_internet_fija_pct), indicators.hogares_con_internet_fija_pct)],
    ['Computador', formatValue(n(d.hogares_con_computador_pct), indicators.hogares_con_computador_pct)],
    ['Ruralidad', formatValue(n(d.hogares_rurales_pct), indicators.hogares_rurales_pct)],
    ['Mayores', formatValue(n(d.pct_hogares_con_mayores), indicators.pct_hogares_con_mayores)],
    ['Discapacidad', formatValue(n(d.pct_hogares_con_discapacidad), indicators.pct_hogares_con_discapacidad)],
    ['Registros 4G', formatInt(d.mobile_4g_point_records_2025m03)],
    ['Operadores 4G', formatValue(n(d.mobile_4g_operators_present_2025m03), indicators.mobile_4g_operators_present_2025m03)],
    ['Registros 5G', formatInt(d.mobile_5g_point_records_2025m03)],
    ['Operadores 5G', formatValue(n(d.mobile_5g_operators_present_2025m03), indicators.mobile_5g_operators_present_2025m03)],
    ['Aulas seleccionadas', formatInt(d.mineduc_aulas_selected_establishments_2025)],
    ['Aulas seleccionadas rurales', formatInt(d.mineduc_aulas_selected_rural_establishments_2025)],
    ['Aulas lista de espera', formatInt(d.mineduc_aulas_waitlist_establishments_2025)],
    ['Matrícula en seleccionados', formatInt(d.mineduc_aulas_selected_enrollment_2025)],
    ['Fijo residencial / 100 hogares', formatValue(n(d.subtel_fixed_residential_per_100_censo_households_2026m03), indicators.subtel_fixed_residential_per_100_censo_households_2026m03)],
    ['Conexiones fijas residenciales', formatInt(d.subtel_fixed_connections_residential_2026m03)],
    ['Operadores RedAcceso público', formatInt(d.fixed_access_public_operators_present)],
    ['Capas RedAcceso públicas', formatInt(d.fixed_access_public_layers_present)],
    ['Trazado RedAcceso publicado', n(d.fixed_access_public_linework_length_km) === null ? 'N/D' : `${Number(d.fixed_access_public_linework_length_km).toLocaleString('es-CL', { maximumFractionDigits: 1 })} km`],
    ['Ookla fijo', formatValue(n(d.ookla_fixed_download_mbps_2026q1), indicators.ookla_fixed_download_mbps_2026q1)],
    ['Ookla móvil', formatValue(n(d.ookla_mobile_download_mbps_2026q1), indicators.ookla_mobile_download_mbps_2026q1)],
    ['Tests fijo', formatInt(d.ookla_fixed_tests_2026q1)],
    ['Tests móvil', formatInt(d.ookla_mobile_tests_2026q1)],
  ];
  document.getElementById('detail-grid').innerHTML = items.map(([label, value]) =>
    `<div class="detail-item"><span>${label}</span><strong>${value}</strong></div>`
  ).join('');
}

function focusCommune(code) {
  selectedCommuneCode = code;
  const d = byCode.get(code);
  if (!d) return;
  updateDetail(code);
  if (geoLayer) {
    geoLayer.eachLayer(layer => {
      if (Number(layer.feature.properties.commune_code) === code) {
        map.fitBounds(layer.getBounds(), { maxZoom: 9, padding: [20, 20] });
        layer.bindPopup(popupHTML(code)).openPopup();
      }
    });
    const scale = makeScale();
    geoLayer.setStyle(f => featureStyle(f, scale));
  }
}

function populateIndicatorSelect() {
  const select = document.getElementById('indicator');
  select.innerHTML = Object.entries(indicators).map(([key, spec]) => `<option value="${key}">${spec.label}</option>`).join('');
  select.value = selectedIndicator;
  select.addEventListener('change', () => {
    selectedIndicator = select.value;
    renderMap(window.__geojson);
    renderRanking();
  });
}

function setupSearch() {
  const input = document.getElementById('commune-search');
  input.addEventListener('change', () => {
    const q = input.value.trim().toLocaleLowerCase('es-CL');
    const match = master.find(d => d.comuna_nombre.toLocaleLowerCase('es-CL') === q) ||
      master.find(d => d.comuna_nombre.toLocaleLowerCase('es-CL').includes(q));
    if (match) focusCommune(Number(match.comuna));
  });
}

async function init() {
  try {
    const [rows, geojson, sectorRows] = await Promise.all([loadMaster(), d3.json(GEO_URL), loadSector()]);
    master = rows;
    sector = sectorRows;
    byCode = new Map(master.map(d => [Number(d.comuna), d]));
    window.__geojson = geojson;
    populateIndicatorSelect();
    setupSearch();
    updateKPIs();
    updateSectorKPIs();
    renderMap(geojson);
    renderRanking();
    const first = master.find(d => d.comuna_nombre === 'Santiago') || master[0];
    if (first) updateDetail(Number(first.comuna));
  } catch (err) {
    console.error(err);
    document.getElementById('data-status').textContent = `Error cargando datos: ${err.message}`;
  }
}

init();
