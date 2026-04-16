"""Tests for monogate.frontiers.attractor_identity."""
import pytest


def test_constants_has_enough_entries():
    """CONSTANTS dict must have at least 50 entries."""
    from monogate.frontiers.attractor_identity import CONSTANTS

    assert len(CONSTANTS) >= 50, (
        f"CONSTANTS has only {len(CONSTANTS)} entries — expected >= 50"
    )


def test_search_constants_finds_pi():
    """search_constants at tolerance 1e-3 should find 'pi' near pi."""
    pytest.importorskip("mpmath", reason="mpmath required for attractor tests")

    import mpmath
    from monogate.frontiers.attractor_identity import search_constants

    attractor = str(mpmath.pi)
    matches, top20 = search_constants(attractor, tolerance=1e-3)

    # 'pi' must appear somewhere in matches or top 20
    # Items are 3-tuples: (name, value, distance)
    all_names = {name for name, *_ in matches} | {name for name, *_ in top20}
    assert "pi" in all_names, (
        f"'pi' not found near pi. matches={matches[:3]}, top20={top20[:3]}"
    )
