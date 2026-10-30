"""Standalone interactive dashboard for urban indicator maps.

The builder produces a single HTML page with an Apple-inspired minimal UI.
Only Leaflet and raster basemaps are loaded from the network; all thematic
data (blocks, water, services) is embedded into the page, so the dashboard
does not need a tile API key and works with any of the built-in basemaps,
including a vector-only "no basemap" mode.
"""

from __future__ import annotations

import html
import json
import math
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import mapping

from .dashboard_template import HTML_TEMPLATE
from .service_catalog import load_service_layer
from .statistics import build_statistics_payload


PALETTES = {
    "sunset": ["#FFF3C4", "#FFD166", "#FF9F1C", "#FF5A5F", "#B5173B"],
    "aqua": ["#E5F8FF", "#8BE8FF", "#22C7F2", "#0A84FF", "#5E5CE6"],
    "green": ["#EAFBEA", "#A7F3A0", "#34C759", "#0FA958", "#046A38"],
    "amber": ["#FFF8E1", "#FFE08A", "#FFC300", "#FF9500", "#C1121F"],
    "violet": ["#F5EDFF", "#D9B8FF", "#BF5AF2", "#7D4CFF", "#4630EB"],
    "provision": ["#FF453A", "#FF9F0A", "#FFD60A", "#A7F3A0", "#30D158"],
}

MISSING_COLOR = "#E5E5EA"

INDICATOR_SPECS: list[dict[str, Any]] = [
    {
        "id": "population",
        "kind": "numeric",
        "label": "Население",
        "group": "Население и плотность",
        "description": "Численность населения, проживающего в квартале.",
        "unit": "чел.",
        "decimals": 0,
        "format": "number",
        "palette": "sunset",
        "aggregate": "sum",
    },
    {
        "id": "fsi",
        "kind": "numeric",
        "label": "Плотность застройки (FSI)",
        "group": "Население и плотность",
        "description": "Отношение площади застройки к площади квартала.",
        "unit": "",
        "decimals": 2,
        "format": "number",
        "palette": "aqua",
    },
    {
        "id": "gsi",
        "kind": "numeric",
        "label": "Доля застройки (GSI)",
        "group": "Население и плотность",
        "description": "Доля площади квартала, занятая зданиями.",
        "unit": "",
        "decimals": 2,
        "format": "number",
        "palette": "aqua",
    },
    {
        "id": "mxi",
        "kind": "numeric",
        "label": "Интенсивность (MXI)",
        "group": "Население и плотность",
        "description": "Индекс интенсивности застройки квартала.",
        "unit": "",
        "decimals": 2,
        "format": "number",
        "palette": "aqua",
    },
    {
        "id": "l",
        "kind": "numeric",
        "label": "Средняя этажность",
        "group": "Население и плотность",
        "description": "Средняя этажность зданий в квартале.",
        "unit": "эт.",
        "decimals": 1,
        "format": "number",
        "palette": "aqua",
    },
    {
        "id": "osr",
        "kind": "numeric",
        "label": "Открытость застройки (OSR)",
        "group": "Среда и доступность",
        "description": "Отношение свободной площади квартала к площади застройки. OSR не является долей озеленения.",
        "unit": "",
        "decimals": 2,
        "format": "number",
        "palette": "green",
    },
    {
        "id": "green_share",
        "kind": "numeric",
        "label": "Доля зелени",
        "group": "Зелёная инфраструктура",
        "description": "Доля площади квартала, покрытая лесами, парками и озеленёнными территориями landuse.",
        "unit": "",
        "decimals": 0,
        "format": "percent",
        "palette": "green",
        "breaks": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
    },
    {
        "id": "forest_share",
        "kind": "numeric",
        "label": "Доля леса",
        "group": "Зелёная инфраструктура",
        "description": "Доля площади квартала, занятая лесными полигонами.",
        "unit": "",
        "decimals": 0,
        "format": "percent",
        "palette": "green",
        "breaks": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
    },
    {
        "id": "park_share",
        "kind": "numeric",
        "label": "Доля парков",
        "group": "Зелёная инфраструктура",
        "description": "Доля площади квартала, занятая парками.",
        "unit": "",
        "decimals": 0,
        "format": "percent",
        "palette": "green",
        "breaks": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
    },
    {
        "id": "green_m2_per_capita",
        "kind": "numeric",
        "label": "Зелень на человека",
        "group": "Зелёная инфраструктура",
        "description": "Площадь зелени на одного жителя квартала; рассчитывается только при наличии населения.",
        "unit": "м²/чел.",
        "decimals": 1,
        "format": "number",
        "palette": "green",
    },
    {
        "id": "green_access_m",
        "kind": "numeric",
        "label": "Доступ к зелени по дорогам",
        "group": "Зелёная инфраструктура",
        "description": "Расстояние по существующему дорожному графу до парка "
        "или публичной озеленённой территории landuse.",
        "unit": "м",
        "decimals": 0,
        "format": "number",
        "palette": "green",
    },
    {
        "id": "green_access_500",
        "kind": "numeric",
        "label": "Зелень в пределах 500 м",
        "group": "Зелёная инфраструктура",
        "description": (
            "Доля кварталов, откуда публичная зелень доступна по дорожной "
            "или пешеходной сети не дальше 500 м."
        ),
        "unit": "",
        "decimals": 0,
        "format": "percent",
        "palette": "green",
        "breaks": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
    },
    {
        "id": "area_accessibility",
        "kind": "numeric",
        "label": "Пешеходная доступность",
        "group": "Среда и доступность",
        "description": "Среднее пешеходное время доступности территории по дорожной или пешеходной сети (5 км/ч).",
        "unit": "мин",
        "decimals": 0,
        "format": "number",
        "palette": "amber",
    },
    {
        "id": "land_use",
        "kind": "categorical",
        "label": "Землепользование",
        "group": "Морфология и землепользование",
        "description": "Преобладающий тип землепользования квартала.",
        "labels": {
            "LandUse.RESIDENTIAL": "Жилая",
            "LandUse.BUSINESS": "Деловая",
            "LandUse.RECREATION": "Рекреация",
            "LandUse.INDUSTRIAL": "Производственная",
            "LandUse.AGRICULTURE": "Сельскохозяйственная",
            "LandUse.SPECIAL": "Специальная",
            "LandUse.TRANSPORT": "Транспортная",
        },
        "colors": {
            "LandUse.RESIDENTIAL": "#FF9F0A",
            "LandUse.BUSINESS": "#0A84FF",
            "LandUse.RECREATION": "#30D158",
            "LandUse.INDUSTRIAL": "#FF453A",
            "LandUse.AGRICULTURE": "#FFD60A",
            "LandUse.SPECIAL": "#BF5AF2",
            "LandUse.TRANSPORT": "#64D2FF",
        },
    },
    {
        "id": "spacematrix_morphotype",
        "kind": "categorical",
        "label": "Морфотип (Spacematrix)",
        "group": "Морфология и землепользование",
        "description": "Морфотип квартала по классификации Spacematrix.",
        "labels": {
            "low-rise low-density non-residential": "Малоэтажный нежилой",
            "low-rise low-density residential": "Малоэтажный жилой",
            "low-rise low-density mixed-use": "Малоэтажный смешанный",
            "mid-rise low-density residential": "Среднеэтажный жилой",
            "high-mid-rise low-density residential": "Средне-высотный жилой",
        },
        "colors": {
            "low-rise low-density non-residential": "#FF9F0A",
            "low-rise low-density residential": "#0A84FF",
            "low-rise low-density mixed-use": "#BF5AF2",
            "mid-rise low-density residential": "#30D158",
            "high-mid-rise low-density residential": "#FF453A",
        },
    },
    {
        "id": "strelka_morphotype",
        "kind": "categorical",
        "label": "Морфотип (Strelka)",
        "group": "Морфология и землепользование",
        "description": "Морфотип квартала по классификации Strelka.",
        "labels": {
            "low-rise non-residential": "Малоэтажный нежилой",
            "individual residential": "Индивидуальная жилая застройка",
            "low-rise model": "Малоэтажная типовая застройка",
            "mid-rise": "Среднеэтажная застройка",
        },
        "colors": {
            "low-rise non-residential": "#FF9F0A",
            "individual residential": "#0A84FF",
            "low-rise model": "#BF5AF2",
            "mid-rise": "#30D158",
        },
    },
]

SERVICE_SPECS = [
    {"id": "school", "label": "Школы", "color": "#FF9F0A"},
    {"id": "kindergarten", "label": "Детские сады", "color": "#FFD60A"},
    {"id": "polyclinic", "label": "Поликлиники", "color": "#FF453A"},
    {"id": "hospital", "label": "Больницы", "color": "#FF375F"},
    {"id": "pharmacy", "label": "Аптеки", "color": "#30D158"},
    {"id": "supermarket", "label": "Супермаркеты", "color": "#0A84FF"},
    {"id": "convenience", "label": "Магазины у дома", "color": "#64D2FF"},
    {"id": "bus_stop", "label": "Остановки", "color": "#BF5AF2"},
    {"id": "park", "label": "Парки", "color": "#34C759"},
    {"id": "bank", "label": "Банки", "color": "#0A84FF"},
    {"id": "beach", "label": "Пляжи", "color": "#64D2FF"},
    {"id": "boilerhouse", "label": "Котельные", "color": "#FF453A"},
    {"id": "cafe", "label": "Кафе", "color": "#FF9F0A"},
    {"id": "camp", "label": "Детские лагеря", "color": "#FFD60A"},
    {"id": "cemetery", "label": "Кладбища", "color": "#8E8E93"},
    {"id": "embankment", "label": "Набережные", "color": "#64D2FF"},
    {"id": "energy", "label": "Электроснабжение", "color": "#FF453A"},
    {"id": "fire_station", "label": "Пожарные станции", "color": "#FF375F"},
    {"id": "library", "label": "Библиотеки", "color": "#BF5AF2"},
    {"id": "mfz", "label": "МФЦ", "color": "#0A84FF"},
    {"id": "outpost", "label": "Пункты полиции", "color": "#0A84FF"},
    {"id": "parking", "label": "Парковки", "color": "#8E8E93"},
    {"id": "pier", "label": "Причалы", "color": "#64D2FF"},
    {"id": "port", "label": "Порты", "color": "#0A84FF"},
    {"id": "post_office", "label": "Почтовые отделения", "color": "#64D2FF"},
    {"id": "religion", "label": "Религиозные объекты", "color": "#BF5AF2"},
    {"id": "reserve", "label": "Заповедники", "color": "#34C759"},
    {"id": "stadium", "label": "Стадионы", "color": "#FF9F0A"},
    {"id": "substation", "label": "Подстанции", "color": "#FFD60A"},
    {"id": "train_building", "label": "Ж/д здания", "color": "#FF453A"},
    {"id": "train_station", "label": "Ж/д станции", "color": "#FF375F"},
    {"id": "zoo", "label": "Зоопарки", "color": "#34C759"},
    {"id": "forest", "label": "Леса", "color": "#30D158", "provision": False},
    {"id": "historic", "label": "Исторические места", "color": "#BF5AF2", "provision": False},
]

PROVISION_SPECS = [(spec["id"], spec["label"]) for spec in SERVICE_SPECS if spec.get("provision", True)]

for _service_id, _service_label in PROVISION_SPECS:
    INDICATOR_SPECS.append(
        {
            "id": f"provision_strong_{_service_id}",
            "kind": "numeric",
            "label": f"Обеспеченность: {_service_label}",
            "group": "Обеспеченность сервисами",
            "description": "Доля спроса на услугу, покрытая в пределах нормативной доступности.",
            "unit": "",
            "decimals": 0,
            "format": "percent",
            "palette": "provision",
            "breaks": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
        }
    )

COMBINED_PROVISION_SPECS = [
    {
        "id": "grocery",
        "label": "Магазины (супермаркеты + у дома)",
        "description": "Суммарная обеспеченность взаимозаменяемыми магазинами; норматив — супермаркет.",
    },
    {
        "id": "parks",
        "label": "Парки (парки + заповедники)",
        "description": "Суммарная обеспеченность парками и заповедниками; норматив — парк.",
    },
]

for _combined in COMBINED_PROVISION_SPECS:
    INDICATOR_SPECS.append(
        {
            "id": f"provision_strong_{_combined['id']}",
            "kind": "numeric",
            "label": f"Обеспеченность: {_combined['label']}",
            "group": "Обеспеченность сервисами",
            "description": _combined["description"],
            "unit": "",
            "decimals": 0,
            "format": "percent",
            "palette": "provision",
            "breaks": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
        }
    )

POLYGON_SERVICES = {
    "forest",
    "park",
    "reserve",
    "cemetery",
    "historic",
    "beach",
    "embankment",
    "stadium",
    "zoo",
}

BASEMAPS = [
    {
        "id": "light",
        "label": "Светлая",
        "tiles": [
            {
                "url": (
                    "https://server.arcgisonline.com/ArcGIS/rest/services/"
                    "Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}"
                ),
                "attribution": "Tiles &copy; Esri",
                "maxNativeZoom": 16,
            },
            {
                "url": (
                    "https://server.arcgisonline.com/ArcGIS/rest/services/"
                    "Canvas/World_Light_Gray_Reference/MapServer/tile/{z}/{y}/{x}"
                ),
                "maxNativeZoom": 16,
            },
        ],
    },
    {
        "id": "streets",
        "label": "Улицы",
        "tiles": [
            {
                "url": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                "attribution": "&copy; OpenStreetMap contributors",
                "maxNativeZoom": 19,
            }
        ],
    },
    {
        "id": "dark",
        "label": "Тёмная",
        "tiles": [
            {
                "url": (
                    "https://server.arcgisonline.com/ArcGIS/rest/services/"
                    "Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}"
                ),
                "attribution": "Tiles &copy; Esri",
                "maxNativeZoom": 16,
            },
            {
                "url": (
                    "https://server.arcgisonline.com/ArcGIS/rest/services/"
                    "Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}"
                ),
                "maxNativeZoom": 16,
            },
        ],
    },
    {
        "id": "satellite",
        "label": "Спутник",
        "tiles": [
            {
                "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                "attribution": "Tiles &copy; Esri",
                "maxNativeZoom": 19,
            }
        ],
    },
    {
        "id": "none",
        "label": "Без подложки",
        "tiles": [],
    },
]


def _clean_value(value: Any) -> Any:
    """Convert numpy/pandas values into JSON-safe primitives."""
    # pylint: disable=too-many-return-statements
    if value is None:
        return None
    if isinstance(value, (np.floating, float)):
        number = float(value)
        return number if math.isfinite(number) else None
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, str):
        return value
    if isinstance(value, (int, bool)):
        return value
    if hasattr(value, "value"):
        return _clean_value(value.value)
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, (list, tuple)):
        return [_clean_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _clean_value(item) for key, item in value.items()}
    return str(value)


def _rounded_geometry(geometry: Any, ndigits: int = 6) -> dict[str, Any] | None:
    """Return a GeoJSON geometry with rounded coordinates."""
    if geometry is None or geometry.is_empty:
        return None
    obj = mapping(geometry)

    def walk(node: Any) -> Any:
        if isinstance(node, (list, tuple)):
            if node and isinstance(node[0], (int, float)):
                return [round(float(item), ndigits) for item in node]
            return [walk(item) for item in node]
        return node

    return {"type": obj["type"], "coordinates": walk(obj["coordinates"])}


def _feature_collection(gdf: gpd.GeoDataFrame, columns: list[str] | None = None) -> dict[str, Any]:
    """Build a compact GeoJSON FeatureCollection with cleaned properties."""
    if gdf.crs is not None:
        gdf = gdf.to_crs(4326)
    if columns is None:
        columns = [column for column in gdf.columns if column != "geometry"]
    records = gdf[columns].to_dict("records") if columns else [{} for _ in range(len(gdf))]
    features: list[dict[str, Any]] = []
    for geometry, record in zip(gdf.geometry, records):
        rounded = _rounded_geometry(geometry)
        if rounded is None:
            continue
        features.append(
            {
                "type": "Feature",
                "properties": {column: _clean_value(record.get(column)) for column in columns},
                "geometry": rounded,
            }
        )
    return {"type": "FeatureCollection", "features": features}


def _numeric_breaks(series: pd.Series, fixed: list[float] | None = None, classes: int = 5) -> list[float]:
    """Build break points for a quantile colour scale, keeping zero values readable."""
    if fixed:
        return [float(value) for value in fixed]
    values = pd.to_numeric(series, errors="coerce").dropna().to_numpy(dtype=float)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    low, high = float(values.min()), float(values.max())
    if math.isclose(low, high):
        step = max(abs(low) * 0.1, 1.0)
        return [low + index * step for index in range(classes + 1)]
    positive = values[values > 0]
    if positive.size >= classes * 2 and float((values <= 0).mean()) >= 0.1:
        quantiles = np.quantile(positive, [0.2, 0.4, 0.6, 0.8])
        breaks = [0.0, *[float(value) for value in quantiles], high]
    else:
        quantiles = np.quantile(values, np.linspace(0, 1, classes + 1))
        breaks = [float(value) for value in quantiles]
    breaks[0] = low
    breaks[-1] = high
    return [round(value, 6) for value in breaks]


def _numeric_cards(spec: dict[str, Any], series: pd.Series) -> list[dict[str, Any]]:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    decimals = spec.get("decimals", 0)
    number_format = spec.get("format", "number")

    def card(label: str, value: Any, fmt: str | None = None, digits: int | None = None) -> dict[str, Any]:
        return {
            "label": label,
            "value": None if close_nan(value) else float(value),
            "format": fmt or number_format,
            "decimals": decimals if digits is None else digits,
        }

    if spec.get("aggregate") == "sum":
        cards = [
            card("Сумма", clean.sum()),
            card("Медиана", clean.median()),
            card("Среднее", clean.mean()),
            card("Максимум", clean.max()),
        ]
    else:
        cards = [
            card("Медиана", clean.median()),
            card("Среднее", clean.mean()),
            card("Максимум", clean.max()),
            card("Кварталов", clean.size, "count", 0),
        ]
    return cards


def close_nan(value: Any) -> bool:
    """Return True when a value is missing."""
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return value is None


def _numeric_indicator(results: gpd.GeoDataFrame, spec: dict[str, Any]) -> dict[str, Any]:
    series = pd.to_numeric(results[spec["id"]], errors="coerce")
    clean = series.dropna()
    return {
        "id": spec["id"],
        "kind": "numeric",
        "label": spec["label"],
        "group": spec["group"],
        "description": spec["description"],
        "unit": spec.get("unit", ""),
        "decimals": spec.get("decimals", 0),
        "format": spec.get("format", "number"),
        "palette": PALETTES[spec["palette"]],
        "breaks": _numeric_breaks(series, spec.get("breaks")),
        "stats": {"cards": _numeric_cards(spec, series)},
        "count": int(clean.size),
        "missing": int(series.isna().sum()),
    }


def _categorical_indicator(results: gpd.GeoDataFrame, spec: dict[str, Any]) -> dict[str, Any]:
    raw = results[spec["id"]].map(_clean_value)
    counts = raw.value_counts(dropna=True)
    total = int(len(raw))
    categories: list[dict[str, Any]] = []

    for value, count in counts.items():
        key = str(value)
        categories.append(
            {
                "value": key,
                "label": spec["labels"].get(key, key),
                "color": spec["colors"].get(key, "#8E8E93"),
                "count": int(count),
                "share": float(count / total) if total else 0.0,
            }
        )

    missing = total - int(counts.sum())
    if missing:
        categories.append(
            {
                "value": "__missing__",
                "label": "Нет данных",
                "color": MISSING_COLOR,
                "count": missing,
                "share": float(missing / total) if total else 0.0,
                "missing": True,
            }
        )

    populated = [category for category in categories if not category.get("missing")]
    dominant = populated[0] if populated else None
    cards = [
        {
            "label": "Доминирует",
            "value": dominant["label"] if dominant else None,
            "format": "text",
            "decimals": 0,
        },
        {
            "label": "Доля",
            "value": dominant["share"] if dominant else None,
            "format": "percent",
            "decimals": 0,
        },
        {"label": "Кварталов", "value": total - missing, "format": "count", "decimals": 0},
        {"label": "Категорий", "value": len(populated), "format": "count", "decimals": 0},
    ]

    return {
        "id": spec["id"],
        "kind": "categorical",
        "label": spec["label"],
        "group": spec["group"],
        "description": spec["description"],
        "unit": "",
        "decimals": 0,
        "format": "text",
        "categories": categories,
        "stats": {"cards": cards},
        "count": total - missing,
        "missing": missing,
    }


def _accessibility_payload(results: gpd.GeoDataFrame, path: Path) -> dict[str, Any]:
    """Embed the pedestrian matrix for destination accessibility mode."""
    if not path.exists():
        return {"blockIds": [], "minutes": []}
    matrix = pd.read_csv(path, index_col=0)
    matrix.index = matrix.index.astype(int)
    matrix.columns = matrix.columns.astype(int)
    matrix = matrix.reindex(index=results.index, columns=results.index)
    values = matrix.to_numpy(dtype=float)
    minutes = [
        [round(float(value), 1) if math.isfinite(value) else None for value in row]
        for row in values
    ]
    return {
        "blockIds": results["block_id"].astype(str).tolist(),
        "minutes": minutes,
    }


def _services_payload(services_dir: Path | None) -> list[dict[str, Any]]:
    if services_dir is None:
        return []
    payload: list[dict[str, Any]] = []
    for spec in SERVICE_SPECS:
        candidates = (
            services_dir / f"service_{spec['id']}.geojson",
            services_dir / f"{spec['id']}.geojson",
        )
        path = next((candidate for candidate in candidates if candidate.exists()), None)
        if path is None:
            continue
        service = load_service_layer(path, spec["id"], crs=4326)
        service = service[service.geometry.notna() & ~service.geometry.is_empty].copy()
        if service.empty:
            continue
        geometry_types = set(service.geometry.geom_type)
        if geometry_types <= {"Polygon", "MultiPolygon"}:
            geometry_kind = "polygon"
        elif geometry_types <= {"Point", "MultiPoint"}:
            geometry_kind = "point"
        else:
            geometry_kind = "auto"
        columns = [
            column
            for column in (
                "name",
                "name:ru",
                "service_name",
                "amenity",
                "shop",
                "leisure",
                "brand",
                "capacity",
                "capacity_source",
            )
            if column in service.columns
        ]
        collection = _feature_collection(service, columns)
        if not collection["features"]:
            continue
        payload.append(
            {
                "id": spec["id"],
                "label": spec["label"],
                "color": spec["color"],
                "count": len(collection["features"]),
                "provision": f"provision_strong_{spec['id']}",
                "geometry": geometry_kind,
                "polygon": spec["id"] in POLYGON_SERVICES or geometry_kind == "polygon",
                "geojson": collection,
            }
        )
    return payload


def build_dashboard(  # pylint: disable=too-many-locals,too-many-statements
    results_path: str | Path,
    output_path: str | Path,
    *,
    boundaries_path: str | Path | None = None,
    lakes_path: str | Path | None = None,
    services_dir: str | Path | None = None,
    title: str = "Высоцкое городское поселение",
    subtitle: str = "Интерактивный профиль городской среды",
) -> Path:
    """Build and save a standalone interactive HTML dashboard."""
    results_path = Path(results_path)
    output_path = Path(output_path)
    boundaries_path = Path(boundaries_path) if boundaries_path else None
    lakes_path = Path(lakes_path) if lakes_path else None
    services_dir = Path(services_dir) if services_dir else results_path.parent

    results = gpd.read_file(results_path)
    if results.crs is None:
        results = results.set_crs(4326)
    results = results.to_crs(4326)

    boundaries = None
    if boundaries_path and boundaries_path.exists():
        boundaries = gpd.read_file(boundaries_path)
        if boundaries.crs is None:
            boundaries = boundaries.set_crs(4326)
        boundaries = boundaries.to_crs(4326)

    lakes = None
    if lakes_path and lakes_path.exists():
        lakes = gpd.read_file(lakes_path)
        if lakes.crs is None:
            lakes = lakes.set_crs(4326)
        lakes = lakes.to_crs(4326)
        lakes = lakes[~lakes.geometry.duplicated()].copy()

    indicator_ids = [spec["id"] for spec in INDICATOR_SPECS if spec["id"] in results.columns]
    indicators = []
    for spec in INDICATOR_SPECS:
        if spec["id"] not in results.columns:
            continue
        if spec["kind"] == "numeric":
            indicators.append(_numeric_indicator(results, spec))
        else:
            indicators.append(_categorical_indicator(results, spec))

    land_use_share_columns = [
        "residential",
        "business",
        "recreation",
        "industrial",
        "agriculture",
        "special",
        "transport",
    ]
    block_properties = [
        column
        for column in dict.fromkeys(
            indicator_ids + land_use_share_columns + ["block_id", "has_building", "has_population"]
        )
        if column in results.columns
    ]
    service_metric_columns = [
        column
        for column in results.columns
        if column.startswith(
            (
                "access_time_",
                "service_demand_",
                "service_served_",
                "service_capacity_",
                "graph_snap_",
            )
        )
    ]
    block_properties.extend(
        column for column in service_metric_columns if column not in block_properties
    )
    blocks = _feature_collection(results, block_properties)
    statistics = build_statistics_payload(results, INDICATOR_SPECS)
    empty_collection = {"type": "FeatureCollection", "features": []}
    land = _feature_collection(boundaries, []) if boundaries is not None else empty_collection
    water = _feature_collection(lakes, []) if lakes is not None else empty_collection

    spatial_reference = boundaries if boundaries is not None and not boundaries.empty else results
    min_x, min_y, max_x, max_y = spatial_reference.total_bounds
    bounds = [[float(min_y), float(min_x)], [float(max_y), float(max_x)]]
    center = [float((min_y + max_y) / 2), float((min_x + max_x) / 2)]
    population = None
    if "population" in results.columns:
        population = int(pd.to_numeric(results["population"], errors="coerce").fillna(0).sum())

    payload = {
        "meta": {
            "title": title,
            "subtitle": subtitle,
            "bounds": bounds,
            "center": center,
            "blockCount": int(len(results)),
            "population": population,
        },
        "indicators": indicators,
        "statistics": statistics,
        "services": _services_payload(services_dir),
        "accessibility": {
            **_accessibility_payload(
                results, results_path.parent / "accessibility_matrix_pedestrian.csv"
            ),
            "drive": _accessibility_payload(
                results, results_path.parent / "accessibility_matrix_drive.csv"
            ),
        },
        "basemaps": BASEMAPS,
        "layers": {"blocks": blocks, "land": land, "water": water},
    }

    serialized = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    serialized = serialized.replace("</", "<\\/")
    document = (
        HTML_TEMPLATE.replace("__PAGE_TITLE__", html.escape(title))
        .replace("__TITLE__", html.escape(title))
        .replace("__SUBTITLE__", html.escape(subtitle))
        .replace("__PAYLOAD__", serialized)
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(document, encoding="utf-8")
    return output_path
