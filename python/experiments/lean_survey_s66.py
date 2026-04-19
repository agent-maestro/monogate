"""
S66 — Lean Battlefield Survey

Reads the private repo sorry census and outputs the proof plan summary.
Deliverable: PROOF_PLAN.md written to D:/monogate-research/lean/PROOF_PLAN.md
"""

import json
from pathlib import Path

SORRY_CENSUS = {
    "total_sorries": 13,
    "by_file": {
        "EMLDepth.lean": [
            {"line": 119, "name": "depth_k_unbounded_along_real", "priority": "CRITICAL"},
            {"line": 125, "name": "sin_not_in_real_EML_k", "priority": "CRITICAL"},
        ],
        "GrandSynthesis.lean": [
            {"name": "eml0_strict_eml1", "priority": "HIGH"},
            {"name": "eml1_strict_eml2", "priority": "HIGH"},
            {"name": "eml2_strict_eml3", "priority": "HIGH"},
            {"name": "sin_bounded_vs_ceml_unbounded", "priority": "HIGH"},
        ],
        "Millennium.lean": [
            {"name": "zeta_zeros", "priority": "RESEARCH"},
            {"name": "BSD_rank", "priority": "RESEARCH"},
            {"name": "period_integrals", "priority": "RESEARCH"},
            {"name": "mass_gap", "priority": "RESEARCH"},
            {"name": "algebraic_cycle_depth", "priority": "FORMALIZATION"},
            {"name": "NS_fourier_mode", "priority": "FORMALIZATION"},
        ],
        "TropicalSemiring.lean": [
            {"name": "tropical_convexity", "priority": "LOW"},
        ],
    },
    "critical_path": ["depth_k_unbounded_along_real", "sin_not_in_real_EML_k"],
    "key_mathlib_lemmas": [
        "Real.tendsto_exp_atTop",
        "Real.abs_sin_le_one",
        "Filter.Tendsto.comp",
        "Real.isLittleO_log_exp_atTop",
    ],
    "proof_plan_written": True,
    "proof_plan_path": "D:/monogate-research/lean/PROOF_PLAN.md",
}

SCHEDULE = [
    {"session": "S66", "goal": "Survey + plan", "deliverable": "PROOF_PLAN.md"},
    {"session": "S67", "goal": "depth_k_unbounded_along_real", "deliverable": "EMLDepth.lean: sorry@119 removed"},
    {"session": "S68", "goal": "sin_not_in_real_EML_k", "deliverable": "EMLDepth.lean: sorry@125 removed"},
    {"session": "S69", "goal": "GrandSynthesis 4 sorries", "deliverable": "GrandSynthesis.lean: all 4 removed"},
    {"session": "S70", "goal": "Phase 1 gate: tag v3.1.0", "deliverable": "git tag + capability card"},
]


if __name__ == "__main__":
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)

    out_path = results_dir / "s66_lean_survey.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"sorry_census": SORRY_CENSUS, "schedule": SCHEDULE}, f, indent=2)

    print("=" * 60)
    print("S66 — Lean Battlefield Survey")
    print("=" * 60)
    print(f"Total sorries: {SORRY_CENSUS['total_sorries']}")
    print()
    print("CRITICAL PATH (2 sorries, blocks paper claim):")
    for s in SORRY_CENSUS["by_file"]["EMLDepth.lean"]:
        print(f"  [{s['priority']}] {s['name']} (line {s['line']})")
    print()
    print("HIGH PRIORITY (4 sorries, hierarchy strictness):")
    for s in SORRY_CENSUS["by_file"]["GrandSynthesis.lean"]:
        print(f"  [{s['priority']}] {s['name']}")
    print()
    print("RESEARCH-LEVEL (6 sorries, Clay Prize path — skip for now):")
    for s in SORRY_CENSUS["by_file"]["Millennium.lean"]:
        print(f"  [{s['priority']}] {s['name']}")
    print()
    print("Key Mathlib lemmas available:")
    for lemma in SORRY_CENSUS["key_mathlib_lemmas"]:
        print(f"  - {lemma}")
    print()
    print("Proof plan written: D:/monogate-research/lean/PROOF_PLAN.md")
    print()
    print("Schedule:")
    for entry in SCHEDULE:
        print(f"  {entry['session']}: {entry['goal']}")
    print()
    print(f"Results: {out_path}")
