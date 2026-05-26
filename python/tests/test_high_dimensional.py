from monogate.high_dimensional import (
    hypersphere_cube_ratio,
    run_corner_concentration_probe,
)


def test_hypersphere_cube_ratio_collapses():
    assert hypersphere_cube_ratio(2) > hypersphere_cube_ratio(8)
    assert hypersphere_cube_ratio(8) > hypersphere_cube_ratio(32)


def test_corner_concentration_probe_boundaries():
    packet = run_corner_concentration_probe(depths=[1, 3, 5], samples=200, seed=7)
    rows = packet["rows"]

    assert packet["schema_version"] == "monogate.high_dim_corner_concentration.v1"
    assert packet["boundaries"]["sampled_evidence_only"] is True
    assert packet["boundaries"]["phantom_attractor_proof"] is False
    assert rows[-1]["boundary_shell_fraction"] > rows[0]["boundary_shell_fraction"]
    assert rows[-1]["hypersphere_cube_ratio"] < rows[0]["hypersphere_cube_ratio"]
    assert 0 <= rows[-1]["useful_volume_proxy"] <= 1
