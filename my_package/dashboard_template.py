"""HTML template for the standalone indicator dashboard."""

# pylint: disable=line-too-long

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<title>__PAGE_TITLE__ — дашборд</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" crossorigin="">
<style>
:root {
  --ink: #1d1d1f;
  --muted: #6e6e73;
  --line: rgba(0, 0, 0, .08);
  --accent: #0071e3;
  --panel: rgba(255, 255, 255, .86);
  --surface: #f5f5f7;
  --radius: 24px;
}
* { box-sizing: border-box; }
html, body { height: 100%; margin: 0; }
body {
  background: #f5f5f7;
  color: var(--ink);
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}
#map { position: fixed; inset: 0; background: #e8e8ed; }
.leaflet-container { font-family: inherit; background: #e8e8ed; }
body.no-basemap #map,
body.no-basemap .leaflet-container { background: #dff1fb; }

.panel {
  position: fixed;
  z-index: 1000;
  top: 20px;
  left: 20px;
  width: 372px;
  max-height: calc(100vh - 40px);
  overflow-y: auto;
  overscroll-behavior: contain;
  padding: 26px 24px 20px;
  border-radius: 28px;
  border: 1px solid rgba(255, 255, 255, .7);
  background: var(--panel);
  box-shadow: 0 24px 70px rgba(0, 0, 0, .16), 0 2px 8px rgba(0, 0, 0, .05);
  -webkit-backdrop-filter: saturate(180%) blur(30px);
  backdrop-filter: saturate(180%) blur(30px);
  scrollbar-width: none;
}
.panel::-webkit-scrollbar { width: 0; height: 0; }
.eyebrow {
  font-size: 10.5px;
  line-height: 1.2;
  letter-spacing: .14em;
  text-transform: uppercase;
  color: var(--muted);
  font-weight: 700;
}
h1 {
  margin: 10px 0 8px;
  font-size: 29px;
  line-height: 1.04;
  letter-spacing: -.045em;
  font-weight: 700;
}
.sub {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
  line-height: 1.45;
}
.field { margin-top: 22px; }
.field > label,
.section-title,
.legend-title {
  display: block;
  margin: 0;
  color: var(--muted);
  font-size: 10.5px;
  line-height: 1.2;
  letter-spacing: .08em;
  text-transform: uppercase;
  font-weight: 700;
}
.select-wrap { position: relative; margin-top: 8px; }
.select {
  appearance: none;
  -webkit-appearance: none;
  width: 100%;
  border: 0;
  border-radius: 14px;
  background: var(--surface);
  color: var(--ink);
  padding: 13px 40px 13px 14px;
  font: inherit;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: -.01em;
  cursor: pointer;
  outline: none;
  transition: box-shadow .18s ease, background .18s ease;
}
.select:hover { background: #efeff3; }
.select:focus { box-shadow: 0 0 0 3px rgba(0, 113, 227, .2); }
.select-wrap .chevron,
.mini-wrap .chevron {
  position: absolute;
  top: 50%;
  right: 14px;
  transform: translateY(-50%);
  pointer-events: none;
  opacity: .42;
}
.desc {
  min-height: 17px;
  margin: 8px 2px 0;
  color: var(--muted);
  font-size: 11.5px;
  line-height: 1.45;
}

.stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-top: 18px;
}
.stat {
  min-width: 0;
  padding: 12px 13px;
  border-radius: 16px;
  background: var(--surface);
}
.stat-label {
  display: block;
  margin-bottom: 5px;
  overflow: hidden;
  color: var(--muted);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: .015em;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.stat-value {
  display: block;
  overflow: hidden;
  font-size: 19px;
  line-height: 1.08;
  letter-spacing: -.04em;
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.stat-value.small { font-size: 13px; letter-spacing: -.01em; }

.legend { margin-top: 20px; }
.legend-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}
.legend-unit { color: var(--muted); font-size: 10.5px; font-weight: 500; }
.legend-bar {
  height: 10px;
  margin: 12px 0 8px;
  border-radius: 6px;
  box-shadow: inset 0 0 0 1px rgba(0, 0, 0, .06);
}
.legend-labels {
  display: flex;
  justify-content: space-between;
  gap: 4px;
  color: var(--muted);
  font-size: 9.5px;
  line-height: 1.3;
  font-variant-numeric: tabular-nums;
}
.legend-labels span {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-align: center;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.legend-labels span:first-child { text-align: left; }
.legend-labels span:last-child { text-align: right; }
.legend-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}
.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  max-width: 100%;
  padding: 6px 9px;
  border-radius: 999px;
  background: var(--surface);
  font-size: 10.5px;
  font-weight: 600;
}
.chip .count { color: var(--muted); font-weight: 500; }
.dot {
  width: 8px;
  height: 8px;
  flex: none;
  border-radius: 50%;
}

.services {
  margin-top: 20px;
  padding-top: 18px;
  border-top: 1px solid var(--line);
}
.section-sub {
  margin: 5px 0 0;
  color: var(--muted);
  font-size: 10.5px;
  line-height: 1.4;
}
.service-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}
.service-toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 11px;
  border: 0;
  border-radius: 999px;
  background: var(--surface);
  color: var(--ink);
  font: inherit;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: background .18s ease, color .18s ease, transform .18s ease;
}
.service-toggle:hover { transform: translateY(-1px); }
.service-toggle[aria-pressed="true"] { background: var(--ink); color: #fff; }
.service-toggle[aria-pressed="true"] .dot { box-shadow: 0 0 0 2px rgba(255, 255, 255, .35); }

.foot {
  padding-top: 18px;
  color: var(--muted);
  font-size: 10px;
  line-height: 1.55;
}
.foot span { color: var(--ink); font-weight: 600; }

.map-actions {
  position: fixed;
  z-index: 1000;
  top: 20px;
  right: 20px;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
}
.control {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 13px;
  border: 1px solid rgba(255, 255, 255, .7);
  border-radius: 16px;
  background: var(--panel);
  box-shadow: 0 12px 34px rgba(0, 0, 0, .12);
  -webkit-backdrop-filter: saturate(180%) blur(24px);
  backdrop-filter: saturate(180%) blur(24px);
  color: var(--ink);
  font: inherit;
  font-size: 12px;
}
.control-label { color: var(--muted); font-size: 10.5px; font-weight: 600; letter-spacing: .02em; }
.mini-wrap { position: relative; display: flex; align-items: center; }
.mini-select {
  appearance: none;
  -webkit-appearance: none;
  max-width: 150px;
  padding: 0 20px 0 0;
  border: 0;
  background: transparent;
  color: var(--ink);
  font: inherit;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  outline: none;
}
.mini-wrap .chevron { right: 0; }
.reset-btn { border: 0; cursor: pointer; font-size: 12px; font-weight: 600; }
.segmented { gap: 0; padding: 4px; border-radius: 14px; }
.segmented button {
  border: 0;
  border-radius: 10px;
  padding: 6px 10px;
  background: transparent;
  color: var(--muted);
  font: inherit;
  font-size: 11.5px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}
.segmented button[aria-pressed="true"] { background: var(--ink); color: #fff; }
.map-actions .control[hidden] { display: none; }

.leaflet-control-zoom {
  overflow: hidden;
  border: 0 !important;
  border-radius: 12px !important;
  box-shadow: 0 10px 28px rgba(0, 0, 0, .16) !important;
}
.leaflet-control-zoom a {
  width: 34px !important;
  height: 34px !important;
  border: 0 !important;
  background: rgba(255, 255, 255, .92) !important;
  color: var(--ink) !important;
  font-size: 18px !important;
  line-height: 34px !important;
}
.leaflet-control-zoom a:hover { background: #fff !important; }
.leaflet-control-attribution {
  padding: 2px 6px !important;
  border-radius: 8px !important;
  background: rgba(255, 255, 255, .72) !important;
  color: var(--muted) !important;
  font-size: 9px !important;
  -webkit-backdrop-filter: blur(10px);
  backdrop-filter: blur(10px);
}
.leaflet-control-attribution a { color: var(--muted) !important; }

.leaflet-tooltip.city-tip {
  width: max-content;
  min-width: min(260px, calc(100vw - 28px));
  max-width: min(380px, calc(100vw - 28px));
  padding: 12px 14px;
  border: 0;
  border-radius: 14px;
  background: rgba(255, 255, 255, .97);
  box-shadow: 0 14px 36px rgba(0, 0, 0, .18);
  color: var(--ink);
  font-size: 11.5px;
  line-height: 1.4;
  white-space: normal;
}
.leaflet-tooltip.city-tip::before { display: none; }
.tip-kicker {
  margin-bottom: 2px;
  color: var(--muted);
  font-size: 9.5px;
  font-weight: 700;
  letter-spacing: .09em;
  text-transform: uppercase;
}
.tip-value {
  margin: 2px 0 6px;
  font-size: 21px;
  line-height: 1.08;
  letter-spacing: -.04em;
  font-weight: 700;
}
.tip-value.small { font-size: 15px; letter-spacing: -.02em; }
.tip-unit { color: var(--muted); font-size: 11px; font-weight: 600; letter-spacing: 0; }
.tip-row {
  display: flex;
  justify-content: space-between;
  gap: 22px;
  color: var(--muted);
  white-space: nowrap;
}
.tip-row b { color: var(--ink); font-weight: 600; text-align: right; }

.stats-modal {
  position: fixed;
  z-index: 3000;
  inset: 0;
  display: grid;
  place-items: center;
  padding: 24px;
  background: rgba(20, 20, 22, .32);
  -webkit-backdrop-filter: blur(12px);
  backdrop-filter: blur(12px);
}
.stats-modal[hidden] { display: none; }
.stats-dialog {
  width: min(1080px, 100%);
  max-height: min(860px, calc(100vh - 48px));
  overflow: auto;
  border: 1px solid rgba(255, 255, 255, .78);
  border-radius: 30px;
  background: rgba(255, 255, 255, .97);
  box-shadow: 0 36px 110px rgba(0, 0, 0, .3);
  padding: 26px;
  scrollbar-width: thin;
}
.stats-head { display: flex; justify-content: space-between; gap: 24px; align-items: flex-start; }
.stats-head h2 { margin: 5px 0 5px; font-size: 30px; letter-spacing: -.045em; }
.stats-close {
  border: 0;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: var(--surface);
  color: var(--ink);
  font-size: 22px;
  line-height: 1;
  cursor: pointer;
}
.stats-toolbar { display: flex; flex-wrap: wrap; gap: 8px; margin: 20px 0 12px; }
.stats-toolbar button,
.filter-remove {
  border: 0;
  border-radius: 999px;
  background: var(--surface);
  color: var(--ink);
  padding: 8px 13px;
  font: inherit;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}
.stats-toolbar button:hover,
.filter-remove:hover { background: #e9e9ee; }
.stats-toolbar .primary { background: var(--ink); color: #fff; }
.filter-rows { display: grid; gap: 8px; margin-bottom: 18px; }
.filter-row {
  display: grid;
  grid-template-columns: minmax(170px, 1.4fr) minmax(110px, .7fr) minmax(150px, 1fr) auto;
  gap: 8px;
  align-items: center;
}
.filter-row select,
.filter-row input {
  width: 100%;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: #fff;
  color: var(--ink);
  padding: 9px 10px;
  font: inherit;
  font-size: 12.5px;
  outline: none;
}
.filter-row input[type="number"] { min-width: 0; }
.filter-range { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  margin: 14px 0 22px;
}
.stats-card {
  padding: 14px;
  border-radius: 18px;
  background: var(--surface);
}
.stats-card span { display: block; color: var(--muted); font-size: 10.5px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; }
.stats-card b { display: block; margin-top: 6px; font-size: 25px; letter-spacing: -.04em; }
.stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 22px; margin-top: 22px; }
.stats-grid h3, .insights h3 { margin: 0 0 10px; font-size: 14px; letter-spacing: -.01em; }
.stats-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.stats-table th { color: var(--muted); text-align: right; font-size: 9.5px; letter-spacing: .06em; text-transform: uppercase; padding: 0 0 7px; }
.stats-table th:first-child, .stats-table td:first-child { text-align: left; }
.stats-table td { border-top: 1px solid var(--line); padding: 8px 0; text-align: right; }
.stats-table td:first-child { padding-right: 10px; }
.stats-table .warn { color: #c93400; font-size: 10px; font-weight: 700; }
.bar-row { display: grid; grid-template-columns: 108px 1fr 46px; gap: 8px; align-items: center; margin: 7px 0; font-size: 11.5px; }
.bar-row span:first-child { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--muted); }
.bar-track { height: 8px; border-radius: 999px; background: #ededf0; overflow: hidden; }
.bar-fill { height: 100%; border-radius: inherit; background: var(--accent); }
.bar-row b { text-align: right; font-size: 11.5px; }
.insights { margin-top: 26px; padding-top: 20px; border-top: 1px solid var(--line); }
.insights ul { margin: 0; padding-left: 18px; }
.insights li { margin: 7px 0; font-size: 12.5px; line-height: 1.45; }
.insights .disclaimer { margin: 14px 0 0; color: var(--muted); font-size: 10.5px; line-height: 1.5; }
.stats-empty { padding: 22px; border-radius: 16px; background: var(--surface); color: var(--muted); font-size: 12.5px; }

@media (max-width: 820px) {
  .stats-modal { padding: 10px; }
  .stats-dialog { max-height: calc(100vh - 20px); padding: 20px 16px; border-radius: 24px; }
  .stats-grid { grid-template-columns: 1fr; }
  .stats-cards { grid-template-columns: 1fr 1fr; }
  .filter-row { grid-template-columns: 1fr 1fr; }
  .filter-row .filter-remove { grid-column: 1 / -1; }
}

@media (max-width: 820px) {
  .panel {
    top: auto;
    left: 12px;
    right: 12px;
    bottom: 12px;
    width: auto;
    max-height: 56vh;
    padding: 20px 18px 16px;
    border-radius: 24px;
  }
  h1 { font-size: 24px; }
  .sub { font-size: 12px; }
  .map-actions { top: 12px; right: 12px; }
  .control { padding: 8px 11px; }
  .mini-select { max-width: 118px; }
}
</style>
</head>
<body>
<div id="map" aria-label="Карта показателей"></div>

<aside class="panel" aria-label="Панель показателей">
  <div class="eyebrow">Urban analytics · IDU</div>
  <h1>__TITLE__</h1>
  <p class="sub">__SUBTITLE__. Выберите показатель — карта, шкала и метрики обновятся.</p>

  <div class="field">
    <label for="indicatorSelect">Показатель</label>
    <div class="select-wrap">
      <select id="indicatorSelect" class="select"></select>
      <svg class="chevron" width="12" height="8" viewBox="0 0 12 8" aria-hidden="true"><path d="M1 1.5 6 6.5l5-5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
    </div>
    <p class="desc" id="indicatorDesc"></p>
  </div>

  <div class="stats" id="stats"></div>

  <div class="legend">
    <div class="legend-head">
      <span class="legend-title" id="legendTitle">Шкала показателя</span>
      <span class="legend-unit" id="legendUnit"></span>
    </div>
    <div class="legend-bar" id="legendBar"></div>
    <div class="legend-labels" id="legendLabels"></div>
    <div class="legend-chips" id="legendChips"></div>
  </div>

  <div class="services" id="servicesBlock" hidden>
    <div class="section-title">Сервисы на карте</div>
    <p class="section-sub">Точки OpenStreetMap. Для показателей обеспеченности нужный слой включается автоматически.</p>
    <div class="service-list" id="serviceList"></div>
  </div>

  <div class="foot">
    <span id="dataNote"></span><br>
    Данные: OpenStreetMap · BlocksNet. Подложки — без API-ключей.
  </div>
</aside>

<div class="map-actions">
  <div class="control">
    <label class="control-label" for="basemapSelect">Подложка</label>
    <div class="mini-wrap">
      <select id="basemapSelect" class="mini-select"></select>
      <svg class="chevron" width="10" height="7" viewBox="0 0 12 8" aria-hidden="true"><path d="M1 1.5 6 6.5l5-5" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>
    </div>
  </div>
  <div class="control segmented" id="blocksToggle" role="group" aria-label="Отображение кварталов">
    <button type="button" data-blocks-mode="clean" aria-pressed="true">Только кварталы</button>
    <button type="button" data-blocks-mode="blank" aria-pressed="false">Без кварталов</button>
  </div>
  <button type="button" class="control reset-btn" id="destinationMode">Доступность до квартала</button>
  <div class="control segmented" id="accessModeToggle" role="group" aria-label="Способ передвижения" hidden>
    <button type="button" data-access-mode="pedestrian" aria-pressed="true">Пешком</button>
    <button type="button" data-access-mode="drive" aria-pressed="false">Авто</button>
  </div>
  <button type="button" class="control reset-btn" id="resetView">Сбросить вид</button>
  <button type="button" class="control reset-btn" id="statsButton">Статистика</button>
</div>

<div class="stats-modal" id="statsModal" hidden>
  <div class="stats-dialog" role="dialog" aria-modal="true" aria-labelledby="statsTitle">
    <div class="stats-head">
      <div>
        <div class="eyebrow">Аналитика по кварталам</div>
        <h2 id="statsTitle">Статистика территории</h2>
        <p class="sub" id="statsSub">Фильтры пересчитывают показатели по выбранным кварталам.</p>
      </div>
      <button type="button" class="stats-close" id="statsClose" aria-label="Закрыть статистику">×</button>
    </div>
    <div class="stats-toolbar">
      <button type="button" data-preset="all">Все кварталы</button>
      <button type="button" data-preset="built">С застройкой</button>
      <button type="button" data-preset="populated">С населением</button>
      <button type="button" data-preset="green">Зелень ≥ 50%</button>
      <button type="button" class="primary" id="addFilter">+ Фильтр</button>
      <button type="button" id="resetFilters">Сбросить фильтры</button>
    </div>
    <div class="filter-rows" id="filterRows"></div>
    <div class="stats-cards" id="statsCards"></div>
    <div class="stats-grid">
      <section>
        <h3>Ключевые показатели</h3>
        <div id="statsTable"></div>
      </section>
      <section>
        <h3>Землепользование</h3>
        <div id="statsLanduse"></div>
      </section>
    </div>
    <div class="stats-grid">
      <section>
        <h3>Распределение доли зелени</h3>
        <div id="statsGreenBins"></div>
      </section>
      <section>
        <h3>Обеспеченность в кварталах с населением</h3>
        <div id="statsProvision"></div>
      </section>
    </div>
    <section class="insights">
      <h3>Автоматические выводы</h3>
      <ul id="statsInsights"></ul>
      <p class="disclaimer" id="statsDisclaimer"></p>
    </section>
  </div>
</div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" crossorigin=""></script>
<script>
const DATA = __PAYLOAD__;
const MISSING_COLOR = "#E5E5EA";
const numberFormat = new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 0 });

const map = L.map("map", {
  zoomControl: false,
  attributionControl: true,
  minZoom: 9,
  maxZoom: 19,
  zoomSnap: 0.25,
  wheelPxPerZoomLevel: 110
});
L.control.zoom({ position: "bottomright" }).addTo(map);
map.attributionControl.setPrefix(false);

map.createPane("landPane").style.zIndex = 340;
map.createPane("blockPane").style.zIndex = 350;
map.createPane("waterPane").style.zIndex = 360;
map.createPane("servicePane").style.zIndex = 370;

const landUseIndicator = DATA.indicators.find(item => item.id === "land_use");
const LAND_USE_SHARE_FIELDS = [
  ["residential", "LandUse.RESIDENTIAL"],
  ["business", "LandUse.BUSINESS"],
  ["recreation", "LandUse.RECREATION"],
  ["industrial", "LandUse.INDUSTRIAL"],
  ["agriculture", "LandUse.AGRICULTURE"],
  ["special", "LandUse.SPECIAL"],
  ["transport", "LandUse.TRANSPORT"]
];
const MODE_INDICATORS = [
  {
    id: "__blank__",
    kind: "blank",
    label: "Без кварталов",
    group: "Режимы карты",
    description: "Чистая карта: подложка без кварталов и сервисных слоёв. ПКМ возвращает режим «Только кварталы».",
    unit: "",
    decimals: 0,
    format: "number",
    stats: {
      cards: [
        { label: "Кварталов скрыто", value: DATA.meta.blockCount, format: "count", decimals: 0 },
        { label: "Население", value: DATA.meta.population, format: "count", decimals: 0 }
      ]
    },
    count: DATA.meta.blockCount,
    missing: 0
  },
  {
    id: "__clean__",
    kind: "empty",
    label: "Только кварталы",
    group: "Режимы карты",
    description: "Кварталы без тематической окраски и сервисных слоёв. ПКМ возвращает этот режим.",
    unit: "",
    decimals: 0,
    format: "number",
    stats: {
      cards: [
        { label: "Кварталов", value: DATA.meta.blockCount, format: "count", decimals: 0 },
        { label: "Население", value: DATA.meta.population, format: "count", decimals: 0 }
      ]
    },
    count: DATA.meta.blockCount,
    missing: 0
  },
  {
    id: "__destination__",
    kind: "destination",
    label: "Доступность до квартала",
    group: "Режимы карты",
    description: "Выберите квартал на карте: покажем время в пути до него из всех кварталов. Способ передвижения переключается кнопками «Пешком» и «Авто». ПКМ — сброс.",
    unit: "мин",
    decimals: 0,
    format: "number",
    palette: ["#30D158", "#8BE8A0", "#D4F7A0", "#FFD60A", "#FFB340", "#FF9F0A", "#FF453A", "#B5173B"],
    breaks: [0, 5, 10, 15, 20, 30, 45, 60, 90],
    stats: { cards: [] },
    count: 0,
    missing: 0
  }
];
const ALL_INDICATORS = DATA.indicators.concat(MODE_INDICATORS);
const MODE_BY_ID = {};
MODE_INDICATORS.forEach(item => { MODE_BY_ID[item.id] = item; });
const requestedIndicator = decodeURIComponent((window.location.hash || "").replace(/^#/, ""));
let accessMode = requestedIndicator === "__drive__" ? "drive" : "pedestrian";
const requestedModeId = requestedIndicator === "__drive__" ? "__destination__" : requestedIndicator;
let activeIndicator = ALL_INDICATORS.find(item => item.id === requestedModeId)
  || DATA.indicators.find(item => item.id === "population")
  || DATA.indicators[0];
let mapMode = activeIndicator.kind === "empty" ? "clean"
  : activeIndicator.kind === "blank" ? "blank"
  : activeIndicator.kind === "destination" ? "destination" : "indicator";
if (mapMode === "destination") {
  activeIndicator = Object.assign({}, MODE_BY_ID["__destination__"], {
    label: "Доступность до квартала · " + (accessMode === "drive" ? "Авто" : "Пешком")
  });
}
let destinationBlockId = null;
let destinationValues = {};
let activeTile = null;
let basemapDisabled = false;
const serviceState = {};

const serviceLayers = {};
DATA.services.forEach(service => {
  serviceState[service.id] = false;
  serviceLayers[service.id] = L.layerGroup();
});

function esc(value) {
  return String(value === null || value === undefined ? "" : value).replace(/[&<>"']/g, character => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  }[character]));
}

function formatInt(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return numberFormat.format(Number(value));
}

function formatNumber(value, spec, compact) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  const number = Number(value);
  const decimals = spec && spec.decimals !== undefined ? spec.decimals : 0;
  if (spec && spec.format === "percent") {
    return (number * 100).toLocaleString("ru-RU", { maximumFractionDigits: decimals }) + "%";
  }
  if (compact && Math.abs(number) >= 10000) {
    return number.toLocaleString("ru-RU", { notation: "compact", maximumFractionDigits: 1 });
  }
  return number.toLocaleString("ru-RU", { minimumFractionDigits: 0, maximumFractionDigits: decimals });
}

function formatStat(card) {
  if (card.value === null || card.value === undefined) return "—";
  if (card.format === "text") return String(card.value);
  if (card.format === "count") return formatInt(card.value);
  return formatNumber(card.value, card, false);
}

function numericColor(value, indicator) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return missingFill();
  const number = Number(value);
  const breaks = indicator.breaks;
  for (let index = 0; index < indicator.palette.length; index += 1) {
    if (number <= breaks[index + 1]) return indicator.palette[index];
  }
  return indicator.palette[indicator.palette.length - 1];
}

function categoryFor(value, indicator) {
  if (value === null || value === undefined) return null;
  const key = String(value);
  return indicator.categories.find(category => category.value === key) || null;
}

function missingFill() {
  return basemapDisabled ? "#EFEEE9" : MISSING_COLOR;
}

function blockStyle(feature) {
  const indicator = activeIndicator;
  if (indicator.kind === "blank") {
    return {
      fillColor: "#F5F5F7",
      fillOpacity: 0,
      color: "rgba(29,29,31,0)",
      weight: 0,
      opacity: 0
    };
  }
  if (indicator.kind === "empty") {
    return {
      fillColor: basemapDisabled ? "#EFEEE9" : "#F5F5F7",
      fillOpacity: basemapDisabled ? 1 : 0.72,
      color: "rgba(29,29,31,.38)",
      weight: 0.8,
      opacity: 1
    };
  }
  if (indicator.kind === "destination") {
    const blockId = feature.properties.block_id;
    const fill = numericColor(destinationValues[blockId], indicator);
    const isTarget = destinationBlockId === blockId;
    return {
      fillColor: fill,
      fillOpacity: 1,
      color: isTarget ? "#1d1d1f" : "rgba(255,255,255,.92)",
      weight: isTarget ? 2.8 : 0.7,
      opacity: 1
    };
  }
  let fill = missingFill();
  if (indicator.kind === "numeric") {
    fill = numericColor(feature.properties[indicator.id], indicator);
  } else {
    const category = categoryFor(feature.properties[indicator.id], indicator);
    fill = category ? category.color : missingFill();
  }
  return {
    fillColor: fill,
    fillOpacity: 1,
    color: "rgba(255,255,255,.92)",
    weight: 0.7,
    opacity: 1
  };
}

function landUseLabel(value) {
  if (!landUseIndicator) return "—";
  const category = categoryFor(value, landUseIndicator);
  return category ? category.label : "—";
}

function row(label, value) {
  return '<div class="tip-row"><span>' + esc(label) + "</span><b>" + esc(value) + "</b></div>";
}

function landUseShareRows(properties) {
  return LAND_USE_SHARE_FIELDS
    .map(([field, landUse]) => ({ label: landUseLabel(landUse), value: Number(properties[field]) }))
    .filter(item => Number.isFinite(item.value) && item.value > 0.0005)
    .sort((left, right) => right.value - left.value)
    .map(item => row(
      "Доля: " + item.label,
      formatNumber(item.value, { format: "percent", decimals: 0 }, false)
    ));
}

function formatMetric(value, spec, unit) {
  const formatted = formatNumber(value, spec, false);
  return formatted === "—" ? formatted : formatted + " " + unit;
}

function formatUsers(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  const number = Number(value);
  const digits = Math.abs(number) < 10 ? 1 : 0;
  return number.toLocaleString("ru-RU", { maximumFractionDigits: digits }) + " чел.";
}

function serviceIdForIndicator(indicatorId) {
  const prefix = "provision_strong_";
  if (!indicatorId || indicatorId.indexOf(prefix) !== 0) return null;
  return indicatorId.slice(prefix.length);
}

function serviceMetricRows(properties, serviceId) {
  const rows = [];
  rows.push(row(
    "Время в пути до сервиса",
    formatMetric(properties["access_time_" + serviceId], { decimals: 1 }, "мин")
  ));
  rows.push(row(
    "Потенциальные пользователи",
    formatMetric(properties["service_demand_" + serviceId], { decimals: 0 }, "чел.")
  ));
  rows.push(row("Пользуются сервисом", formatUsers(properties["service_served_" + serviceId])));
  const capacity = Number(properties["service_capacity_" + serviceId]);
  if (Number.isFinite(capacity) && capacity > 0) {
    rows.push(row("Ёмкость сервиса в квартале", formatMetric(capacity, { decimals: 0 }, "мест")));
  }
  return rows;
}

function blockTip(properties) {
  const indicator = activeIndicator;
  const rows = [];
  let valueHtml = "";
  if (indicator.kind === "empty") {
    valueHtml = '<div class="tip-value small">' + esc(properties.block_id) + "</div>";
    rows.push(row("Землепользование", landUseLabel(properties.land_use)));
    rows.push(...landUseShareRows(properties));
    rows.push(row("Население", formatNumber(properties.population, { format: "number", decimals: 0 }, false) + " чел."));
    return '<div class="tip-kicker">Только кварталы</div>' + valueHtml + rows.join("");
  }
  if (indicator.kind === "destination") {
    const unit = indicator.unit ? ' <span class="tip-unit">' + esc(indicator.unit) + "</span>" : "";
    valueHtml = '<div class="tip-value">' + formatNumber(destinationValues[properties.block_id], indicator, false) + unit + "</div>";
    rows.push(row("Доступность до", destinationBlockId || "выберите квартал"));
  } else if (indicator.kind === "numeric") {
    const unit = indicator.unit ? ' <span class="tip-unit">' + esc(indicator.unit) + "</span>" : "";
    valueHtml = '<div class="tip-value">' + formatNumber(properties[indicator.id], indicator, false) + unit + "</div>";
  } else {
    const category = categoryFor(properties[indicator.id], indicator);
    valueHtml = '<div class="tip-value small">' + esc(category ? category.label : "Нет данных") + "</div>";
  }
  rows.push(row("Землепользование", landUseLabel(properties.land_use)));
  rows.push(...landUseShareRows(properties));
  const serviceId = serviceIdForIndicator(indicator.id);
  if (serviceId) rows.push(...serviceMetricRows(properties, serviceId));
  if (indicator.id !== "population") {
    rows.push(row("Население", formatNumber(properties.population, { format: "number", decimals: 0 }, false) + " чел."));
  }
  if (indicator.id !== "fsi") {
    rows.push(row("Плотность (FSI)", formatNumber(properties.fsi, { format: "number", decimals: 2 }, false)));
  }
  if (indicator.id !== "area_accessibility") {
    rows.push(row("Пешеходная доступность", formatNumber(properties.area_accessibility, { format: "number", decimals: 0 }, false) + " мин"));
  }
  const snapWalk = Number(properties.graph_snap_walk_m);
  if (Number.isFinite(snapWalk) && snapWalk > 500) {
    rows.push(row("Привязка к пешеходной сети", formatMetric(snapWalk, { decimals: 0 }, "м")));
  }
  return '<div class="tip-kicker">' + esc(indicator.label) + "</div>" + valueHtml + rows.join("");
}

const blocksLayer = L.geoJSON(DATA.layers.blocks, {
  pane: "blockPane",
  style: blockStyle,
  onEachFeature: (feature, layer) => {
    layer.bindTooltip(() => blockTip(feature.properties), {
      sticky: true,
      direction: "top",
      className: "city-tip",
      opacity: 1
    });
    layer.on({
      click: () => {
        if (mapMode === "destination") setDestination(feature.properties.block_id);
      },
      mouseover: event => {
        event.target.setStyle({ weight: 1.8, color: "#1d1d1f" });
        event.target.bringToFront();
      },
      mouseout: event => {
        blocksLayer.resetStyle(event.target);
      }
    });
  }
}).addTo(map);

function setBlocksVisible(visible) {
  if (visible && !map.hasLayer(blocksLayer)) blocksLayer.addTo(map);
  if (!visible && map.hasLayer(blocksLayer)) map.removeLayer(blocksLayer);
}

const landLayer = L.geoJSON(DATA.layers.land, {
  pane: "landPane",
  interactive: false,
  style: {
    color: "#D2D2D7",
    weight: 1,
    opacity: 1,
    fillColor: "#EFEEE9",
    fillOpacity: 1
  }
});

const waterLayer = L.geoJSON(DATA.layers.water, {
  pane: "waterPane",
  interactive: false,
  style: {
    color: "#FFFFFF",
    weight: 0.8,
    opacity: 1,
    fillColor: "#0A84FF",
    fillOpacity: 1
  }
});

DATA.services.forEach(service => {
  const layerGroup = L.geoJSON(service.geojson, {
    pointToLayer: (feature, latlng) => L.circleMarker(latlng, {
      pane: "servicePane",
      radius: 6.5,
      color: "#ffffff",
      weight: 2,
      opacity: 1,
      fillColor: service.color,
      fillOpacity: 1
    }),
    style: feature => {
      const geometryType = feature.geometry ? feature.geometry.type : "";
      if (geometryType === "Point" || geometryType === "MultiPoint") return {};
      return {
        pane: "servicePane",
        color: service.color,
        weight: 1.6,
        opacity: .95,
        fillColor: service.color,
        fillOpacity: .28
      };
    },
    onEachFeature: (feature, layer) => {
      const properties = feature.properties || {};
      const name = properties.name || properties["name:ru"] || properties.brand || service.label;
      const kind = properties.amenity || properties.shop || properties.leisure || "";
      const rows = kind ? row("тип", kind) : "";
      const capacity = Number(properties.capacity);
      const capacityRow = Number.isFinite(capacity) && capacity > 0
        ? row("Ёмкость", formatMetric(capacity, { decimals: 0 }, "мест"))
        : "";
      const isPoint = feature.geometry && (feature.geometry.type === "Point" || feature.geometry.type === "MultiPoint");
      layer.bindTooltip(
        '<div class="tip-kicker">' + esc(service.label) + '</div><div class="tip-value small">' + esc(name) + "</div>" + rows + capacityRow,
        { sticky: true, direction: "top", className: "city-tip", opacity: 1 }
      );
      layer.on("mouseover", () => layer.setStyle(isPoint ? { radius: 8, weight: 2.5 } : { weight: 3, fillOpacity: .45 }));
      layer.on("mouseout", () => layer.setStyle(isPoint ? { radius: 6.5, weight: 2 } : { weight: 1.6, fillOpacity: .28 }));
    }
  });
  layerGroup.eachLayer(layer => serviceLayers[service.id].addLayer(layer));
});

const tileLayers = {};
DATA.basemaps.forEach(basemap => {
  if (!basemap.tiles || !basemap.tiles.length) return;
  const group = L.layerGroup();
  basemap.tiles.forEach(tile => {
    L.tileLayer(tile.url, {
      attribution: tile.attribution || "",
      subdomains: tile.subdomains || "abc",
      maxNativeZoom: tile.maxNativeZoom || 19,
      maxZoom: 20
    }).addTo(group);
  });
  tileLayers[basemap.id] = group;
});

function setBasemap(id) {
  if (activeTile) {
    map.removeLayer(activeTile);
    activeTile = null;
  }
  if (id !== "none" && tileLayers[id]) {
    activeTile = tileLayers[id];
    activeTile.addTo(map);
  }
  const noBasemap = id === "none";
  if (noBasemap) {
    if (!map.hasLayer(landLayer)) landLayer.addTo(map);
    if (!map.hasLayer(waterLayer)) waterLayer.addTo(map);
  } else {
    if (map.hasLayer(landLayer)) map.removeLayer(landLayer);
    if (map.hasLayer(waterLayer)) map.removeLayer(waterLayer);
  }
  basemapDisabled = noBasemap;
  blocksLayer.setStyle(blockStyle);
  document.body.classList.toggle("no-basemap", noBasemap);
  document.getElementById("basemapSelect").value = id;
}

function updateStats(indicator) {
  const container = document.getElementById("stats");
  container.innerHTML = indicator.stats.cards.map(card => {
    const value = formatStat(card);
    const small = String(value).length > 13 ? " small" : "";
    return '<div class="stat"><span class="stat-label">' + esc(card.label) +
      '</span><span class="stat-value' + small + '">' + esc(value) + "</span></div>";
  }).join("");
}

function updateLegend(indicator) {
  const title = document.getElementById("legendTitle");
  const unit = document.getElementById("legendUnit");
  const bar = document.getElementById("legendBar");
  const labels = document.getElementById("legendLabels");
  const chips = document.getElementById("legendChips");

  if (indicator.kind === "numeric" || indicator.kind === "destination") {
    title.textContent = indicator.kind === "destination" ? indicator.label : "Шкала показателя";
    unit.textContent = indicator.unit || "";
    bar.style.display = "block";
    labels.style.display = "flex";
    chips.style.display = "none";
    const step = 100 / indicator.palette.length;
    bar.style.background = "linear-gradient(90deg, " + indicator.palette.map((color, index) =>
      color + " " + (index * step).toFixed(2) + "% " + ((index + 1) * step).toFixed(2) + "%"
    ).join(", ") + ")";
    labels.innerHTML = indicator.breaks.map(value =>
      "<span>" + esc(formatNumber(value, indicator, true)) + "</span>"
    ).join("");
  } else if (indicator.kind === "empty" || indicator.kind === "blank") {
    title.textContent = indicator.kind === "blank" ? "Без кварталов" : "Только кварталы";
    unit.textContent = "";
    bar.style.display = "none";
    labels.style.display = "none";
    chips.style.display = "none";
    chips.innerHTML = "";
  } else {
    title.textContent = "Категории";
    unit.textContent = "";
    bar.style.display = "none";
    labels.style.display = "none";
    chips.style.display = "flex";
    chips.innerHTML = indicator.categories.map(category =>
      '<span class="chip"><span class="dot" style="background:' + esc(category.color) + '"></span>' +
      esc(category.label) + '<span class="count">' + formatInt(category.count) + "</span></span>"
    ).join("");
  }
}

function refreshServiceButtons() {
  document.querySelectorAll(".service-toggle").forEach(button => {
    const id = button.dataset.service;
    const enabled = Boolean(serviceState[id]);
    button.setAttribute("aria-pressed", String(enabled));
    const layer = serviceLayers[id];
    if (!layer) return;
    if (enabled && !map.hasLayer(layer)) layer.addTo(map);
    if (!enabled && map.hasLayer(layer)) map.removeLayer(layer);
  });
}

function syncServicesWithIndicator() {
  Object.keys(serviceState).forEach(id => { serviceState[id] = false; });
  if (activeIndicator.id.indexOf("provision_strong_") === 0) {
    const serviceId = activeIndicator.id.replace("provision_strong_", "");
    if (serviceId in serviceState) serviceState[serviceId] = true;
  }
  refreshServiceButtons();
}

function updateViewToggles() {
  const blocksToggle = document.getElementById("blocksToggle");
  if (blocksToggle) {
    const blank = activeIndicator.kind === "blank";
    blocksToggle.querySelectorAll("[data-blocks-mode]").forEach(button => {
      button.setAttribute("aria-pressed", String(button.dataset.blocksMode === (blank ? "blank" : "clean")));
    });
  }
  const accessToggle = document.getElementById("accessModeToggle");
  if (accessToggle) {
    accessToggle.hidden = activeIndicator.kind !== "destination";
    accessToggle.querySelectorAll("[data-access-mode]").forEach(button => {
      button.setAttribute("aria-pressed", String(button.dataset.accessMode === accessMode));
    });
  }
}

function updatePanel() {
  document.getElementById("indicatorSelect").value = activeIndicator.id;
  document.getElementById("indicatorDesc").textContent = activeIndicator.description || "";
  updateStats(activeIndicator);
  updateLegend(activeIndicator);
  updateViewToggles();
  const note = document.getElementById("dataNote");
  if (activeIndicator.kind === "blank") {
    note.textContent = formatInt(DATA.meta.blockCount) + " кварталов · слой кварталов скрыт";
  } else if (activeIndicator.kind === "empty") {
    note.textContent = formatInt(DATA.meta.blockCount) + " кварталов · без тематических слоёв";
  } else if (activeIndicator.kind === "destination" && !destinationBlockId) {
    note.textContent = "Кликните квартал на карте · ПКМ — сброс";
  } else {
    const parts = [formatInt(activeIndicator.count) + " кварталов с данными"];
    if (activeIndicator.missing) parts.push(formatInt(activeIndicator.missing) + " без данных");
    note.textContent = parts.join(" · ");
  }
  syncServicesWithIndicator();
}

function updateHash(id) {
  if (window.history && window.history.replaceState) {
    window.history.replaceState(null, "", "#" + id);
  }
}

function clearDestination() {
  destinationBlockId = null;
  destinationValues = {};
}

function destinationSource() {
  const accessibility = DATA.accessibility || {};
  if (accessMode === "drive") {
    return accessibility.drive || { blockIds: [], minutes: [] };
  }
  return accessibility;
}

function destinationCards(values) {
  const numbers = Object.values(values)
    .filter(value => value !== null && value !== undefined && Number.isFinite(Number(value)))
    .map(value => Number(value));
  const summary = statsSummary(numbers);
  return [
    { label: "Медиана", value: summary.median, format: "number", decimals: 0 },
    { label: "Среднее", value: summary.mean, format: "number", decimals: 0 },
    { label: "Максимум", value: summary.max, format: "number", decimals: 0 },
    { label: "Кварталов", value: summary.n, format: "count", decimals: 0 }
  ];
}

function enterBlankMode() {
  mapMode = "blank";
  clearDestination();
  activeIndicator = MODE_BY_ID["__blank__"];
  setBlocksVisible(false);
  blocksLayer.setStyle(blockStyle);
  updatePanel();
  updateHash("__blank__");
}

function enterCleanMode() {
  mapMode = "clean";
  clearDestination();
  activeIndicator = MODE_BY_ID["__clean__"];
  setBlocksVisible(true);
  blocksLayer.setStyle(blockStyle);
  updatePanel();
  updateHash("__clean__");
}

function enterDestinationMode(mode) {
  if (mode) accessMode = mode === "drive" ? "drive" : "pedestrian";
  const destinationMode = MODE_BY_ID["__destination__"];
  const matrix = destinationSource();
  const hasMatrix = Boolean(matrix && Array.isArray(matrix.blockIds) && matrix.blockIds.length);
  const label = destinationMode.label + " · " + (accessMode === "drive" ? "Авто" : "Пешком");
  mapMode = "destination";
  clearDestination();
  activeIndicator = Object.assign({}, destinationMode, {
    label: label,
    description: hasMatrix
      ? destinationMode.description
      : "Матрица доступности не найдена. Пересоберите основной ноутбук.",
    stats: { cards: [] },
    count: 0,
    missing: 0
  });
  setBlocksVisible(true);
  blocksLayer.setStyle(blockStyle);
  updatePanel();
  updateHash(accessMode === "drive" ? "__drive__" : "__destination__");
}

function setAccessMode(mode) {
  accessMode = mode === "drive" ? "drive" : "pedestrian";
  if (mapMode !== "destination") {
    enterDestinationMode(accessMode);
    return;
  }
  const selected = destinationBlockId;
  enterDestinationMode(accessMode);
  if (selected) setDestination(selected);
}

function setDestination(blockId) {
  const matrix = destinationSource();
  const ids = matrix && Array.isArray(matrix.blockIds) ? matrix.blockIds : [];
  const targetIndex = ids.indexOf(blockId);
  if (targetIndex < 0) return;
  const values = {};
  ids.forEach((id, originIndex) => {
    const row = matrix.minutes[originIndex] || [];
    values[id] = row[targetIndex];
  });
  destinationBlockId = blockId;
  destinationValues = values;
  const isDrive = accessMode === "drive";
  const sourceMode = MODE_BY_ID["__destination__"];
  const valid = Object.values(values)
    .filter(value => value !== null && value !== undefined && Number.isFinite(Number(value))).length;
  activeIndicator = Object.assign({}, sourceMode, {
    label: sourceMode.label + " · " + (isDrive ? "Авто" : "Пешком") + " · " + blockId,
    description: (isDrive ? "Время в пути на автомобиле" : "Пешеходное время") +
      " от каждого квартала до " + blockId + ". ПКМ — сброс.",
    stats: { cards: destinationCards(values) },
    count: valid,
    missing: Math.max(0, ids.length - valid)
  });
  blocksLayer.setStyle(blockStyle);
  updatePanel();
}

function setIndicator(id) {
  if (id === "__blank__") {
    enterBlankMode();
    return;
  }
  if (id === "__clean__") {
    enterCleanMode();
    return;
  }
  if (id === "__destination__") {
    enterDestinationMode();
    return;
  }
  if (id === "__drive__") {
    enterDestinationMode("drive");
    return;
  }
  const indicator = DATA.indicators.find(item => item.id === id);
  if (!indicator) return;
  mapMode = "indicator";
  clearDestination();
  activeIndicator = indicator;
  setBlocksVisible(true);
  blocksLayer.setStyle(blockStyle);
  updatePanel();
}

function fitView() {
  const mobile = window.matchMedia("(max-width: 820px)").matches;
  const options = mobile
    ? { paddingTopLeft: [20, 20], paddingBottomRight: [20, Math.min(340, window.innerHeight * 0.48)] }
    : { paddingTopLeft: [430, 60], paddingBottomRight: [60, 60] };
  map.fitBounds(DATA.meta.bounds, Object.assign({ animate: true }, options));
}

const indicatorSelect = document.getElementById("indicatorSelect");
const groups = new Map();
ALL_INDICATORS.forEach(indicator => {
  if (!groups.has(indicator.group)) {
    const group = document.createElement("optgroup");
    group.label = indicator.group;
    groups.set(indicator.group, group);
    indicatorSelect.appendChild(group);
  }
  const option = document.createElement("option");
  option.value = indicator.id;
  option.textContent = indicator.label;
  groups.get(indicator.group).appendChild(option);
});
indicatorSelect.addEventListener("change", event => setIndicator(event.target.value));

const basemapSelect = document.getElementById("basemapSelect");
DATA.basemaps.forEach(basemap => {
  const option = document.createElement("option");
  option.value = basemap.id;
  option.textContent = basemap.label;
  basemapSelect.appendChild(option);
});
basemapSelect.addEventListener("change", event => setBasemap(event.target.value));

const servicesBlock = document.getElementById("servicesBlock");
const serviceList = document.getElementById("serviceList");
if (DATA.services.length) {
  servicesBlock.hidden = false;
  DATA.services.forEach(service => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "service-toggle";
    button.dataset.service = service.id;
    button.setAttribute("aria-pressed", "false");
    button.innerHTML = '<span class="dot" style="background:' + esc(service.color) + '"></span>' +
      esc(service.label) + ' <span class="count">' + formatInt(service.count) + "</span>";
    button.addEventListener("click", () => {
      serviceState[service.id] = !serviceState[service.id];
      refreshServiceButtons();
    });
    serviceList.appendChild(button);
  });
}

const statsModal = document.getElementById("statsModal");
const statsButton = document.getElementById("statsButton");
const filterRows = document.getElementById("filterRows");
const statsFields = DATA.statistics && Array.isArray(DATA.statistics.fields) ? DATA.statistics.fields : [];
const statsFieldMap = new Map(statsFields.map(field => [field.id, field]));
const statsBlockFeatures = DATA.layers.blocks.features || [];
let statsFilters = [];
// STATS_JS_START

function statsNumeric(value) {
  if (value === null || value === undefined || value === "") return null;
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function statsQuantile(sorted, quantile) {
  if (!sorted.length) return null;
  if (sorted.length === 1) return sorted[0];
  const position = (sorted.length - 1) * quantile;
  const lower = Math.floor(position);
  const upper = Math.ceil(position);
  if (lower === upper) return sorted[lower];
  return sorted[lower] + (sorted[upper] - sorted[lower]) * (position - lower);
}

function statsSummary(values) {
  const sorted = values.slice().sort((left, right) => left - right);
  const sum = sorted.reduce((total, value) => total + value, 0);
  return {
    n: sorted.length,
    mean: sorted.length ? sum / sorted.length : null,
    median: statsQuantile(sorted, 0.5),
    min: sorted.length ? sorted[0] : null,
    max: sorted.length ? sorted[sorted.length - 1] : null,
    q1: statsQuantile(sorted, 0.25),
    q3: statsQuantile(sorted, 0.75),
    sum: sorted.length ? sum : null
  };
}

function statsValues(features, field) {
  return features.map(feature => statsNumeric(feature.properties[field])).filter(value => value !== null);
}

function statsRank(values) {
  const order = values.map((value, index) => ({ value, index })).sort((left, right) => left.value - right.value);
  const ranks = new Array(values.length);
  let index = 0;
  while (index < order.length) {
    let end = index;
    while (end + 1 < order.length && order[end + 1].value === order[index].value) end += 1;
    const rank = (index + end) / 2 + 1;
    for (let cursor = index; cursor <= end; cursor += 1) ranks[order[cursor].index] = rank;
    index = end + 1;
  }
  return ranks;
}

function statsCorrelation(features, left, right) {
  const pairs = features
    .map(feature => [statsNumeric(feature.properties[left]), statsNumeric(feature.properties[right])])
    .filter(pair => pair[0] !== null && pair[1] !== null);
  if (pairs.length < 5) return null;
  const leftRanks = statsRank(pairs.map(pair => pair[0]));
  const rightRanks = statsRank(pairs.map(pair => pair[1]));
  const meanLeft = leftRanks.reduce((sum, value) => sum + value, 0) / leftRanks.length;
  const meanRight = rightRanks.reduce((sum, value) => sum + value, 0) / rightRanks.length;
  let numerator = 0;
  let leftSquare = 0;
  let rightSquare = 0;
  for (let index = 0; index < leftRanks.length; index += 1) {
    const deltaLeft = leftRanks[index] - meanLeft;
    const deltaRight = rightRanks[index] - meanRight;
    numerator += deltaLeft * deltaRight;
    leftSquare += deltaLeft * deltaLeft;
    rightSquare += deltaRight * deltaRight;
  }
  if (!leftSquare || !rightSquare) return null;
  return { rho: numerator / Math.sqrt(leftSquare * rightSquare), n: pairs.length };
}

function statsFilterMatches(properties, filter) {
  const spec = statsFieldMap.get(filter.field) || { kind: "numeric" };
  const raw = properties ? properties[filter.field] : null;
  if (spec.kind === "boolean") {
    return Boolean(raw) === (filter.value === true || filter.value === "true");
  }
  if (filter.op === "contains") {
    return String(raw === null || raw === undefined ? "" : raw).toLowerCase()
      .includes(String(filter.value || "").toLowerCase());
  }
  if (["gt", "gte", "lt", "lte", "between"].includes(filter.op)) {
    const number = statsNumeric(raw);
    if (number === null) return false;
    if (filter.op === "between") {
      const first = statsNumeric(filter.value[0]);
      const second = statsNumeric(filter.value[1]);
      if (first === null || second === null) return false;
      const low = Math.min(first, second);
      const high = Math.max(first, second);
      return number >= low && number <= high;
    }
    const target = statsNumeric(filter.value);
    if (target === null) return false;
    if (filter.op === "gt") return number > target;
    if (filter.op === "gte") return number >= target;
    if (filter.op === "lt") return number < target;
    return number <= target;
  }
  if (filter.op === "ne") return String(raw) !== String(filter.value);
  return String(raw) === String(filter.value);
}

function statsFilteredFeatures() {
  return statsBlockFeatures.filter(feature => statsFilters.every(filter => statsFilterMatches(feature.properties, filter)));
}

function statsInsights(features) {
  const insights = [];
  const green = statsValues(features, "green_share");
  if (green.length >= 5) {
    const covered = green.filter(value => value >= 0.5).length / green.length;
    insights.push("Доля кварталов с green_share ≥ 0,5: " + Math.round(covered * 100) + "% (n=" + green.length + ").");
  }
  const access = statsValues(features, "green_access_m");
  if (access.length >= 5) {
    const within = access.filter(value => value <= 500).length / access.length;
    insights.push("Медианный доступ к публичной зелени по дорожной сети: " + Math.round(statsQuantile(access.slice().sort((a, b) => a - b), 0.5)) + " м; в пределах 500 м — " + Math.round(within * 100) + "% кварталов.");
  }
  const built = features.filter(feature => statsNumeric(feature.properties.osr) !== null);
  const osr = statsValues(built, "osr");
  if (osr.length >= 5) {
    insights.push("Медианная открытость застройки (OSR): " + statsQuantile(osr.slice().sort((a, b) => a - b), 0.5).toFixed(2) + " (n=" + osr.length + " кварталов с застройкой).");
  }
  const populated = features.filter(feature => Boolean(feature.properties.has_population));
  [["grocery", "магазинами"], ["parks", "парками"]].forEach(([serviceId, label]) => {
    const values = statsValues(populated, "provision_strong_" + serviceId);
    if (values.length >= 5) {
      const covered = values.filter(value => value >= 0.999999).length / values.length;
      insights.push("Полная обеспеченность " + label + ": " + Math.round(covered * 100) + "% (n=" + values.length + " кварталов с населением).");
    }
  });
  [
    ["с застройкой", built],
    ["с населением", populated]
  ].forEach(([label, universe]) => {
    const correlation = statsCorrelation(universe, "osr", "green_share");
    if (correlation) {
      insights.push("Spearman OSR ↔ green_share, " + label + ": ρ=" + correlation.rho.toFixed(3) + " (n=" + correlation.n + ").");
    }
  });
  return insights;
}
// STATS_JS_END

function statsBarRows(rows) {
  const maximum = Math.max(1, ...rows.map(row => row.value));
  return rows.map(row => (
    '<div class="bar-row"><span title="' + esc(row.label) + '">' + esc(row.label) + "</span>" +
    '<div class="bar-track"><div class="bar-fill" style="width:' + Math.round(row.value / maximum * 100) + "%;background:" + esc(row.color || "#0071e3") + '"></div></div>' +
    "<b>" + esc(row.display) + "</b></div>"
  )).join("");
}

function renderStatsCards(meta) {
  const cards = [
    ["Кварталов", formatInt(meta.blocks)],
    ["С застройкой", formatInt(meta.built)],
    ["С населением", formatInt(meta.populated)],
    ["Население", formatInt(meta.population)]
  ];
  document.getElementById("statsCards").innerHTML = cards.map(card => (
    '<div class="stats-card"><span>' + esc(card[0]) + "</span><b>" + esc(card[1]) + "</b></div>"
  )).join("");
}

function renderStatsTable(features) {
  const keyIds = [
    "population", "osr", "green_share", "green_access_m", "green_m2_per_capita",
    "fsi", "area_accessibility", "provision_strong_grocery", "provision_strong_parks"
  ];
  if (activeIndicator.kind === "numeric" && !keyIds.includes(activeIndicator.id)) keyIds.unshift(activeIndicator.id);
  const rows = keyIds
    .map(id => DATA.indicators.find(indicator => indicator.id === id))
    .filter(Boolean)
    .map(spec => {
      const values = statsValues(features, spec.id);
      const summary = statsSummary(values);
      const missing = features.length - summary.n;
      const warn = summary.n < 5 ? ' <span class="warn">n&lt;5</span>' : "";
      return "<tr><td>" + esc(spec.label) + warn + "</td><td>" + formatInt(summary.n) +
        "</td><td>" + formatNumber(summary.median, spec, false) +
        "</td><td>" + formatNumber(summary.mean, spec, false) +
        "</td><td>" + formatNumber(summary.min, spec, false) +
        "</td><td>" + formatNumber(summary.max, spec, false) + "</td></tr>";
    });
  document.getElementById("statsTable").innerHTML = rows.length
    ? '<table class="stats-table"><thead><tr><th>Показатель</th><th>n</th><th>Медиана</th><th>Среднее</th><th>Мин</th><th>Макс</th></tr></thead><tbody>' + rows.join("") + "</tbody></table>"
    : '<div class="stats-empty">Нет кварталов под выбранные фильтры.</div>';
}

function renderStatsCharts(features) {
  const ledger = {};
  features.forEach(feature => {
    const value = feature.properties.land_use;
    if (value !== null && value !== undefined) ledger[value] = (ledger[value] || 0) + 1;
  });
  const landRows = Object.entries(ledger)
    .sort((left, right) => right[1] - left[1])
    .map(([value, count]) => ({
      label: landUseLabel(value),
      value: count,
      display: formatInt(count),
      color: (categoryFor(value, landUseIndicator) || {}).color || "#8E8E93"
    }));
  document.getElementById("statsLanduse").innerHTML = landRows.length
    ? statsBarRows(landRows)
    : '<div class="stats-empty">Нет данных о землепользовании.</div>';

  const bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0000001];
  const counts = [0, 0, 0, 0, 0];
  statsValues(features, "green_share").forEach(value => {
    const index = Math.max(0, Math.min(4, bins.findIndex((upper, position) => value < upper && position > 0) - 1));
    counts[index] += 1;
  });
  document.getElementById("statsGreenBins").innerHTML = statsBarRows(counts.map((count, index) => ({
    label: (index * 20) + "–" + ((index + 1) * 20) + "%",
    value: count,
    display: formatInt(count),
    color: "#34c759"
  })));

  const populated = features.filter(feature => Boolean(feature.properties.has_population));
  const provisionRows = [["grocery", "Магазины"], ["parks", "Парки"]].map(([serviceId, label]) => {
    const values = statsValues(populated, "provision_strong_" + serviceId);
    const full = values.filter(value => value >= 0.999999).length;
    const share = values.length ? full / values.length : 0;
    return { label: label, value: share, display: Math.round(share * 100) + "%", color: "#30d158" };
  });
  document.getElementById("statsProvision").innerHTML = populated.length
    ? statsBarRows(provisionRows)
    : '<div class="stats-empty">Нет кварталов с населением.</div>';
}

function renderStats() {
  if (!DATA.statistics) return;
  const features = statsFilteredFeatures();
  const meta = {
    blocks: features.length,
    built: features.filter(feature => Boolean(feature.properties.has_building)).length,
    populated: features.filter(feature => Boolean(feature.properties.has_population)).length,
    population: features.reduce((sum, feature) => sum + (statsNumeric(feature.properties.population) || 0), 0)
  };
  renderStatsCards(meta);
  renderStatsTable(features);
  renderStatsCharts(features);
  const insights = statsInsights(features);
  document.getElementById("statsInsights").innerHTML = insights.length
    ? insights.map(item => "<li>" + esc(item) + "</li>").join("")
    : '<li class="warn">Недостаточно данных для автоматических выводов.</li>';
  document.getElementById("statsDisclaimer").textContent = DATA.statistics.disclaimer || "";
}

function statsDefaultValue(spec) {
  if (!spec) return "";
  if (spec.kind === "boolean") return "true";
  if (spec.kind === "categorical") return (spec.categories && spec.categories[0]) || "";
  return 0;
}

function statsOperatorOptions(kind) {
  if (kind === "categorical") return [["eq", "="], ["ne", "≠"], ["contains", "содержит"]];
  if (kind === "boolean") return [["eq", "="]];
  return [["gte", "≥"], ["gt", ">"], ["lte", "≤"], ["lt", "<"], ["eq", "="], ["between", "между"]];
}

function renderFilterRows() {
  filterRows.innerHTML = "";
  statsFilters.forEach((filter, index) => {
    const spec = statsFieldMap.get(filter.field);
    const row = document.createElement("div");
    row.className = "filter-row";

    const fieldSelect = document.createElement("select");
    statsFields.forEach(field => {
      const option = document.createElement("option");
      option.value = field.id;
      option.textContent = field.label;
      option.selected = field.id === filter.field;
      fieldSelect.appendChild(option);
    });
    fieldSelect.addEventListener("change", () => {
      filter.field = fieldSelect.value;
      const nextSpec = statsFieldMap.get(filter.field);
      const operators = statsOperatorOptions(nextSpec ? nextSpec.kind : "numeric");
      filter.op = operators[0][0];
      filter.value = statsDefaultValue(nextSpec);
      renderFilterRows();
      renderStats();
    });

    const operatorSelect = document.createElement("select");
    const operators = statsOperatorOptions(spec ? spec.kind : "numeric");
    operators.forEach(([value, label]) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = label;
      option.selected = value === filter.op;
      operatorSelect.appendChild(option);
    });
    operatorSelect.addEventListener("change", () => {
      filter.op = operatorSelect.value;
      if (filter.op === "between" && !Array.isArray(filter.value)) filter.value = [0, 1];
      renderFilterRows();
      renderStats();
    });

    const inputWrap = document.createElement("div");
    inputWrap.className = spec && spec.kind === "numeric" && filter.op === "between" ? "filter-range" : "";
    if (spec && spec.kind === "boolean") {
      const input = document.createElement("select");
      [["true", "Да"], ["false", "Нет"]].forEach(([value, label]) => {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = label;
        option.selected = String(filter.value) === value;
        input.appendChild(option);
      });
      input.addEventListener("change", () => {
        filter.value = input.value;
        renderStats();
      });
      inputWrap.appendChild(input);
    } else if (spec && spec.kind === "categorical") {
      const input = document.createElement("select");
      (spec.categories || []).forEach(value => {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = (spec.labels && spec.labels[value]) || value;
        option.selected = String(filter.value) === value;
        input.appendChild(option);
      });
      input.addEventListener("change", () => {
        filter.value = input.value;
        renderStats();
      });
      inputWrap.appendChild(input);
    } else if (filter.op === "between") {
      const low = document.createElement("input");
      low.type = "number";
      low.step = "any";
      low.value = Array.isArray(filter.value) ? filter.value[0] : 0;
      low.addEventListener("input", () => {
        filter.value = [low.value, high.value];
        renderStats();
      });
      const high = document.createElement("input");
      high.type = "number";
      high.step = "any";
      high.value = Array.isArray(filter.value) ? filter.value[1] : 1;
      high.addEventListener("input", () => {
        filter.value = [low.value, high.value];
        renderStats();
      });
      inputWrap.appendChild(low);
      inputWrap.appendChild(high);
    } else {
      const input = document.createElement("input");
      input.type = "number";
      input.step = "any";
      input.value = filter.value === null || filter.value === undefined ? "" : filter.value;
      input.addEventListener("input", () => {
        filter.value = input.value;
        renderStats();
      });
      inputWrap.appendChild(input);
    }

    const remove = document.createElement("button");
    remove.type = "button";
    remove.className = "filter-remove";
    remove.textContent = "Удалить";
    remove.addEventListener("click", () => {
      statsFilters.splice(index, 1);
      renderFilterRows();
      renderStats();
    });

    row.appendChild(fieldSelect);
    row.appendChild(operatorSelect);
    row.appendChild(inputWrap);
    row.appendChild(remove);
    filterRows.appendChild(row);
  });
}

document.getElementById("addFilter").addEventListener("click", () => {
  const spec = statsFields.find(field => field.kind === "numeric") || statsFields[0];
  if (!spec) return;
  statsFilters.push({ field: spec.id, op: "gte", value: 0 });
  renderFilterRows();
  renderStats();
});

document.getElementById("resetFilters").addEventListener("click", () => {
  statsFilters = [];
  renderFilterRows();
  renderStats();
});

document.querySelectorAll("[data-preset]").forEach(button => {
  button.addEventListener("click", () => {
    const preset = button.dataset.preset;
    if (preset === "all") statsFilters = [];
    if (preset === "built") statsFilters = [{ field: "has_building", op: "eq", value: "true" }];
    if (preset === "populated") statsFilters = [{ field: "has_population", op: "eq", value: "true" }];
    if (preset === "green") statsFilters = [{ field: "green_share", op: "gte", value: 0.5 }];
    renderFilterRows();
    renderStats();
  });
});

function openStats() {
  statsModal.hidden = false;
  renderFilterRows();
  renderStats();
}

function closeStats() {
  statsModal.hidden = true;
}

statsButton.addEventListener("click", openStats);
document.getElementById("statsClose").addEventListener("click", closeStats);
statsModal.addEventListener("click", event => {
  if (event.target === statsModal) closeStats();
});
window.addEventListener("keydown", event => {
  if (event.key === "Escape" && !statsModal.hidden) closeStats();
});

document.querySelectorAll("[data-blocks-mode]").forEach(button => {
  button.addEventListener("click", () => {
    if (button.dataset.blocksMode === "blank") {
      enterBlankMode();
    } else {
      enterCleanMode();
    }
  });
});
document.querySelectorAll("[data-access-mode]").forEach(button => {
  button.addEventListener("click", () => setAccessMode(button.dataset.accessMode));
});
document.getElementById("destinationMode").addEventListener("click", () => enterDestinationMode());
document.getElementById("resetView").addEventListener("click", fitView);
map.on("contextmenu", event => {
  L.DomEvent.preventDefault(event.originalEvent);
  enterCleanMode();
});
window.addEventListener("resize", () => map.invalidateSize());

const requestedBasemap = new URLSearchParams(window.location.search).get("basemap");
const initialBasemap = DATA.basemaps.some(item => item.id === requestedBasemap) ? requestedBasemap : "light";
setBasemap(initialBasemap);
setBlocksVisible(mapMode !== "blank");
updatePanel();
fitView();
if (new URLSearchParams(window.location.search).get("stats") === "1") openStats();
</script>
</body>
</html>
"""
