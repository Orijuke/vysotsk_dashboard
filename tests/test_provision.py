import numpy as np
import pandas as pd
import pytest

from my_package.provision import probabilistic_provision


def _matrix(times):
    index = list(range(len(times)))
    return pd.DataFrame(times, index=index, columns=index, dtype=float)


def test_probabilistic_provision_uses_distance_decay():
    blocks = pd.DataFrame({"population": [1000, 0], "capacity": [0, 100]}, index=[0, 1])
    result = probabilistic_provision(blocks, _matrix([[0, 10], [10, 0]]), 10, 100)

    assert result.loc[0, "demand"] == 100
    assert result.loc[0, "access_time"] == 10
    assert result.loc[0, "provision_weak"] == pytest.approx(0.5 ** (10 / 7.5))
    assert result.loc[0, "demand_within"] == pytest.approx(100 * 0.5 ** (10 / 7.5))


def test_probabilistic_provision_respects_capacity():
    blocks = pd.DataFrame({"population": [1000, 0], "capacity": [0, 10]}, index=[0, 1])
    result = probabilistic_provision(blocks, _matrix([[0, 10], [10, 0]]), 10, 100)

    assert result.loc[0, "demand_within"] == pytest.approx(10)
    assert result.loc[0, "provision_strong"] == pytest.approx(0.1)
    assert result.loc[0, "provision_weak"] == pytest.approx(0.5 ** (10 / 7.5))


def test_probabilistic_provision_prefers_near_large_service():
    blocks = pd.DataFrame(
        {"population": [1000, 0, 0], "capacity": [0, 100, 100]},
        index=[0, 1, 2],
    )
    result = probabilistic_provision(
        blocks,
        _matrix([[0, 5, 15], [5, 0, 20], [15, 20, 0]]),
        10,
        100,
    )

    near_decay = 0.5 ** (5 / 7.5)
    far_decay = 0.5 ** (15 / 7.5)
    assert result.loc[0, "demand_within"] == pytest.approx(100 * near_decay)
    assert result.loc[1, "capacity_within"] > result.loc[2, "capacity_within"]
    assert result.loc[1, "capacity_within"] / result.loc[2, "capacity_within"] == pytest.approx(
        near_decay / far_decay
    )


def test_probabilistic_provision_without_services_returns_missing():
    blocks = pd.DataFrame({"population": [100], "capacity": [0]}, index=[0])
    result = probabilistic_provision(blocks, _matrix([[0]]), 10, 100)

    assert result.loc[0, "demand_within"] == 0
    assert np.isnan(result.loc[0, "access_time"])
    assert np.isnan(result.loc[0, "provision_strong"])
