#!/usr/bin/env python3
"""Private EML expression packet builder.

Input: expression metadata packet.
Output: EML IR, replay summary, Evidence Packet v0, and a short report.

This is EML-R2/R6/R7/R8-R14 plumbing. It does not change Forge/compiler
behavior and does not create public savings, formal verification, or hardware
claims.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_ir_pipeline import build_ir, validate_ir  # noqa: E402

DATE = "2026-05-27"
SCHEMA_VERSION = "monogate.eml_expression_packet.v0"
RESULT_SCHEMA_VERSION = "monogate.eml_packet_builder.result.v0"
PROOF_STATUS_SCHEMA_VERSION = "monogate.eml_proof_status_manifest.v0"
OBLIGATION_REGISTRY_SCHEMA_VERSION = "monogate.eml_proof_obligation_registry.v0"
FORBIDDEN_TRUE_FLAGS = [
    "public_ready",
    "public_savings_claim",
    "hardware_observed",
    "live_serial_capture_performed",
    "certified_safety_claim",
    "production_controller_claim",
    "formal_verification_claim",
    "theorem_proof_claim",
    "compiler_behavior_changed",
    "forge_behavior_changed",
]
DEFAULT_CLAIM_FLAGS = {key: False for key in FORBIDDEN_TRUE_FLAGS}


def artifact_id(program_id: str) -> str:
    return program_id.replace("_", "-")


def _edges(nodes: list[dict[str, Any]]) -> list[dict[str, str]]:
    edges = []
    for node in nodes:
        op = node.get("op") or "input"
        for arg in node.get("args", []):
            edges.append({"from": arg, "to": node["id"], "op": op})
    return edges


def _timeline(frames: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for frame in frames:
        kernel = frame["kernel_id"]
        if frame["lifecycle_state"] == "INIT":
            what = "The EML expression packet enters the local IR runtime."
        elif frame["lifecycle_state"] == "READY":
            what = "Stable DAG node identifiers are assigned."
        elif kernel == "div":
            what = "A division node is replayed with a domain annotation, not a proof."
        elif frame["lifecycle_state"] == "END":
            what = "The output node is reached."
        elif frame["lifecycle_state"] == "PARKED":
            what = "The replay packet parks at the terminal boundary."
        else:
            what = f"The {kernel} node replays as a static expression step."
        out.append(
            {
                "frame_id": frame["frame_id"],
                "tick": frame["monotonic_tick"],
                "state": frame["lifecycle_state"],
                "kernel_id": kernel,
                "guard_action": frame["guard_action"],
                "guard_reason": frame["guard_reason"],
                "replay_hash": frame["replay_hash"],
                "what_happened": what,
            }
        )
    return out


def _load_proof_statuses(program_id: str, proof_status_dir: Path | None) -> dict[str, dict[str, Any]]:
    if proof_status_dir is None or not proof_status_dir.exists():
        return {}
    statuses: dict[str, dict[str, Any]] = {}
    for path in sorted(proof_status_dir.glob(f"{program_id}*_proof_status_*.json")):
        manifest = json.loads(path.read_text(encoding="utf-8"))
        if manifest.get("schemaVersion") != PROOF_STATUS_SCHEMA_VERSION:
            raise ValueError(f"invalid proof status schema in {path}")
        if manifest.get("programId") != program_id:
            raise ValueError(f"proof status program mismatch in {path}")
        for item in manifest.get("obligations", []):
            obligation_id = item.get("obligationId")
            if not isinstance(obligation_id, str) or not obligation_id:
                raise ValueError(f"invalid obligationId in {path}")
            statuses[obligation_id] = {**item, "manifestPath": str(path)}
    return statuses


def _apply_proof_status(card: dict[str, Any], proof_statuses: dict[str, dict[str, Any]]) -> dict[str, Any]:
    proof_status = proof_statuses.get(card["obligationId"])
    if proof_status is None:
        return card
    if proof_status.get("status") != "checked_small_witness":
        raise ValueError(f"unsupported proof status for {card['obligationId']}: {proof_status.get('status')}")
    return {
        **card,
        "status": "checked_small_witness",
        "checkedBy": proof_status["checkedBy"],
        "proofArtifact": proof_status["proofArtifact"],
        "proofSummary": proof_status["proofSummary"],
        "nonClaim": proof_status["nonClaim"],
    }


def _build_obligations(
    packet: dict[str, Any],
    ir: dict[str, Any],
    proof_statuses: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    obligations: list[dict[str, Any]] = []
    program_id = packet["program_id"]
    for node in ir["nodes"]:
        op = node.get("op")
        if op == "div":
            obligations.append(
                {
                    "obligationId": f"{program_id}:domain:{node['id']}:div-denominator-nonzero",
                    "kind": "domain",
                    "status": "candidate_only",
                    "trigger": "div",
                    "nodeId": node["id"],
                    "description": "Division node requires evidence that the denominator is not zero over declared inputs/ranges.",
                    "proofTarget": "denominator_nonzero",
                    "nonClaim": "This card records a proof obligation; it does not prove the denominator condition.",
                }
            )
        elif op == "ln":
            obligations.append(
                {
                    "obligationId": f"{program_id}:domain:{node['id']}:ln-argument-positive",
                    "kind": "domain",
                    "status": "candidate_only",
                    "trigger": "ln",
                    "nodeId": node["id"],
                    "description": "Log node requires evidence that its argument is positive over declared inputs/ranges.",
                    "proofTarget": "log_argument_positive",
                    "nonClaim": "This card records a proof obligation; it does not prove positivity.",
                }
            )
        elif op == "sqrt":
            obligations.append(
                {
                    "obligationId": f"{program_id}:domain:{node['id']}:sqrt-argument-nonnegative",
                    "kind": "domain",
                    "status": "candidate_only",
                    "trigger": "sqrt",
                    "nodeId": node["id"],
                    "description": "Square-root node requires evidence that its argument is nonnegative over declared inputs/ranges.",
                    "proofTarget": "sqrt_argument_nonnegative",
                    "nonClaim": "This card records a proof obligation; it does not prove nonnegativity.",
                }
            )
    for name, bounds in sorted(packet.get("safe_ranges", {}).items()):
        obligations.append(
            {
                "obligationId": f"{program_id}:range:{name}:declared-safe-range",
                "kind": "range_safety",
                "status": "candidate_only",
                "trigger": "safe_range",
                "input": name,
                "description": f"Input {name} declares range [{bounds['min']}, {bounds['max']}]; downstream runtime or proof work must preserve this boundary.",
                "proofTarget": "input_range_respected",
                "nonClaim": "This card records a declared range boundary; it is not hardware evidence or a certified safety proof.",
            }
        )
    statuses = proof_statuses or {}
    return [_apply_proof_status(card, statuses) for card in obligations]


def _domain_requirement_for_card(card: dict[str, Any]) -> dict[str, Any] | None:
    if card["kind"] != "domain":
        return None
    if card["trigger"] == "div":
        requirement = "denominator_nonzero"
        blocker = "division denominator may be zero"
        rewrite = "Introduce a guard or range proof before division."
    elif card["trigger"] == "ln":
        requirement = "argument_positive"
        blocker = "log argument may be nonpositive"
        rewrite = "Introduce log-domain lift, positivity guard, or range proof."
    elif card["trigger"] == "sqrt":
        requirement = "argument_nonnegative"
        blocker = "sqrt argument may be negative"
        rewrite = "Introduce nonnegative clamp, square-domain guard, or range proof."
    else:
        requirement = "unknown_domain_requirement"
        blocker = "domain requirement unresolved"
        rewrite = "Add a domain-specific guard or proof."
    return {
        "requirementId": card["obligationId"],
        "nodeId": card.get("nodeId"),
        "trigger": card["trigger"],
        "requirement": requirement,
        "status": card["status"] if card["status"] == "checked_small_witness" else "unresolved",
        "blockedPublicClaim": blocker,
        "possibleSafeRewrite": rewrite,
        "checkedBy": card.get("checkedBy"),
        "proofArtifact": card.get("proofArtifact"),
        "proofSummary": card.get("proofSummary"),
    }


def _build_domain_safety(packet: dict[str, Any], obligations: list[dict[str, Any]]) -> dict[str, Any]:
    domain_requirements = [
        requirement
        for card in obligations
        for requirement in [_domain_requirement_for_card(card)]
        if requirement is not None
    ]
    range_assumptions = [
        {
            "input": name,
            "min": bounds["min"],
            "max": bounds["max"],
            "status": "declared_unverified",
            "blockedPublicClaim": "declared range is not runtime, hardware, or proof evidence",
            "possibleSafeRewrite": "Attach runtime guard, sampled replay evidence, or MachLib range proof before promotion.",
        }
        for name, bounds in sorted(packet.get("safe_ranges", {}).items())
    ]
    unresolved = [
        {
            "obligationId": card["obligationId"],
            "kind": card["kind"],
            "proofTarget": card["proofTarget"],
            "reason": card["nonClaim"],
        }
        for card in obligations
        if card["status"] != "checked_small_witness"
    ]
    checked = [
        {
            "obligationId": card["obligationId"],
            "kind": card["kind"],
            "proofTarget": card["proofTarget"],
            "checkedBy": card.get("checkedBy"),
            "proofArtifact": card.get("proofArtifact"),
            "proofSummary": card.get("proofSummary"),
        }
        for card in obligations
        if card["status"] == "checked_small_witness"
    ]
    blocked_public_claims = [
        "public_savings_claim",
        "formal_verification_claim",
        "theorem_proof_claim",
        "hardware_observed",
        "certified_safety_claim",
        "production_controller_claim",
    ]
    if any(item["status"] != "checked_small_witness" for item in domain_requirements):
        blocked_public_claims.append("total_domain_safety_claim")
    if range_assumptions:
        blocked_public_claims.append("range_safety_proved_claim")
    return {
        "schemaVersion": "monogate.eml_domain_safety_lens.v0",
        "status": "candidate_only",
        "domainRequirements": domain_requirements,
        "rangeAssumptions": range_assumptions,
        "unresolvedObligations": unresolved,
        "checkedObligations": checked,
        "possibleSafeRewrites": [
            item["possibleSafeRewrite"]
            for item in [*domain_requirements, *range_assumptions]
        ],
        "blockedPublicClaims": sorted(set(blocked_public_claims)),
        "summary": {
            "domain_requirement_count": len(domain_requirements),
            "range_assumption_count": len(range_assumptions),
            "unresolved_obligation_count": len(unresolved),
            "checked_obligation_count": len(checked),
            "checked_domain_requirement_count": sum(
                1 for item in domain_requirements if item["status"] == "checked_small_witness"
            ),
            "safe_rewrite_candidate_count": len(domain_requirements) + len(range_assumptions),
            "blocked_public_claim_count": len(set(blocked_public_claims)),
            "proved_count": len(checked),
        },
        "nonClaims": [
            "The domain safety lens is deterministic classification, not proof.",
            "Safe rewrite suggestions are candidates, not compiler behavior changes.",
            "Range assumptions are declared metadata, not hardware observations.",
        ],
    }


def _build_safe_rewrite_proposals(result: dict[str, Any]) -> list[dict[str, Any]]:
    proposals = []
    for requirement in result["domainSafety"]["domainRequirements"]:
        if requirement["status"] != "checked_small_witness":
            continue
        proposals.append(
            {
                "proposalId": f"{result['sourcePacket']['program_id']}:{requirement['trigger']}:checked-domain-rewrite",
                "status": "candidate_no_compiler_change",
                "nodeId": requirement.get("nodeId"),
                "requirementId": requirement["requirementId"],
                "proposal": f"Mark this {requirement['requirement']} guard as proof-backed in review surfaces.",
                "blockedAction": "Do not change compiler lowering or public savings claims from this witness alone.",
                "proofArtifact": requirement.get("proofArtifact"),
            }
        )
    return proposals


def _lean_name(text: str) -> str:
    parts = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").split("_")
    if not parts:
        return "eml_obligation"
    first = parts[0].lower()
    rest = [part[:1].upper() + part[1:] for part in parts[1:]]
    return first + "".join(rest)


def _build_machlib_stub_text(result: dict[str, Any]) -> str:
    packet = result["sourcePacket"]
    lines = [
        f"-- EML-R7 MachLib obligation stubs for {packet['program_id']}",
        "-- Candidate-only artifact generated from EML packet obligations.",
        "-- This file contains no proofs and makes no theorem/proof claim.",
        "",
        "namespace Monogate",
        "namespace EML",
        "namespace GeneratedObligations",
        "",
        f"-- Source expression: {packet['expression']}",
        "",
    ]
    cards = result["obligations"]["cards"]
    if not cards:
        lines.append("-- No obligation cards were generated for this packet.")
    for index, card in enumerate(cards):
        stub_name = _lean_name(f"{packet['program_id']}_{card['proofTarget']}_{index}")
        lines.extend(
            [
                f"/-- Candidate obligation: {card['description']} -/",
                f"def {stub_name} : String := \"{card['obligationId']}\"",
                "",
            ]
        )
    lines.extend(
        [
            "end GeneratedObligations",
            "end EML",
            "end Monogate",
            "",
        ]
    )
    return "\n".join(lines)


def _build_machlib_stub_manifest(result: dict[str, Any], stub_relpath: str) -> dict[str, Any]:
    return {
        "schemaVersion": "monogate.eml_machlib_obligation_stub.v0",
        "status": "candidate_only",
        "programId": result["sourcePacket"]["program_id"],
        "artifactId": result["artifactId"],
        "stubPath": stub_relpath,
        "obligationCount": result["obligations"]["summary"]["count"],
        "provedCount": result["obligations"]["summary"]["proved_count"],
        "checkedWitnessCount": result["domainSafety"]["summary"]["checked_obligation_count"],
        "claimFlags": {
            "formal_verification_claim": False,
            "theorem_proof_claim": False,
            "machlib_build_claim": False,
            "compiler_behavior_changed": False,
            "public_ready": False,
        },
        "nonClaims": [
            "Lean stub export is not a proof.",
            "Lean stub export is not a MachLib build result.",
            "Lean stub export does not change Forge/compiler behavior.",
        ],
    }


def _registry_next_action(card: dict[str, Any]) -> str:
    if card["status"] == "checked_small_witness":
        return "Keep witness linked and do not promote broad claims."
    if card["kind"] == "range_safety":
        return "Attach runtime guard, sampled replay evidence, or MachLib range proof."
    if card["trigger"] == "div":
        return "Prove denominator nonzero or add a guard before division."
    if card["trigger"] == "ln":
        return "Prove log argument positive or route through a log-domain guard."
    if card["trigger"] == "sqrt":
        return "Prove argument nonnegative or route through a nonnegative guard."
    return "Classify the proof target and add a specific witness plan."


def build_obligation_registry(results: list[dict[str, Any]]) -> dict[str, Any]:
    entries = []
    for result in sorted(results, key=lambda item: item["sourcePacket"]["program_id"]):
        packet = result["sourcePacket"]
        domain_by_id = {
            item["requirementId"]: item
            for item in result["domainSafety"]["domainRequirements"]
        }
        for card in result["obligations"]["cards"]:
            requirement = domain_by_id.get(card["obligationId"])
            entries.append(
                {
                    "obligationId": card["obligationId"],
                    "programId": packet["program_id"],
                    "artifactId": result["artifactId"],
                    "family": packet["family"],
                    "kind": card["kind"],
                    "trigger": card["trigger"],
                    "proofTarget": card["proofTarget"],
                    "status": card["status"],
                    "checkedBy": card.get("checkedBy"),
                    "proofArtifact": card.get("proofArtifact"),
                    "claimBoundary": card["nonClaim"],
                    "blockedPublicClaims": result["domainSafety"]["blockedPublicClaims"],
                    "nextAction": _registry_next_action(card),
                    "requirement": requirement.get("requirement") if requirement else None,
                }
            )
    checked = [entry for entry in entries if entry["status"] == "checked_small_witness"]
    unresolved = [entry for entry in entries if entry["status"] != "checked_small_witness"]
    domain_entries = [entry for entry in entries if entry["kind"] == "domain"]
    next_targets = [
        entry
        for entry in unresolved
        if entry["kind"] == "domain"
    ] or unresolved
    return {
        "schemaVersion": OBLIGATION_REGISTRY_SCHEMA_VERSION,
        "date": DATE,
        "status": "candidate_only",
        "entries": entries,
        "summary": {
            "obligation_count": len(entries),
            "domain_obligation_count": len(domain_entries),
            "range_safety_obligation_count": sum(1 for entry in entries if entry["kind"] == "range_safety"),
            "checked_witness_count": len(checked),
            "unresolved_obligation_count": len(unresolved),
            "checked_domain_obligation_count": sum(1 for entry in domain_entries if entry["status"] == "checked_small_witness"),
            "blocked_public_claim_count": len(
                sorted({claim for entry in entries for claim in entry["blockedPublicClaims"]})
            ),
        },
        "nextProofTargets": next_targets[:3],
        "claimFlags": {
            "public_ready": False,
            "public_savings_claim": False,
            "hardware_observed": False,
            "formal_verification_claim": False,
            "theorem_proof_claim": False,
            "certified_safety_claim": False,
            "production_controller_claim": False,
            "compiler_behavior_changed": False,
            "forge_behavior_changed": False,
        },
        "nonClaims": [
            "The registry is an internal proof-work queue, not a proof.",
            "Checked witnesses are local obligations, not complete EML safety.",
            "The registry does not change Forge/compiler behavior.",
        ],
    }


def packet_from_cli(args: argparse.Namespace) -> dict[str, Any]:
    if not args.expression:
        raise ValueError("--expression is required when --packet is not provided")
    inputs = [item.strip() for item in args.inputs.split(",") if item.strip()] if args.inputs else []
    return {
        "schemaVersion": SCHEMA_VERSION,
        "program_id": args.program_id,
        "family": args.family,
        "expression": args.expression,
        "inputs": inputs,
        "units": {name: "unspecified" for name in inputs},
        "safe_ranges": {},
        "physical_meaning": args.physical_meaning,
        "source_repo": args.source_repo,
        "simulated_trace_samples": [],
        "claim_flags": dict(DEFAULT_CLAIM_FLAGS),
    }


def load_packet(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_expression_packet(packet: dict[str, Any]) -> None:
    if packet.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("schemaVersion must be monogate.eml_expression_packet.v0")
    program_id = packet.get("program_id")
    if not isinstance(program_id, str) or not re.match(r"^[a-z][a-z0-9_]*_v[0-9]+$", program_id):
        raise ValueError("program_id must match ^[a-z][a-z0-9_]*_v[0-9]+$")
    for key in ["family", "expression", "physical_meaning", "source_repo"]:
        if not isinstance(packet.get(key), str) or not packet[key]:
            raise ValueError(f"{key} must be a non-empty string")
    inputs = packet.get("inputs")
    if not isinstance(inputs, list) or not inputs:
        raise ValueError("inputs must be a non-empty list")
    if len(set(inputs)) != len(inputs):
        raise ValueError("inputs must be unique")
    for name in inputs:
        if not isinstance(name, str) or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
            raise ValueError(f"invalid input name: {name!r}")
    units = packet.get("units")
    if not isinstance(units, dict):
        raise ValueError("units must be an object")
    safe_ranges = packet.get("safe_ranges")
    if not isinstance(safe_ranges, dict):
        raise ValueError("safe_ranges must be an object")
    for name, bounds in safe_ranges.items():
        if not isinstance(bounds, dict) or "min" not in bounds or "max" not in bounds:
            raise ValueError(f"safe range for {name} must include min and max")
        if not isinstance(bounds["min"], (int, float)) or not isinstance(bounds["max"], (int, float)):
            raise ValueError(f"safe range for {name} must be numeric")
        if bounds["min"] > bounds["max"]:
            raise ValueError(f"safe range for {name} has min > max")
    claim_flags = packet.get("claim_flags")
    if not isinstance(claim_flags, dict):
        raise ValueError("claim_flags must be an object")
    missing = [key for key in FORBIDDEN_TRUE_FLAGS if key not in claim_flags]
    if missing:
        raise ValueError(f"claim_flags missing required keys: {', '.join(missing)}")
    for key in FORBIDDEN_TRUE_FLAGS:
        if claim_flags.get(key) is not False:
            raise ValueError(f"forbidden claim flag must be false: {key}")


def build_result(packet: dict[str, Any], proof_status_dir: Path | None = ROOT / "reports/eml_proof_status") -> dict[str, Any]:
    validate_expression_packet(packet)
    ir = build_ir(packet["program_id"], packet["expression"])
    validate_ir(ir)
    ir_args = set(ir["arguments"])
    declared_inputs = set(packet["inputs"])
    if ir_args != declared_inputs:
        raise ValueError(
            "declared inputs must match parsed expression arguments: "
            f"declared={sorted(declared_inputs)} parsed={sorted(ir_args)}"
        )
    reused_nodes = [
        {
            "id": node["id"],
            "kind": node["kind"],
            "op": node.get("op"),
            "source": node["source"],
            "reuse_count": node["reuse_count"],
        }
        for node in ir["nodes"]
        if node.get("reuse_count", 1) > 1
    ]
    edges = _edges(ir["nodes"])
    proof_statuses = _load_proof_statuses(packet["program_id"], proof_status_dir)
    obligations = _build_obligations(packet, ir, proof_statuses)
    domain_safety = _build_domain_safety(packet, obligations)
    result = {
        "schemaVersion": RESULT_SCHEMA_VERSION,
        "artifactId": artifact_id(packet["program_id"]),
        "date": DATE,
        "status": "EML_PACKET_BUILDER_CANDIDATE_PASS",
        "sourcePacket": packet,
        "ir": {
            "schemaVersion": ir["schema_version"],
            "programId": ir["program_id"],
            "outputNode": ir["output_node"],
            "nodeCount": len(ir["nodes"]),
            "edgeCount": len(edges),
            "nodes": ir["nodes"],
            "edges": edges,
            "reusedNodes": reused_nodes,
            "lowering": ir["lowering"],
        },
        "costs": {
            "costModel": ir["cost_model"],
            "canonicalPublicTreeSuperbestNodes": ir["tree_superbest_nodes"],
            "internalDagSuperbestNodes": ir["dag_superbest_nodes"],
            "internalExtraDagSavingsNodes": ir["extra_superbest_savings_nodes"],
            "canonicalPublicTreeEmlNodes": ir["tree_eml_nodes"],
            "internalDagEmlNodes": ir["dag_eml_nodes"],
            "publicSavingsClaim": False,
        },
        "replay": {
            "packetId": ir["replay_packet"]["packet_id"],
            "frameCount": ir["replay_packet"]["frame_count"],
            "terminalState": ir["replay_packet"]["terminal_state"],
            "hashChainValid": True,
            "frames": ir["replay_packet"]["frames"],
            "timeline": _timeline(ir["replay_packet"]["frames"]),
        },
        "review": {
            "decision": "candidate_only",
            "validationStatus": "pass",
            "replayStatus": "pass",
            "semanticStrength": "eml_expression_packet_candidate_no_public_savings_claim",
            "claimBoundary": "Generated EML packet is candidate-only. DAG savings are internal evidence, not a public savings claim.",
            "nonClaims": [
                "No new public savings claim.",
                "No Forge/compiler behavior change.",
                "No theorem or formal verification claim.",
                "No hardware observation.",
                "No certified safety or production controller claim.",
                "No package publish or deploy.",
            ],
        },
        "obligations": {
            "schemaVersion": "monogate.eml_obligation_cards.v0",
            "status": "candidate_only",
            "cards": obligations,
            "summary": {
                "count": len(obligations),
                "domain_count": sum(1 for item in obligations if item["kind"] == "domain"),
                "range_safety_count": sum(1 for item in obligations if item["kind"] == "range_safety"),
                "proved_count": sum(1 for item in obligations if item["status"] == "checked_small_witness"),
            },
            "nonClaims": [
                "Obligation cards are not proofs.",
                "Range cards are not hardware observations.",
                "Domain cards are not formal verification claims.",
            ],
        },
        "domainSafety": domain_safety,
        "validationCommands": [
            "python python/scripts/eml_packet_builder.py --build-fixtures --strict",
            "python -m pytest -q python/tests/test_eml_packet_builder.py",
        ],
    }
    result["safeRewriteProposals"] = _build_safe_rewrite_proposals(result)
    return result


def build_evidence_packet(result: dict[str, Any]) -> dict[str, Any]:
    packet = result["sourcePacket"]
    return {
        "schemaVersion": "monogate.evidence_public_packet.v0",
        "artifactId": result["artifactId"],
        "title": f"EML Packet: {packet['program_id']}",
        "reviewDecision": "candidate_only",
        "validationStatus": "pass",
        "replayStatus": "pass",
        "semanticStrength": result["review"]["semanticStrength"],
        "semanticReview": {
            "program_id": packet["program_id"],
            "family": packet["family"],
            "source_expression": packet["expression"],
            "input_count": len(packet["inputs"]),
            "node_count": result["ir"]["nodeCount"],
            "edge_count": result["ir"]["edgeCount"],
            "reused_node_count": len(result["ir"]["reusedNodes"]),
            "frame_count": result["replay"]["frameCount"],
            "obligation_count": result["obligations"]["summary"]["count"],
            "domain_obligation_count": result["obligations"]["summary"]["domain_count"],
            "range_safety_obligation_count": result["obligations"]["summary"]["range_safety_count"],
            "domain_requirement_count": result["domainSafety"]["summary"]["domain_requirement_count"],
            "range_assumption_count": result["domainSafety"]["summary"]["range_assumption_count"],
            "blocked_public_claim_count": result["domainSafety"]["summary"]["blocked_public_claim_count"],
            "checked_obligation_count": result["domainSafety"]["summary"]["checked_obligation_count"],
            "checked_domain_requirement_count": result["domainSafety"]["summary"]["checked_domain_requirement_count"],
            "public_savings_claim": False,
            "internal_extra_dag_savings_nodes": result["costs"]["internalExtraDagSavingsNodes"],
        },
        "claimFlags": {
            **dict(DEFAULT_CLAIM_FLAGS),
            "package_publish_performed": False,
            "deploy_performed": False,
        },
        "claimBoundary": result["review"]["claimBoundary"],
        "nonClaims": result["review"]["nonClaims"],
        "reviewHighlights": [
            "Built from an EML Expression Packet v0 input.",
            "Generated EML IR and replay frames with the existing IR substrate pipeline.",
            "Generated candidate proof-obligation cards for domain and range boundaries.",
            "Classified domain requirements, range assumptions, blocked claims, and candidate safe rewrites.",
            f"Loaded {result['domainSafety']['summary']['checked_obligation_count']} checked small witness(es).",
            "Kept public savings and hardware/proof claims false.",
        ],
        "validationCommands": result["validationCommands"],
        "timeline": [
            {"label": "Packet intake", "status": "pass", "detail": "Expression packet validated locally."},
            {"label": "IR/replay", "status": "pass", "detail": "Existing EML IR pipeline emitted a parked replay packet."},
            {"label": "Claim boundary", "status": "pass", "detail": "Forbidden public/hardware/proof claims remain false."},
        ],
        "reviewReasons": [
            "Private intake artifact for deciding whether an EML expression should be surfaced later.",
        ],
        "reviewNotes": "Candidate-only private EML packet-builder output.",
        "sourceReportPath": f"reports/eml_packets/{packet['program_id']}_packet_builder_{DATE.replace('-', '_')}.md",
        "evidencePaths": [
            "schemas/eml_expression_packet_v0.json",
            "python/scripts/eml_packet_builder.py",
            f"python/results/eml_packets/{packet['program_id']}_packet_{DATE.replace('-', '_')}.json",
            f"reports/evidence_packets/{packet['program_id']}_eml_packet.json",
        ],
    }


def render_report(result: dict[str, Any], evidence: dict[str, Any]) -> str:
    packet = result["sourcePacket"]
    return "\n".join(
        [
            f"# EML Packet Builder Result: {packet['program_id']}",
            "",
            f"Date: {DATE}",
            "",
            "Status: `EML_PACKET_BUILDER_CANDIDATE_PASS`",
            "",
            "## Source Packet",
            "",
            f"- Family: `{packet['family']}`",
            f"- Expression: `{packet['expression']}`",
            f"- Inputs: `{', '.join(packet['inputs'])}`",
            f"- Source repo: `{packet['source_repo']}`",
            f"- Meaning: {packet['physical_meaning']}",
            "",
            "## Generated Artifact",
            "",
            f"- Artifact: `{result['artifactId']}`",
            f"- DAG nodes: `{result['ir']['nodeCount']}`",
            f"- DAG edges: `{result['ir']['edgeCount']}`",
            f"- Reused nodes: `{len(result['ir']['reusedNodes'])}`",
            f"- Replay frames: `{result['replay']['frameCount']}`",
            f"- Obligation cards: `{result['obligations']['summary']['count']}`",
            f"- Domain requirements: `{result['domainSafety']['summary']['domain_requirement_count']}`",
            f"- Range assumptions: `{result['domainSafety']['summary']['range_assumption_count']}`",
            f"- Public tree SuperBEST baseline: `{result['costs']['canonicalPublicTreeSuperbestNodes']}`",
            f"- Internal DAG SuperBEST candidate: `{result['costs']['internalDagSuperbestNodes']}`",
            "",
            "## Review",
            "",
            f"- Decision: `{evidence['reviewDecision']}`",
            f"- Validation: `{evidence['validationStatus']}`",
            f"- Replay: `{evidence['replayStatus']}`",
            f"- Semantic strength: `{evidence['semanticStrength']}`",
            "",
            "## Obligation Cards",
            "",
            f"- Domain obligations: `{result['obligations']['summary']['domain_count']}`",
            f"- Range-safety obligations: `{result['obligations']['summary']['range_safety_count']}`",
            f"- Proved obligations: `{result['obligations']['summary']['proved_count']}`",
            "",
            "## Domain Safety Lens",
            "",
            f"- Unresolved obligations: `{result['domainSafety']['summary']['unresolved_obligation_count']}`",
            f"- Checked obligations: `{result['domainSafety']['summary']['checked_obligation_count']}`",
            f"- Candidate safe rewrites: `{result['domainSafety']['summary']['safe_rewrite_candidate_count']}`",
            f"- Blocked public claims: `{result['domainSafety']['summary']['blocked_public_claim_count']}`",
            "",
            "## Non-Claims",
            "",
            "- No new public savings claim.",
            "- No Forge/compiler behavior change.",
            "- No theorem or formal verification claim.",
            "- No hardware observation.",
            "- No certified safety or production controller claim.",
            "- No package publish or deploy.",
            "",
        ]
    )


def write_outputs(
    result: dict[str, Any],
    out_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    obligation_dir: Path,
) -> dict[str, Path]:
    program_id = result["sourcePacket"]["program_id"]
    stamp = DATE.replace("-", "_")
    evidence = build_evidence_packet(result)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / f"{program_id}_packet_{stamp}.json"
    report_path = report_dir / f"{program_id}_packet_builder_{stamp}.md"
    evidence_path = evidence_dir / f"{program_id}_eml_packet.json"
    stub_dir = obligation_dir / program_id
    stub_path = stub_dir / f"{program_id}_obligations.lean"
    stub_manifest_path = stub_dir / f"{program_id}_machlib_stub_manifest.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(result, evidence), encoding="utf-8")
    stub_dir.mkdir(parents=True, exist_ok=True)
    stub_path.write_text(_build_machlib_stub_text(result), encoding="utf-8")
    try:
        stub_relpath = str(stub_path.relative_to(ROOT))
    except ValueError:
        stub_relpath = str(stub_path)
    manifest = _build_machlib_stub_manifest(result, stub_relpath)
    stub_manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "result": result_path,
        "report": report_path,
        "evidence": evidence_path,
        "machlib_stub": stub_path,
        "machlib_stub_manifest": stub_manifest_path,
    }


def write_obligation_registry(results: list[dict[str, Any]], registry_dir: Path) -> Path:
    registry_dir.mkdir(parents=True, exist_ok=True)
    registry = build_obligation_registry(results)
    path = registry_dir / f"eml_proof_obligation_registry_{DATE.replace('-', '_')}.json"
    path.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def build_one(
    packet: dict[str, Any],
    out_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    obligation_dir: Path,
    proof_status_dir: Path | None = ROOT / "reports/eml_proof_status",
) -> dict[str, Any]:
    result = build_result(packet, proof_status_dir)
    paths = write_outputs(result, out_dir, report_dir, evidence_dir, obligation_dir)
    return {"result": result, "paths": {key: str(value) for key, value in paths.items()}}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, help="EML Expression Packet v0 JSON file")
    parser.add_argument("--expression", help="Expression for direct CLI intake")
    parser.add_argument("--program-id", default="adhoc_expression_v0")
    parser.add_argument("--family", default="adhoc")
    parser.add_argument("--inputs", default="", help="Comma-separated input names for direct CLI intake")
    parser.add_argument("--physical-meaning", default="Ad hoc EML expression packet.")
    parser.add_argument("--source-repo", default="monogate")
    parser.add_argument("--fixtures-dir", type=Path, default=ROOT / "python/fixtures/eml_expression_packets")
    parser.add_argument("--build-fixtures", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports/eml_packets")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--obligation-dir", type=Path, default=ROOT / "reports/eml_obligations")
    parser.add_argument("--proof-status-dir", type=Path, default=ROOT / "reports/eml_proof_status")
    parser.add_argument("--registry-dir", type=Path, default=ROOT / "reports/eml_obligation_registry")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    if args.build_fixtures:
        packets = [load_packet(path) for path in sorted(args.fixtures_dir.glob("*.json"))]
        if args.strict and len(packets) < 3:
            raise SystemExit("strict mode requires at least 3 fixture packets")
        built = [
            build_one(packet, args.out_dir, args.report_dir, args.evidence_dir, args.obligation_dir, args.proof_status_dir)
            for packet in packets
        ]
        registry_path = write_obligation_registry([item["result"] for item in built], args.registry_dir)
        print("EML_PACKET_BUILDER_FIXTURES_OK")
        print(f"packets={len(built)}")
        print(f"registry={registry_path}")
        return 0

    packet = load_packet(args.packet) if args.packet else packet_from_cli(args)
    built = build_one(packet, args.out_dir, args.report_dir, args.evidence_dir, args.obligation_dir, args.proof_status_dir)
    if args.strict and built["result"]["review"]["decision"] != "candidate_only":
        raise SystemExit("strict mode requires candidate_only review decision")
    print("EML_PACKET_BUILDER_OK")
    print(f"artifact={built['result']['artifactId']} frames={built['result']['replay']['frameCount']}")
    print(json.dumps(built["paths"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
