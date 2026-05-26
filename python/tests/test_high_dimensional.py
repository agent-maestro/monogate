from monogate.high_dimensional import (
    hypersphere_cube_ratio,
    run_forge_attractor_trace_packet,
    run_corner_concentration_probe,
    run_optimizer_trace,
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


def test_optimizer_trace_packet_has_regime_labels():
    trace = run_optimizer_trace(regime="guarded_gradient", depth=2, steps=8, seed=11)

    assert trace["schema_version"] == "monogate.forge_attractor_trace.v1"
    assert trace["trace"]["regime"] == "guarded_gradient"
    assert trace["trace"]["final_label"] in {
        "converged",
        "transient",
        "collapsed",
        "domain_failed",
        "overflowed",
        "saturated",
    }
    assert trace["boundaries"]["optimizer_release_claim"] is False


def test_forge_attractor_trace_packet_compares_regimes():
    packet = run_forge_attractor_trace_packet(depth=2, steps=8, seed=13)
    regimes = {row["regime"] for row in packet["summary"]}

    assert packet["schema_version"] == "monogate.forge_attractor_trace_packet.v1"
    assert regimes == {
        "naive_gradient",
        "regularized_gradient",
        "guarded_gradient",
        "boundary_aware_gradient",
        "random_search",
    }
    assert packet["boundaries"]["formal_verification_claim"] is False
    assert len(packet["machlib_lean_obligations"]) >= 3
