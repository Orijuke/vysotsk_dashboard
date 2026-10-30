from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import Point, box

from my_package.service_catalog import (
    PROVISION_COMBINATIONS,
    SERVICE_GROUPS,
    SERVICE_SPECS,
    is_context_only,
    list_service_files,
    load_service_layer,
    resolve_service_type,
)


def test_catalogue_groups_and_combinations():
    assert len(SERVICE_GROUPS) == 10
    assert len(SERVICE_SPECS) == 34
    assert {item["id"] for item in PROVISION_COMBINATIONS} == {"grocery", "parks"}
    assert is_context_only("forest") is True
    assert is_context_only("park") is False


def test_aliases_are_resolved():
    assert resolve_service_type("post_office") == "post"
    assert resolve_service_type("boilerhouse") == "energy"
    assert resolve_service_type("cafe") == "cafe"


def test_existing_service_files_are_discovered():
    services = Path(__file__).parents[1] / "notebooks" / "better_data" / "services"
    if not services.exists():
        pytest.skip("research data is not available")
    files = list_service_files(services)
    assert len(files) == 29
    assert "park" in files
    assert "forest" not in files
    assert files["supermarket"][0].name == "supermarket.geojson"


def test_capacity_overrides_for_missing_stores(tmp_path):
    path = tmp_path / "supermarket.geojson"
    gpd.GeoDataFrame(
        {"capacity": [None]},
        geometry=[Point(0, 0)],
        crs=3857,
    ).to_file(path, driver="GeoJSON")
    layer = load_service_layer(path, "supermarket", crs=3857)
    assert layer.loc[0, "capacity"] == 1000
    assert layer.loc[0, "capacity_source"] == "override"


def test_capacity_is_estimated_by_area_or_type(tmp_path):
    polygon_path = tmp_path / "school_polygon.geojson"
    gpd.GeoDataFrame(
        {"capacity": [None]},
        geometry=[box(0, 0, 100, 200)],
        crs=3857,
    ).to_file(polygon_path, driver="GeoJSON")
    polygon = load_service_layer(polygon_path, "school", crs=3857)
    assert polygon.loc[0, "capacity"] == 250
    assert polygon.loc[0, "capacity_source"] == "area"

    point_path = tmp_path / "school_point.geojson"
    gpd.GeoDataFrame(
        {"capacity": [None]},
        geometry=[Point(0, 0)],
        crs=3857,
    ).to_file(point_path, driver="GeoJSON")
    point = load_service_layer(point_path, "school", crs=3857)
    assert point.loc[0, "capacity"] == 250
    assert point.loc[0, "capacity_source"] == "type"

    source_path = tmp_path / "school_source.geojson"
    gpd.GeoDataFrame(
        {"capacity": [340]},
        geometry=[Point(0, 0)],
        crs=3857,
    ).to_file(source_path, driver="GeoJSON")
    source = load_service_layer(source_path, "school", crs=3857)
    assert source.loc[0, "capacity"] == 340
    assert source.loc[0, "capacity_source"] == "source"
