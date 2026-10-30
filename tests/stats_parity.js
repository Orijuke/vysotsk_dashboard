const fs = require("fs");

const html = fs.readFileSync(process.argv[2], "utf8");
const dataMatch = html.match(/const DATA = (.*?);\r?\nconst MISSING_COLOR/s);
const scriptMatch = html.match(/\/\/ STATS_JS_START([\s\S]*?)\/\/ STATS_JS_END/);
if (!dataMatch || !scriptMatch) throw new Error("dashboard payload or stats block not found");

const data = JSON.parse(dataMatch[1]);
const filters = [];
const factory = new Function(
  "DATA",
  "statsFilters",
  "statsFieldMap",
  "statsBlockFeatures",
  scriptMatch[1] + "\nreturn { statsNumeric, statsSummary, statsValues, statsInsights, statsFilteredFeatures };"
);
const api = factory(
  data,
  filters,
  new Map(data.statistics.fields.map(field => [field.id, field])),
  data.layers.blocks.features
);
const features = data.layers.blocks.features;
const osr = api.statsSummary(api.statsValues(features, "osr"));
const green = api.statsSummary(api.statsValues(features, "green_share"));
const access = api.statsSummary(api.statsValues(features, "green_access_m"));
const built = features.filter(feature => api.statsNumeric(feature.properties.osr) !== null).length;
const populated = features.filter(feature => Boolean(feature.properties.has_population)).length;
const population = features.reduce((sum, feature) => sum + (api.statsNumeric(feature.properties.population) || 0), 0);

filters.push({ field: "green_share", op: "gte", value: 0.5 });
const filtered = api.statsFilteredFeatures();
const filteredGreen = api.statsSummary(api.statsValues(filtered, "green_share"));

console.log(JSON.stringify({
  blocks: features.length,
  built,
  populated,
  population,
  osr_n: osr.n,
  osr_median: osr.median,
  green_median: green.median,
  access_n: access.n,
  access_median: access.median,
  insights: api.statsInsights(features).length,
  filtered_blocks: filtered.length,
  filtered_green_n: filteredGreen.n,
  filtered_green_median: filteredGreen.median
}));
