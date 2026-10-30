"""Service catalogue shared by the research pipeline and the dashboard."""

# pylint: disable=import-outside-toplevel

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd


SERVICE_GROUPS: list[dict[str, Any]] = [
    {"id": "retail", "label": "Торговля и общественное питание"},
    {"id": "education", "label": "Образование"},
    {"id": "healthcare", "label": "Здравоохранение"},
    {"id": "culture", "label": "Культура и досуг"},
    {"id": "nature", "label": "Природа и рекреация"},
    {"id": "transport", "label": "Транспорт и мобильность"},
    {"id": "finance", "label": "Финансы и административные услуги"},
    {"id": "safety", "label": "Безопасность"},
    {"id": "engineering", "label": "Инженерная инфраструктура"},
    {"id": "other", "label": "Прочие и специальные объекты"},
]

SERVICE_GROUP_BY_ID = {group["id"]: group for group in SERVICE_GROUPS}
SERVICE_GROUP_ORDER = {group["id"]: index for index, group in enumerate(SERVICE_GROUPS)}

SERVICE_SPECS: list[dict[str, Any]] = [
    {
        "id": "supermarket",
        "label": "Супермаркеты",
        "group": "retail",
        "color": "#0A84FF",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "convenience",
        "label": "Магазины у дома",
        "group": "retail",
        "color": "#64D2FF",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "cafe",
        "label": "Кафе",
        "group": "retail",
        "color": "#FF9F0A",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "school",
        "label": "Школы",
        "group": "education",
        "color": "#FF9F0A",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "kindergarten",
        "label": "Детские сады",
        "group": "education",
        "color": "#FFD60A",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "polyclinic",
        "label": "Поликлиники",
        "group": "healthcare",
        "color": "#FF453A",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "hospital",
        "label": "Больницы",
        "group": "healthcare",
        "color": "#FF375F",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "pharmacy",
        "label": "Аптеки",
        "group": "healthcare",
        "color": "#30D158",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "library",
        "label": "Библиотеки",
        "group": "culture",
        "color": "#BF5AF2",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "stadium",
        "label": "Стадионы",
        "group": "culture",
        "color": "#FF9F0A",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "religion",
        "label": "Религиозные объекты",
        "group": "culture",
        "color": "#BF5AF2",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "camp",
        "label": "Детские лагеря",
        "group": "culture",
        "color": "#FFD60A",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "zoo",
        "label": "Зоопарки",
        "group": "culture",
        "color": "#34C759",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "historic",
        "label": "Исторические места",
        "group": "culture",
        "color": "#BF5AF2",
        "render": "auto",
        "provision": False,
        "context_only": True,
    },
    {
        "id": "park",
        "label": "Парки",
        "group": "nature",
        "color": "#34C759",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "forest",
        "label": "Леса",
        "group": "nature",
        "color": "#30D158",
        "render": "auto",
        "provision": False,
        "context_only": True,
    },
    {
        "id": "reserve",
        "label": "Заповедники",
        "group": "nature",
        "color": "#34C759",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "beach",
        "label": "Пляжи",
        "group": "nature",
        "color": "#64D2FF",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "embankment",
        "label": "Набережные",
        "group": "nature",
        "color": "#64D2FF",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "bus_stop",
        "label": "Остановки",
        "group": "transport",
        "color": "#BF5AF2",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "parking",
        "label": "Парковки",
        "group": "transport",
        "color": "#8E8E93",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "pier",
        "label": "Причалы",
        "group": "transport",
        "color": "#64D2FF",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "port",
        "label": "Порты",
        "group": "transport",
        "color": "#0A84FF",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "train_station",
        "label": "Ж/д станции",
        "group": "transport",
        "color": "#FF375F",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "train_building",
        "label": "Ж/д здания",
        "group": "transport",
        "color": "#FF453A",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "bank",
        "label": "Банки",
        "group": "finance",
        "color": "#0A84FF",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "post_office",
        "label": "Почтовые отделения",
        "group": "finance",
        "color": "#64D2FF",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "mfz",
        "label": "МФЦ",
        "group": "finance",
        "color": "#0A84FF",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "outpost",
        "label": "Пункты полиции",
        "group": "safety",
        "color": "#0A84FF",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "fire_station",
        "label": "Пожарные станции",
        "group": "safety",
        "color": "#FF375F",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "energy",
        "label": "Электроснабжение",
        "group": "engineering",
        "color": "#FF453A",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "boilerhouse",
        "label": "Котельные",
        "group": "engineering",
        "color": "#FF453A",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "substation",
        "label": "Подстанции",
        "group": "engineering",
        "color": "#FFD60A",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
    {
        "id": "cemetery",
        "label": "Кладбища",
        "group": "other",
        "color": "#8E8E93",
        "render": "auto",
        "provision": True,
        "context_only": False,
    },
]

SERVICE_SPEC_BY_ID = {spec["id"]: spec for spec in SERVICE_SPECS}

SERVICE_ALIASES: dict[str, str] = {
    "post_office": "post",
    "boilerhouse": "energy",
    "fire_station": "government",
    "camp": "hotel",
    "mfz": "multifunctional_center",
    "outpost": "police",
    "port": "pier",
}

SERVICE_CONTEXT_ONLY = {spec["id"] for spec in SERVICE_SPECS if spec["context_only"]}
SERVICE_LABELS = {spec["id"]: spec["label"] for spec in SERVICE_SPECS}

CAPACITY_OVERRIDES: dict[str, float] = {
    "supermarket": 1000.0,
    "convenience": 100.0,
}

PROVISION_COMBINATIONS: list[dict[str, Any]] = [
    {
        "id": "grocery",
        "label": "Продукты: супермаркеты и магазины у дома",
        "short_label": "Продукты (комб.)",
        "group": "retail",
        "components": ["supermarket", "convenience"],
        "norm_service": "supermarket",
        "description": (
            "Совокупная ёмкость супермаркетов и магазинов у дома в пределах нормативной доступности. "
            "Используется норматив супермаркета как более консервативный; ёмкость магазинов у дома "
            "учитывается в общем балансе."
        ),
    },
    {
        "id": "parks",
        "label": "Парки и заповедники",
        "short_label": "Парки (комб.)",
        "group": "nature",
        "components": ["park", "reserve"],
        "norm_service": "park",
        "description": (
            "Совокупная ёмкость парков и заповедников в пределах нормативной доступности. "
            "Используется норматив парка; лес остаётся контекстным слоем и не входит в этот индекс."
        ),
    },
]

PROVISION_COMBINATION_BY_ID = {item["id"]: item for item in PROVISION_COMBINATIONS}


def resolve_service_type(service_id: str) -> str:
    """Return the BlocksNet service type for a source layer identifier."""
    return SERVICE_ALIASES.get(service_id, service_id)


def is_context_only(service_id: str) -> bool:
    """Return True when a layer is displayed but has no provision indicator."""
    return service_id in SERVICE_CONTEXT_ONLY


def service_spec(service_id: str) -> dict[str, Any] | None:
    """Return the catalogue entry for a service identifier."""
    return SERVICE_SPEC_BY_ID.get(service_id)


def service_group(service_id: str) -> dict[str, Any] | None:
    """Return the functional group for a service identifier."""
    spec = service_spec(service_id)
    return SERVICE_GROUP_BY_ID.get(spec["group"]) if spec else None


def list_service_files(services_dir: str | Path, *, include_context: bool = False) -> dict[str, tuple[Path, str]]:
    """Return service data files mapped to their BlocksNet types."""
    services_dir = Path(services_dir)
    if not services_dir.exists():
        return {}
    from blocksnet.config import service_types_config

    known_types = set(service_types_config.service_types.index)
    found: dict[str, tuple[Path, str]] = {}
    for path in sorted(services_dir.glob("*.geojson")):
        service_id = path.stem
        if not include_context and is_context_only(service_id):
            continue
        service_type = resolve_service_type(service_id)
        if service_type not in known_types:
            continue
        found[service_id] = (path, service_type)
    return found


def load_service_layer(
    path: str | Path,
    service_id: str,
    *,
    crs: str | None = None,
) -> gpd.GeoDataFrame:
    """Load a service layer and fill missing capacity by site area or service type."""
    from blocksnet.preprocessing.imputing import impute_services

    layer = gpd.read_file(path)
    if layer.crs is None:
        layer = layer.set_crs(4326)
    if crs is not None:
        layer = layer.to_crs(crs)
    layer = layer[layer.geometry.notna() & ~layer.geometry.is_empty].copy()
    if "capacity" not in layer.columns:
        layer["capacity"] = pd.NA
    layer["capacity"] = pd.to_numeric(layer["capacity"], errors="coerce")
    layer["capacity_source"] = "source"
    missing = layer["capacity"].isna() | (layer["capacity"] <= 0)
    layer.loc[missing, "capacity"] = pd.NA
    layer.loc[missing, "capacity_source"] = "missing"

    service_type = resolve_service_type(service_id)
    if is_context_only(service_id) or service_type not in _known_service_types():
        layer["capacity_source"] = "not_applicable"
        return layer

    layer = layer.copy()
    area_capacity = _capacity_from_site_area(layer, service_type)
    area_mask = missing & area_capacity.notna()
    layer.loc[area_mask, "capacity"] = area_capacity.loc[area_mask]
    layer.loc[area_mask, "capacity_source"] = "area"

    still_missing = layer["capacity"].isna() | (layer["capacity"] <= 0)
    override = CAPACITY_OVERRIDES.get(service_id)
    if override is not None and still_missing.any():
        layer.loc[still_missing, "capacity"] = override
        layer.loc[still_missing, "capacity_source"] = "override"

    still_missing = layer["capacity"].isna() | (layer["capacity"] <= 0)
    if still_missing.any():
        imputed = impute_services(
            layer.loc[still_missing, ["capacity", "geometry"]].copy(),
            service_type,
        )["capacity"]
        layer.loc[still_missing, "capacity"] = imputed
        layer.loc[still_missing, "capacity_source"] = "type"
    return layer


def _capacity_from_site_area(layer: gpd.GeoDataFrame, service_type: str) -> pd.Series:
    """Estimate capacity for polygonal objects using the closest standard site area."""
    from blocksnet.config import service_types_config

    result = pd.Series(pd.NA, index=layer.index, dtype="Float64")
    units = service_types_config.units
    rows = units[
        (units["service_type"] == service_type)
        & (pd.to_numeric(units["site_area"], errors="coerce") > 0)
    ]
    if rows.empty:
        return result

    geometries = layer.geometry
    polygon_mask = geometries.geom_type.isin(["Polygon", "MultiPolygon"])
    if not polygon_mask.any():
        return result

    measured = layer.loc[polygon_mask].to_crs(3857) if layer.crs and layer.crs.is_geographic else layer
    areas = measured.loc[polygon_mask].geometry.area
    reference_areas = pd.to_numeric(rows["site_area"], errors="coerce").astype(float)
    reference_capacities = pd.to_numeric(rows["capacity"], errors="coerce").astype(float)

    for index, area in areas.items():
        if not math.isfinite(area) or area <= 0:
            continue
        distance = (reference_areas / area).map(lambda ratio: abs(math.log(ratio)))
        result.loc[index] = float(reference_capacities.loc[distance.idxmin()])
    return result


def _known_service_types() -> set[str]:
    from blocksnet.config import service_types_config

    return set(service_types_config.service_types.index)
