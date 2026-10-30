"""Statistics for block-level urban indicators and dashboard filters."""

from __future__ import annotations

import math
from typing import Any, Iterable

import numpy as np
import pandas as pd


NUMERIC_OPERATORS = ("eq", "ne", "gt", "gte", "lt", "lte", "between")
CATEGORICAL_OPERATORS = ("eq", "ne", "contains")
BOOLEAN_OPERATORS = ("eq",)


def _number(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _json_number(value: Any) -> float | None:
    return _number(value)


def _mask_for_filter(  # pylint: disable=too-many-return-statements
    frame: pd.DataFrame, item: dict[str, Any]
) -> pd.Series:
    field = str(item.get("field", ""))
    operator = str(item.get("op", "eq"))
    value = item.get("value")
    if field not in frame.columns:
        return pd.Series(False, index=frame.index)

    series = frame[field]
    if operator in ("gt", "gte", "lt", "lte", "between"):
        numeric = pd.to_numeric(series, errors="coerce")
        if operator == "between":
            if not isinstance(value, (list, tuple)) or len(value) != 2:
                return pd.Series(False, index=frame.index)
            low, high = _number(value[0]), _number(value[1])
            if low is None or high is None:
                return pd.Series(False, index=frame.index)
            low, high = min(low, high), max(low, high)
            return numeric.between(low, high, inclusive="both")
        target = _number(value)
        if target is None:
            return pd.Series(False, index=frame.index)
        if operator == "gt":
            return numeric > target
        if operator == "gte":
            return numeric >= target
        if operator == "lt":
            return numeric < target
        return numeric <= target

    if operator == "contains":
        needle = str(value or "").strip().lower()
        return series.fillna("").astype(str).str.lower().str.contains(needle, regex=False)

    if operator == "ne":
        return series.astype(str) != str(value)

    return series.astype(str) == str(value)


def apply_filters(frame: pd.DataFrame, filters: Iterable[dict[str, Any]] | None = None) -> pd.DataFrame:
    """Return rows matching all filters."""
    filtered = frame
    for item in filters or []:
        filtered = filtered[_mask_for_filter(filtered, item)]
    return filtered


def _numeric_summary(series: pd.Series, spec: dict[str, Any]) -> dict[str, Any]:
    numeric = pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan)
    clean = numeric.dropna()
    size = int(clean.size)
    result: dict[str, Any] = {
        "id": spec["id"],
        "label": spec.get("label", spec["id"]),
        "unit": spec.get("unit", ""),
        "decimals": int(spec.get("decimals", 0)),
        "format": spec.get("format", "number"),
        "n": size,
        "missing": int(numeric.isna().sum()),
        "reliable": size >= 5,
    }
    if not size:
        result.update({"mean": None, "median": None, "min": None, "max": None, "q1": None, "q3": None, "sum": None})
        return result
    result.update(
        {
            "mean": _json_number(clean.mean()),
            "median": _json_number(clean.median()),
            "min": _json_number(clean.min()),
            "max": _json_number(clean.max()),
            "q1": _json_number(clean.quantile(0.25)),
            "q3": _json_number(clean.quantile(0.75)),
            "sum": _json_number(clean.sum()),
        }
    )
    return result


def _categorical_summary(series: pd.Series, spec: dict[str, Any]) -> dict[str, Any]:
    raw = series.map(lambda value: None if pd.isna(value) else str(value))
    counts = raw.value_counts(dropna=True)
    total = int(len(raw))
    labels = spec.get("labels", {})
    categories = [
        {
            "value": str(value),
            "label": str(labels.get(str(value), value)),
            "count": int(count),
            "share": float(count / total) if total else 0.0,
        }
        for value, count in counts.items()
    ]
    missing = total - int(counts.sum())
    return {
        "id": spec["id"],
        "label": spec.get("label", spec["id"]),
        "n": total - missing,
        "missing": missing,
        "reliable": total - missing >= 5,
        "categories": categories,
    }


def _share(mask: pd.Series, eligible: pd.Series) -> float | None:
    denominator = int(eligible.fillna(False).sum())
    if denominator < 5:
        return None
    return float(int((mask & eligible).fillna(False).sum()) / denominator)


def _numeric_series(frame: pd.DataFrame, field: str) -> pd.Series:
    if field not in frame.columns:
        return pd.Series(np.nan, index=frame.index, dtype=float)
    return pd.to_numeric(frame[field], errors="coerce").replace([np.inf, -np.inf], np.nan)


def _spearman(frame: pd.DataFrame, left: str, right: str, eligible: pd.Series) -> dict[str, Any] | None:
    pair = pd.DataFrame(
        {
            "left": _numeric_series(frame, left),
            "right": _numeric_series(frame, right),
        }
    )
    pair = pair[eligible.fillna(False)].dropna()
    if len(pair) < 5:
        return None
    return {
        "left": left,
        "right": right,
        "n": int(len(pair)),
        "rho": _json_number(pair["left"].rank().corr(pair["right"].rank())),
    }


def _insights(frame: pd.DataFrame) -> list[str]:  # pylint: disable=too-many-locals
    insights: list[str] = []
    population = _numeric_series(frame, "population").fillna(0.0)
    populated = population > 0
    built = _numeric_series(frame, "osr").notna()

    green = _numeric_series(frame, "green_share")
    if green.notna().sum() >= 5:
        share_green = float((green >= 0.5).fillna(False).mean())
        insights.append(
            f"Доля кварталов с green_share ≥ 0,5: {share_green * 100:.0f}% " f"(n={int(green.notna().sum())})."
        )

    access = _numeric_series(frame, "green_access_m")
    if access.notna().sum() >= 5:
        within = float((access <= 500).fillna(False).mean())
        insights.append(
            f"Медианный доступ к публичной зелени по дорожной сети: "
            f"{access.median():.0f} м; в пределах 500 м — {within * 100:.0f}% кварталов."
        )

    osr = _numeric_series(frame, "osr").loc[built]
    if len(osr) >= 5:
        insights.append(
            f"Медианная открытость застройки (OSR): {osr.median():.2f} " f"(n={len(osr)} кварталов с застройкой)."
        )

    for service_id, label in (("grocery", "магазинами"), ("parks", "парками")):
        provision = _numeric_series(frame, f"provision_strong_{service_id}")
        eligible = populated & provision.notna()
        if int(eligible.sum()) >= 5:
            covered = float((provision >= 0.999999).loc[eligible].mean())
            insights.append(
                f"Полная обеспеченность {label}: {covered * 100:.0f}% "
                f"(n={int(eligible.sum())} кварталов с населением)."
            )
    for universe, mask in (("с застройкой", built), ("с населением", populated)):
        correlation = _spearman(frame, "osr", "green_share", mask)
        if correlation is not None:
            insights.append(
                f"Spearman OSR ↔ green_share, {universe}: ρ={correlation['rho']:.3f} " f"(n={correlation['n']})."
            )

    return insights


def _field_metadata(frame: pd.DataFrame, specs: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    fields: list[dict[str, Any]] = []
    for spec in specs:
        field = spec.get("id")
        if not field or field not in frame.columns:
            continue
        item = {
            "id": field,
            "label": spec.get("label", field),
            "kind": spec.get("kind", "numeric"),
            "unit": spec.get("unit", ""),
            "decimals": int(spec.get("decimals", 0)),
            "format": spec.get("format", "number"),
        }
        if item["kind"] == "categorical":
            item["labels"] = spec.get("labels", {})
            item["categories"] = [
                str(value) for value in frame[field].dropna().astype(str).value_counts().index.tolist()
            ]
        fields.append(item)
    for field, label in (("has_building", "Только с застройкой"), ("has_population", "Только с населением")):
        if field in frame.columns:
            fields.append(
                {
                    "id": field,
                    "label": label,
                    "kind": "boolean",
                    "unit": "",
                    "decimals": 0,
                    "format": "boolean",
                }
            )
    return fields


def compute_statistics(
    frame: pd.DataFrame,
    specs: Iterable[dict[str, Any]],
    filters: Iterable[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Compute a JSON-ready statistics block for the selected filters."""
    specs = list(specs)
    filtered = apply_filters(frame, filters)
    population = _numeric_series(filtered, "population").fillna(0.0)
    built = _numeric_series(filtered, "osr").notna()
    populated = population > 0

    numeric = [
        _numeric_summary(filtered[spec["id"]], spec)
        for spec in specs
        if spec.get("kind", "numeric") == "numeric" and spec.get("id") in filtered.columns
    ]
    categorical = [
        _categorical_summary(filtered[spec["id"]], spec)
        for spec in specs
        if spec.get("kind") == "categorical" and spec.get("id") in filtered.columns
    ]

    return {
        "meta": {
            "blocks": int(len(filtered)),
            "built": int(built.sum()),
            "populated": int(populated.sum()),
            "population": int(population.sum()),
            "filters": list(filters or []),
        },
        "numeric": numeric,
        "categorical": categorical,
        "insights": _insights(filtered),
    }


def build_statistics_payload(
    frame: pd.DataFrame,
    specs: Iterable[dict[str, Any]],
    filters: Iterable[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build baseline statistics and field metadata for the dashboard."""
    specs = list(specs)
    baseline = compute_statistics(frame, specs, filters)
    return {
        "fields": _field_metadata(frame, specs),
        "baseline": baseline,
        "methods": [
            "Показатели рассчитаны по кварталам, а не по отдельным зданиям.",
            "Пропуски исключаются из расчёта средних и медиан; n указан для каждой метрики.",
            "Группы с n < 5 помечаются как недостаточные для устойчивых выводов.",
            "Доступ к зелени рассчитан по существующему дорожному графу "
            "до park и публичных озеленённых территорий landuse.",
            "OSR — открытость застройки, а не доля озеленения.",
        ],
        "disclaimer": (
            "Материал носит аналитический характер. Показатели зависят от полноты OpenStreetMap, "
            "модели населения и импутации ёмкости сервисов; их нельзя использовать как официальную статистику."
        ),
    }
