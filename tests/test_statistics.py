import json

import numpy as np
import pandas as pd

from my_package.statistics import apply_filters, build_statistics_payload, compute_statistics


SPECS = [
    {"id": "population", "kind": "numeric", "label": "Население", "decimals": 0, "format": "number", "unit": "чел."},
    {"id": "osr", "kind": "numeric", "label": "OSR", "decimals": 2, "format": "number", "unit": ""},
    {"id": "green_share", "kind": "numeric", "label": "Зелень", "decimals": 0, "format": "percent", "unit": ""},
    {
        "id": "land_use",
        "kind": "categorical",
        "label": "Землепользование",
        "labels": {"residential": "Жилая", "recreation": "Рекреация"},
    },
]


def _frame():
    return pd.DataFrame(
        {
            "population": [100, 0, 50, 0, 0, 10],
            "osr": [1.0, np.inf, 0.5, np.inf, np.inf, 2.0],
            "green_share": [0.8, 0.2, 0.6, 0.4, 0.0, 0.9],
            "land_use": ["residential", "recreation", "residential", "recreation", "recreation", "residential"],
        }
    )


def test_apply_filters_combines_conditions():
    filtered = apply_filters(
        _frame(),
        [
            {"field": "population", "op": "gt", "value": 0},
            {"field": "green_share", "op": "between", "value": [0.5, 1.0]},
        ],
    )
    assert filtered.index.tolist() == [0, 2, 5]


def test_numeric_and_categorical_summary():
    stats = compute_statistics(_frame(), SPECS)
    numeric = {item["id"]: item for item in stats["numeric"]}
    categorical = {item["id"]: item for item in stats["categorical"]}

    assert stats["meta"] == {
        "blocks": 6,
        "built": 3,
        "populated": 3,
        "population": 160,
        "filters": [],
    }
    assert numeric["osr"]["n"] == 3
    assert numeric["osr"]["missing"] == 3
    assert numeric["osr"]["median"] == 1.0
    assert numeric["green_share"]["median"] == 0.5
    assert numeric["green_share"]["reliable"] is True
    assert categorical["land_use"]["categories"][0]["value"] == "residential"
    assert categorical["land_use"]["categories"][0]["label"] == "Жилая"


def test_small_groups_are_flagged():
    stats = compute_statistics(_frame().head(4), SPECS)
    numeric = {item["id"]: item for item in stats["numeric"]}
    assert numeric["osr"]["n"] == 2
    assert numeric["osr"]["reliable"] is False


def test_payload_is_json_safe_and_has_methods():
    payload = build_statistics_payload(_frame(), SPECS)
    serialized = json.dumps(payload, ensure_ascii=False, allow_nan=False)
    assert "green_share" in serialized
    assert payload["methods"]
    assert payload["disclaimer"]
    assert payload["fields"]
    assert payload["baseline"]["meta"]["blocks"] == 6
