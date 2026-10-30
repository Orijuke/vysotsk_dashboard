import numpy as np
import pandas as pd

from my_package.accessibility import (
    combine_accessibility_matrices,
    combine_distance_series,
)


def test_combine_accessibility_matrices_takes_best_route():
    drive = pd.DataFrame([[0.0, 10.0], [10.0, 0.0]], index=[0, 1], columns=[0, 1])
    walk = pd.DataFrame([[0.0, 4.0], [np.nan, 0.0]], index=[0, 1], columns=[0, 1])

    combined = combine_accessibility_matrices({"drive": drive, "walk": walk})

    assert combined.loc[0, 1] == 4.0
    assert combined.loc[1, 0] == 10.0


def test_combine_accessibility_matrices_skips_empty_inputs():
    drive = pd.DataFrame([[0.0, 10.0], [10.0, 0.0]], index=[0, 1], columns=[0, 1])

    combined = combine_accessibility_matrices(
        {"drive": drive, "walk": pd.DataFrame()}
    )

    pd.testing.assert_frame_equal(combined, drive.astype(float))


def test_combine_distance_series_uses_available_network():
    drive = pd.Series([300.0, np.nan, 900.0], index=[0, 1, 2])
    walk = pd.Series([250.0, 700.0, np.nan], index=[0, 1, 2])

    combined = combine_distance_series({"drive": drive, "walk": walk})

    assert combined.tolist() == [250.0, 700.0, 900.0]
