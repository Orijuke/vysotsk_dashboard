"""Utilities for combining accessibility results from several networks."""

# pylint: disable=import-outside-toplevel

from __future__ import annotations

from collections.abc import Mapping

import geopandas as gpd
import numpy as np
import pandas as pd


def combine_accessibility_matrices(
    matrices: Mapping[str, pd.DataFrame],
) -> pd.DataFrame:
    """Return an element-wise minimum of accessibility matrices.

    Each matrix describes travel distances within one network (for example,
    ``drive`` and ``walk``). The minimum is the best available route between
    two blocks when any of the networks can be used.
    """
    frames = [
        matrix
        for matrix in matrices.values()
        if matrix is not None and not matrix.empty
    ]
    if not frames:
        raise ValueError("At least one non-empty accessibility matrix is required")

    combined = frames[0].copy()
    for frame in frames[1:]:
        frame = frame.reindex(index=combined.index, columns=combined.columns)
        combined = combined.combine(frame, np.fmin)
    return combined.astype(float)


def combine_distance_series(
    distances: Mapping[str, pd.Series],
) -> pd.Series:
    """Return the best (minimum) distance per object across networks."""
    series_list = [
        series
        for series in distances.values()
        if series is not None and not series.empty
    ]
    if not series_list:
        raise ValueError("At least one non-empty distance series is required")

    combined = series_list[0].copy()
    for series in series_list[1:]:
        combined = combined.combine(series.reindex(combined.index), np.fmin)
    return combined.astype(float)


def boundary_snap_points(
    blocks: gpd.GeoDataFrame,
    graph: object,
    *,
    step: float = 25.0,
) -> tuple[gpd.GeoDataFrame, pd.Series]:
    """Return block boundary points closest to the road graph.

    A block representative point can fall far from a road in large or elongated
    quarters. Sampling the boundary makes the connector to the graph shorter
    and more realistic.
    """
    import iduedu as ie

    if blocks.crs is None:
        raise ValueError("Blocks must have a CRS to snap them to the graph")

    block_indices: list[object] = []
    points: list[object] = []
    for index, geometry in blocks.geometry.items():
        if geometry is None or geometry.is_empty:
            continue
        for point in _boundary_samples(geometry, step):
            block_indices.append(index)
            points.append(point)
        block_indices.append(index)
        points.append(geometry.representative_point())

    if not points:
        empty = gpd.GeoDataFrame(geometry=[], index=blocks.index, crs=blocks.crs)
        return empty, pd.Series(np.nan, index=blocks.index)

    samples = gpd.GeoDataFrame(
        {"block_index": block_indices},
        geometry=points,
        crs=blocks.crs,
    )
    _, distances = ie.get_closest_nodes(samples, graph)
    samples["snap_distance"] = np.asarray(distances, dtype=float)
    best = (
        samples.sort_values("snap_distance")
        .drop_duplicates("block_index")
        .set_index("block_index")
        .reindex(blocks.index)
    )
    missing = best.geometry.isna()
    if missing.any():
        best.loc[missing, "geometry"] = blocks.loc[missing].geometry.representative_point()

    snapped = gpd.GeoDataFrame(
        geometry=best.geometry.to_numpy(),
        index=blocks.index,
        crs=blocks.crs,
    )
    return snapped, pd.Series(best["snap_distance"].to_numpy(dtype=float), index=blocks.index)


def calculate_boundary_accessibility_matrix(
    blocks: gpd.GeoDataFrame,
    graph: object,
    *,
    weight_key: str = "length_meter",
    step: float = 25.0,
) -> tuple[pd.DataFrame, pd.Series]:
    """Calculate a travel-time matrix using boundary points nearest to the graph."""
    import iduedu as ie

    points, snap_distances = boundary_snap_points(blocks, graph, step=step)
    matrix = ie.get_adj_matrix_gdf_to_gdf(
        points,
        points,
        graph,
        weight_key,
        dtype=np.float32,
    )
    return matrix.astype(float), snap_distances


def _boundary_samples(geometry: object, step: float) -> list[object]:
    boundary = geometry.boundary
    if boundary is None or boundary.is_empty:
        return []
    parts = list(boundary.geoms) if hasattr(boundary, "geoms") else [boundary]
    samples: list[object] = []
    for part in parts:
        length = float(part.length)
        if not np.isfinite(length) or length <= 0:
            continue
        positions = np.arange(0.0, length, max(step, 1.0))
        samples.extend(part.interpolate(float(position)) for position in positions)
        samples.append(part.interpolate(length))
    return samples
