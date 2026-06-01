#!/usr/bin/env python3
"""EE-COURSE-A1 electronics course factory contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DATE = "2026-06-01"
STAMP = DATE.replace("-", "_")
SCHEMA_VERSION = "monogate.electronics_course_factory_contract.v0"
EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"
STATUS = "EE_COURSE_A1_ELECTRONICS_COURSE_FACTORY_CONTRACT_PASS"

CLAIM_FLAGS = {
    "hardware_observed": False,
    "live_serial_capture_performed": False,
    "production_controller_claim": False,
    "certified_safety_claim": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "formal_equivalence_claim": False,
    "public_ready": False,
    "source_repo_modified": False,
    "electronics_url_modified": False,
    "automatic_reviewer_approval": False,
}

NON_CLAIMS = [
    "EE-COURSE-A1 defines a research-side course factory contract only.",
    "EE-COURSE-A1 does not modify monogate-electronics.",
    "EE-COURSE-A1 does not modify monogate.dev/electronics or generated electronics public artifacts.",
    "EE-COURSE-A1 does not perform hardware capture, serial reads, flashing, FPGA programming, or hardware operation.",
    "EE-COURSE-A1 does not claim hardware-observed behavior, production control, certified safety, public readiness, runtime performance, compiler correctness, or formal equivalence.",
]


def required_course_files() -> list[dict[str, str]]:
    return [
        {"id": "course_manifest", "description": "Course manifest with lesson ids, kernel ids, source paths, and evidence packet links."},
        {"id": "kernel_contract", "description": "EML or kernel contract naming equations, guards, inputs, outputs, and expected behavior."},
        {"id": "simulated_trace", "description": "Deterministic simulated trace or replay fixture suitable for non-live validation."},
        {"id": "validator_result", "description": "Validator output with pass/fail status and bounded error or guard result."},
        {"id": "learner_material", "description": "Lesson text, exercises, or dashboard-facing content produced by the laptop lane."},
        {"id": "evidence_packet", "description": "Claim-bounded evidence packet using the electronics evidence grammar."},
        {"id": "handoff_notes", "description": "Laptop-agent handoff notes naming what changed and what remains missing."},
        {"id": "claim_boundary", "description": "Explicit public/private claim flags and non-claims for reviewer use."},
    ]


def completeness_rubric() -> list[dict[str, Any]]:
    return [
        {
            "id": "manifest_complete",
            "required": True,
            "passCondition": "course_manifest names course id, target board, kernel ids, source paths, and evidence packet paths",
        },
        {
            "id": "simulated_replayable",
            "required": True,
            "passCondition": "simulated trace validates locally without hardware access",
        },
        {
            "id": "guarded_kernel_present",
            "required": True,
            "passCondition": "kernel contract names input domain guards and output bounds or comparison method",
        },
        {
            "id": "claim_flags_explicit",
            "required": True,
            "passCondition": "hardware/live/public/production/certified-safety flags are present and bounded",
        },
        {
            "id": "live_capture_optional",
            "required": False,
            "passCondition": "live capture may be absent, but absence is marked as missing evidence rather than failure",
        },
        {
            "id": "reviewer_decision_pending",
            "required": True,
            "passCondition": "course is never auto-approved; reviewer decision is pending until explicitly recorded",
        },
    ]


def course_002_intake_readiness() -> dict[str, Any]:
    return {
        "artifactId": "ee-course-a1-course-002-intake-readiness",
        "courseId": "course_002",
        "targetFamily": "esp32",
        "expectedProducer": "laptop_agent",
        "acceptedPacketTypes": [
            "simulated_lesson_packet",
            "comparison_packet",
            "live_capture_packet",
            "proof_guard_obligation_packet",
        ],
        "requiredMetadata": [
            "courseId",
            "lessonIds",
            "kernelIds",
            "targetBoard",
            "sourceRepo",
            "sourceCommit",
            "sourcePaths",
            "tracePaths",
            "validatorCommands",
            "validatorResults",
            "claimFlags",
            "missingEvidence",
            "reviewerAction",
        ],
        "failureModes": [
            "blocked_missing_manifest",
            "blocked_missing_kernel_contract",
            "blocked_missing_trace_or_validator",
            "blocked_claim_overreach",
            "blocked_unexpected_source_owner",
        ],
        "reviewerOutcomes": [
            "private_reviewable_simulated",
            "live_capture_reviewable",
            "needs_laptop_agent_revision",
            "blocked_missing_metadata",
            "blocked_claim_overreach",
        ],
        "defaultDecision": "await_laptop_agent_course_002_packet",
        "monogateElectronicsRepoTouched": False,
        "electronicsSurfaceTouched": False,
    }


def esp32_course_arc() -> list[dict[str, Any]]:
    return [
        {
            "courseId": "course_001",
            "role": "perfected_template",
            "targetFamily": "esp32",
            "courseTheme": "visible_guarded_control_foundation",
            "reviewPosture": "template_source_for_future_course_packets",
        },
        {
            "courseId": "course_002",
            "role": "next_intake",
            "targetFamily": "esp32",
            "courseTheme": "sensor_input_guarded_response",
            "reviewPosture": "await_laptop_agent_packet_then_apply_course_factory_contract",
        },
        {
            "courseId": "course_003",
            "role": "planned",
            "targetFamily": "esp32",
            "courseTheme": "timed_dynamics_or_debounced_state",
            "reviewPosture": "must ship simulated trace before live claim",
        },
        {
            "courseId": "course_004",
            "role": "planned",
            "targetFamily": "esp32",
            "courseTheme": "multi_output_signal_or_actuator_behavior",
            "reviewPosture": "must keep actuator and safety claims bounded",
        },
        {
            "courseId": "course_005",
            "role": "planned",
            "targetFamily": "esp32",
            "courseTheme": "integrated_mini_system_with_evidence_packet",
            "reviewPosture": "may prepare Arty A7 bridge only after ESP32 evidence chain is reviewable",
        },
    ]


def arty_a7_transition_gate() -> dict[str, Any]:
    return {
        "artifactId": "ee-course-a1-arty-a7-transition-gate",
        "targetFamily": "arty_a7",
        "startsAfter": "five_esp32_courses_private_reviewable_or_explicitly_parked",
        "bridgeShape": [
            "guarded_control_on_microcontroller",
            "same_kernel_contract",
            "replayable_trace",
            "hardware_target_translation",
            "fpga_friendly_representation",
            "arty_a7_course_packet",
        ],
        "requiredBeforeFirstArtyCourse": [
            "esp32_course_arc_status_review",
            "fpga_target_profile_or_blocker",
            "simulated_trace_or_formal_guard_packet",
            "no_public_fpga_claim_without_laptop_agent_evidence",
        ],
        "blockedClaims": [
            "fpga_hardware_observed",
            "production_controller_ready",
            "certified_safety",
            "formal_equivalence",
            "public_ready",
        ],
        "monogateElectronicsRepoTouched": False,
        "electronicsSurfaceTouched": False,
    }


def command_center_rows() -> list[dict[str, Any]]:
    return [
        {
            "rowId": "ee-course-factory-contract",
            "rowType": "electronics_course_factory",
            "status": "private_reviewable_contract",
            "decision": "course_factory_ready_no_laptop_repo_touch",
        },
        {
            "rowId": "ee-course-002-intake",
            "rowType": "electronics_course_intake",
            "status": "pending_laptop_agent_packet",
            "decision": "await_course_002_packet",
        },
        {
            "rowId": "ee-esp32-five-course-arc",
            "rowType": "electronics_curriculum_arc",
            "status": "planned_with_course_001_template",
            "decision": "review_each_course_before_public_or_hardware_claim",
        },
        {
            "rowId": "ee-arty-a7-transition",
            "rowType": "electronics_target_transition",
            "status": "parked_until_esp32_arc_reviewable",
            "decision": "do_not_start_arty_public_or_hardware_claims_yet",
        },
    ]


def build_payload() -> dict[str, Any]:
    required_files = required_course_files()
    rubric = completeness_rubric()
    course_002 = course_002_intake_readiness()
    esp32_arc = esp32_course_arc()
    arty_gate = arty_a7_transition_gate()
    cockpit_rows = command_center_rows()
    summary = {
        "requiredCourseFileCount": len(required_files),
        "rubricRowCount": len(rubric),
        "requiredRubricRowCount": sum(1 for row in rubric if row["required"]),
        "esp32CourseCount": len(esp32_arc),
        "course002ReadyForIntake": True,
        "artyA7TransitionParked": True,
        "commandCenterRowCount": len(cockpit_rows),
        "hardwareObserved": False,
        "liveCapturePerformed": False,
        "monogateElectronicsRepoTouched": False,
        "electronicsSurfaceTouched": False,
        "claimFlagsAllFalse": all(value is False for value in CLAIM_FLAGS.values()),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "contractType": "electronics_course_factory_contract_v0",
        "artifactId": "ee-course-a1-electronics-course-factory-contract",
        "status": STATUS,
        "decision": "electronics_course_factory_ready_for_course_002_no_laptop_surface_touch",
        "date": DATE,
        "sourceBridge": "ee-bridge-a6-electronics-bridge-regression-guard",
        "requiredCourseFiles": required_files,
        "completenessRubric": rubric,
        "course002IntakeReadiness": course_002,
        "esp32CourseArc": esp32_arc,
        "artyA7TransitionGate": arty_gate,
        "commandCenterRows": cockpit_rows,
        "summary": summary,
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def validate_payload(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema version")
    if summary["requiredCourseFileCount"] != 8:
        raise ValueError("unexpected required course file count")
    if summary["rubricRowCount"] != 6:
        raise ValueError("unexpected rubric row count")
    if summary["esp32CourseCount"] != 5:
        raise ValueError("unexpected ESP32 course count")
    if payload["course002IntakeReadiness"]["defaultDecision"] != "await_laptop_agent_course_002_packet":
        raise ValueError("Course 002 intake decision drift")
    if not summary["artyA7TransitionParked"]:
        raise ValueError("Arty A7 transition must stay parked")
    if summary["commandCenterRowCount"] != 4:
        raise ValueError("unexpected command-center row count")
    if summary["monogateElectronicsRepoTouched"] or summary["electronicsSurfaceTouched"]:
        raise ValueError("electronics ownership boundary drift")
    if not all(value is False for value in payload["claimFlags"].values()):
        raise ValueError("claim flag drift")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": payload["artifactId"],
        "artifactType": "electronics_course_factory_contract",
        "validationStatus": "pass",
        "semanticStrength": "course_factory_ready_course_002_pending_no_laptop_surface_touch",
        "source": f"python/results/ee_course_a1_electronics_course_factory_contract/ee_course_a1_electronics_course_factory_contract_{STAMP}.json",
        "summary": payload["summary"],
        "claimFlags": dict(CLAIM_FLAGS),
        "nonClaims": list(NON_CLAIMS),
    }


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedId": "ee_course_a1_electronics_course_factory_contract_feed",
        "date": DATE,
        "status": payload["status"],
        "decision": payload["decision"],
        "course002DefaultDecision": payload["course002IntakeReadiness"]["defaultDecision"],
        "esp32CourseCount": payload["summary"]["esp32CourseCount"],
        "artyA7TransitionParked": payload["summary"]["artyA7TransitionParked"],
        "commandCenterRows": payload["commandCenterRows"],
        "nextAction": "Receive Course 002 from the laptop agent and validate it against EE-COURSE-A1 before any public or hardware-observed claim.",
        "claimFlags": dict(CLAIM_FLAGS),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# EE-COURSE-A1 Electronics Course Factory Contract",
        "",
        f"Status: `{payload['status']}`",
        "",
        "EE-COURSE-A1 turns Course 1 into the research-side course factory for Course 2, the five-course ESP32 arc, and the later Arty A7 transition.",
        "",
        "## Summary",
        "",
        f"- required course files: {payload['summary']['requiredCourseFileCount']}",
        f"- completeness rubric rows: {payload['summary']['rubricRowCount']}",
        f"- ESP32 course arc length: {payload['summary']['esp32CourseCount']}",
        f"- Course 002 intake ready: `{payload['summary']['course002ReadyForIntake']}`",
        f"- Arty A7 transition parked: `{payload['summary']['artyA7TransitionParked']}`",
        f"- Command Center row models: {payload['summary']['commandCenterRowCount']}",
        "",
        "## Course 002",
        "",
        f"- default decision: `{payload['course002IntakeReadiness']['defaultDecision']}`",
        f"- accepted packet types: {len(payload['course002IntakeReadiness']['acceptedPacketTypes'])}",
        f"- required metadata fields: {len(payload['course002IntakeReadiness']['requiredMetadata'])}",
        "",
        "## ESP32 Arc",
        "",
    ]
    lines.extend(
        f"- `{course['courseId']}`: {course['courseTheme']} (`{course['role']}`)"
        for course in payload["esp32CourseArc"]
    )
    lines.extend(["", "## Command Center Rows", ""])
    lines.extend(
        f"- `{row['rowId']}`: `{row['status']}`"
        for row in payload["commandCenterRows"]
    )
    lines.extend(["", "## Non-Claims", ""])
    lines.extend(f"- {item}" for item in payload["nonClaims"])
    return "\n".join(lines) + "\n"


def build_outputs(
    out_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
) -> dict[str, str]:
    payload = build_payload()
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"ee_course_a1_electronics_course_factory_contract_{STAMP}.json"
    report_path = report_dir / f"ee_course_a1_electronics_course_factory_contract_{STAMP}.md"
    evidence_path = evidence_dir / "ee_course_a1_electronics_course_factory_contract.json"
    feed_path = command_feed_dir / f"ee_course_a1_electronics_course_factory_contract_feed_{STAMP}.json"
    write_json(result_path, payload)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(payload), encoding="utf-8")
    write_json(evidence_path, evidence)
    write_json(feed_path, feed)
    return {
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/ee_course_a1_electronics_course_factory_contract")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets")
    parser.add_argument("--command-feed-dir", type=Path, default=ROOT / "command_center_feeds")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload()
    validate_payload(payload)
    if args.build:
        build_outputs(args.out_dir, args.report_dir, args.evidence_dir, args.command_feed_dir)
    print("EE_COURSE_A1_ELECTRONICS_COURSE_FACTORY_CONTRACT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
