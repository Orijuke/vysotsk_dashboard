"""Probabilistic service provision based on distance decay and capacity limits."""

from __future__ import annotations

import numpy as np
import pandas as pd


def probabilistic_provision(  # pylint: disable=too-many-locals,too-many-statements
    blocks_df: pd.DataFrame,
    accessibility_matrix: pd.DataFrame,
    accessibility: float,
    demand: float | None = None,
    *,
    half_life_factor: float = 0.75,
    capacity_limit: bool = True,
) -> pd.DataFrame:
    """Estimate expected service users with a gravity/Huff-style model.

    The probability of using a service decays exponentially with travel time.
    The decay half-life is ``accessibility * half_life_factor``. Service choices
    are weighted by capacity, so a large service attracts more users than a
    small one at the same distance. The final number of users can be limited by
    service capacity.

    Parameters
    ----------
    blocks_df:
        Frame with ``population`` and ``capacity`` columns. An existing
        ``demand`` column takes precedence over ``population``/``demand``.
    accessibility_matrix:
        Square travel-time matrix indexed like ``blocks_df``.
    accessibility:
        Normative travel time in minutes, used to calibrate the decay.
    demand:
        Normative demand per 1000 residents, matching BlocksNet conventions.
    half_life_factor:
        Fraction of the normative time at which use probability halves.
    capacity_limit:
        If True, scale incoming expected users when a service is over capacity.
    """
    index = blocks_df.index
    population = (
        pd.to_numeric(blocks_df["population"], errors="coerce").fillna(0.0)
        if "population" in blocks_df.columns
        else pd.Series(0.0, index=index)
    )
    capacity = (
        pd.to_numeric(blocks_df["capacity"], errors="coerce").fillna(0.0)
        if "capacity" in blocks_df.columns
        else pd.Series(0.0, index=index)
    )
    capacity = capacity.clip(lower=0.0)

    if "demand" in blocks_df.columns:
        total_demand = pd.to_numeric(blocks_df["demand"], errors="coerce").fillna(0.0)
    else:
        if demand is None:
            raise ValueError("demand is required when blocks_df has no demand column")
        total_demand = np.ceil(population / 1000.0 * float(demand)).astype(float)

    matrix = accessibility_matrix.reindex(index=index, columns=index).astype(float)
    service_index = capacity[capacity > 0].index

    columns = [
        "demand",
        "demand_expected",
        "demand_within",
        "demand_without",
        "capacity",
        "capacity_within",
        "capacity_without",
        "access_time",
        "provision_strong",
        "provision_weak",
    ]
    if service_index.empty:
        result = pd.DataFrame(0.0, index=index, columns=columns)
        result["access_time"] = np.nan
        result["provision_strong"] = np.nan
        result["provision_weak"] = np.nan
        result["capacity"] = capacity
        result["demand"] = total_demand
        result["demand_expected"] = 0.0
        return result

    half_life = max(float(accessibility) * float(half_life_factor), 1e-9)
    times = matrix.loc[:, service_index]
    decay = np.power(0.5, times / half_life)
    nearest_time = times.min(axis=1)
    participation = np.power(0.5, nearest_time / half_life).clip(0.0, 1.0)
    expected = total_demand * participation

    weights = decay.to_numpy(dtype=float) * capacity.loc[service_index].to_numpy(dtype=float)
    weight_sums = weights.sum(axis=1)
    shares = np.divide(
        weights,
        weight_sums[:, None],
        out=np.zeros_like(weights),
        where=weight_sums[:, None] > 0,
    )

    service_load = shares.T @ expected.to_numpy(dtype=float)
    service_capacity = capacity.loc[service_index].to_numpy(dtype=float)
    if capacity_limit:
        served_by_service = np.minimum(service_load, service_capacity)
    else:
        served_by_service = service_load
    scale = np.divide(
        served_by_service,
        service_load,
        out=np.ones_like(service_load),
        where=service_load > 0,
    )
    links = shares * expected.to_numpy(dtype=float)[:, None] * scale[None, :]
    served = pd.Series(links.sum(axis=1), index=index)

    result = pd.DataFrame(index=index)
    result["demand"] = total_demand
    result["demand_expected"] = expected
    result["demand_within"] = served
    result["demand_without"] = expected - served
    result["capacity"] = capacity
    result["capacity_within"] = pd.Series(served_by_service, index=service_index).reindex(index).fillna(0.0)
    result["capacity_without"] = capacity - result["capacity_within"]
    result["access_time"] = nearest_time
    result["provision_strong"] = _ratio(served, total_demand)
    result["provision_weak"] = _ratio(expected, total_demand)
    return result


def _ratio(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    values = np.asarray(numerator, dtype=float)
    totals = np.asarray(denominator, dtype=float)
    result = np.full(values.shape, np.nan, dtype=float)
    mask = totals > 0
    result[mask] = values[mask] / totals[mask]
    result[~np.isfinite(result)] = np.nan
    return pd.Series(result, index=numerator.index)
