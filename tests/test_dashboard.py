import json
import re

import geopandas as gpd
import pandas as pd
from shapely.geometry import box

from my_package.dashboard import _services_payload, build_dashboard


def _results():
    frame = gpd.GeoDataFrame(
        {
            "block_id": ["B001", "B002", "B003"],
            "population": [100, 0, 30],
            "osr": [1.0, None, 0.5],
            "green_share": [0.2, 0.8, 0.6],
            "land_use": ["LandUse.RESIDENTIAL", "LandUse.RECREATION", "LandUse.RESIDENTIAL"],
            "residential": [1.0, 0.0, 0.6],
            "business": [0.0, 0.5, 0.0],
            "has_building": [True, False, True],
            "has_population": [True, False, True],
            "access_time_school": [12.5, None, 8.0],
            "service_demand_school": [12, 0, 4],
            "service_served_school": [12, 0, 0],
            "service_capacity_school": [0, 340, 0],
        },
        geometry=[box(0, 0, 0.01, 0.01), box(0.01, 0, 0.02, 0.01), box(0.02, 0, 0.03, 0.01)],
        crs=4326,
    )
    frame["osr"] = frame["osr"].astype(float)
    return frame


def test_build_dashboard_embeds_statistics(tmp_path):
    results_path = tmp_path / "results.geojson"
    _results().to_file(results_path, driver="GeoJSON")
    matrix = pd.DataFrame(
        [[0.0, 5.0, 10.0], [5.0, 0.0, 6.0], [10.0, 6.0, 0.0]],
        index=[0, 1, 2],
        columns=[0, 1, 2],
    )
    matrix.to_csv(tmp_path / "accessibility_matrix_pedestrian.csv")
    (matrix * 2).to_csv(tmp_path / "accessibility_matrix_drive.csv")
    output = build_dashboard(results_path, tmp_path / "dashboard.html", services_dir=tmp_path / "services")
    document = output.read_text(encoding="utf-8")

    match = re.search(r"const DATA = (.*?);\nconst MISSING_COLOR", document, re.DOTALL)
    assert match
    payload = json.loads(match.group(1))
    assert payload["statistics"]["baseline"]["meta"]["blocks"] == 3
    assert payload["statistics"]["baseline"]["meta"]["built"] == 2
    assert "green_share" in [field["id"] for field in payload["statistics"]["fields"]]
    assert "statsModal" in document
    assert 'id="statsButton"' in document
    assert "provision_strong_grocery" in document
    assert payload["accessibility"]["blockIds"] == ["B001", "B002", "B003"]
    assert payload["accessibility"]["minutes"][0][2] == 10.0
    assert payload["accessibility"]["drive"]["minutes"][0][2] == 20.0
    assert "__destination__" in document
    assert "__drive__" in document
    assert "__blank__" in document
    assert 'id="blocksToggle"' in document
    assert 'data-blocks-mode="blank"' in document
    assert 'id="accessModeToggle"' in document
    assert 'data-access-mode="drive"' in document

    blocks = {
        feature["properties"]["block_id"]: feature["properties"]
        for feature in payload["layers"]["blocks"]["features"]
    }
    assert blocks["B001"]["access_time_school"] == 12.5
    assert blocks["B002"]["service_capacity_school"] == 340
    assert blocks["B001"]["residential"] == 1.0
    assert blocks["B002"]["business"] == 0.5


def test_polygon_services_keep_geometry(tmp_path):
    services = tmp_path / "services"
    services.mkdir()
    gpd.GeoDataFrame(
        {"name": ["Парк"]},
        geometry=[box(0.01, 0.01, 0.02, 0.02)],
        crs=4326,
    ).to_file(services / "service_park.geojson", driver="GeoJSON")

    payload = _services_payload(services)
    park = next(service for service in payload if service["id"] == "park")
    assert park["polygon"] is True
    assert park["geometry"] == "polygon"
    assert park["geojson"]["features"][0]["geometry"]["type"] == "Polygon"
