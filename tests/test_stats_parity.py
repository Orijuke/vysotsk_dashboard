import json
import shutil
import subprocess
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import box

from my_package.dashboard import INDICATOR_SPECS, build_dashboard
from my_package.statistics import compute_statistics


def _results():
    return gpd.GeoDataFrame(
        {
            "block_id": ["B001", "B002", "B003"],
            "population": [100, 0, 30],
            "osr": [1.0, None, 0.5],
            "green_share": [0.2, 0.8, 0.6],
            "green_access_m": [200.0, 800.0, 400.0],
            "green_access_500": [1.0, 0.0, 1.0],
            "land_use": ["LandUse.RESIDENTIAL", "LandUse.RECREATION", "LandUse.RESIDENTIAL"],
            "has_building": [True, False, True],
            "has_population": [True, False, True],
        },
        geometry=[box(0, 0, 0.01, 0.01), box(0.01, 0, 0.02, 0.01), box(0.02, 0, 0.03, 0.01)],
        crs=4326,
    )


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is not installed")
def test_frontend_stats_match_python(tmp_path):
    results_path = tmp_path / "results.geojson"
    _results().to_file(results_path, driver="GeoJSON")
    html_path = build_dashboard(results_path, tmp_path / "dashboard.html", services_dir=tmp_path / "services")

    script = Path(__file__).with_name("stats_parity.js")
    output = subprocess.run(
        ["node", str(script), str(html_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    frontend = json.loads(output.stdout)
    stats = compute_statistics(gpd.read_file(results_path), INDICATOR_SPECS)
    numeric = {item["id"]: item for item in stats["numeric"]}

    assert frontend["blocks"] == stats["meta"]["blocks"]
    assert frontend["built"] == stats["meta"]["built"]
    assert frontend["populated"] == stats["meta"]["populated"]
    assert frontend["population"] == stats["meta"]["population"]
    assert frontend["osr_n"] == numeric["osr"]["n"]
    assert frontend["osr_median"] == pytest.approx(numeric["osr"]["median"])
    assert frontend["green_median"] == pytest.approx(numeric["green_share"]["median"])
    assert frontend["access_median"] == pytest.approx(numeric["green_access_m"]["median"])

    filtered = compute_statistics(
        gpd.read_file(results_path),
        INDICATOR_SPECS,
        [{"field": "green_share", "op": "gte", "value": 0.5}],
    )
    filtered_green = {item["id"]: item for item in filtered["numeric"]}["green_share"]
    assert frontend["filtered_blocks"] == filtered["meta"]["blocks"]
    assert frontend["filtered_green_n"] == filtered_green["n"]
    assert frontend["filtered_green_median"] == pytest.approx(filtered_green["median"])
