"""Tests for EE-COURSE-A1 electronics course factory contract."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.ee_course_a1_electronics_course_factory_contract import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_ee_course_a1_records_course_factory_contract():
    payload = build_payload()
    validate_payload(payload)
    assert payload["status"] == "EE_COURSE_A1_ELECTRONICS_COURSE_FACTORY_CONTRACT_PASS"
    assert payload["decision"] == "electronics_course_factory_ready_for_course_002_no_laptop_surface_touch"
    assert payload["summary"]["requiredCourseFileCount"] == 8
    assert payload["summary"]["rubricRowCount"] == 6


def test_ee_course_a1_primes_course_002_intake():
    payload = build_payload()
    course_002 = payload["course002IntakeReadiness"]
    assert course_002["courseId"] == "course_002"
    assert course_002["targetFamily"] == "esp32"
    assert course_002["expectedProducer"] == "laptop_agent"
    assert course_002["defaultDecision"] == "await_laptop_agent_course_002_packet"
    assert "blocked_claim_overreach" in course_002["failureModes"]
    assert payload["summary"]["course002ReadyForIntake"] is True


def test_ee_course_a1_records_five_course_esp32_arc():
    payload = build_payload()
    arc = payload["esp32CourseArc"]
    assert [course["courseId"] for course in arc] == [
        "course_001",
        "course_002",
        "course_003",
        "course_004",
        "course_005",
    ]
    assert arc[0]["role"] == "perfected_template"
    assert arc[-1]["reviewPosture"] == "may prepare Arty A7 bridge only after ESP32 evidence chain is reviewable"


def test_ee_course_a1_parks_arty_a7_transition_until_esp32_chain_reviewable():
    payload = build_payload()
    gate = payload["artyA7TransitionGate"]
    assert gate["targetFamily"] == "arty_a7"
    assert gate["startsAfter"] == "five_esp32_courses_private_reviewable_or_explicitly_parked"
    assert payload["summary"]["artyA7TransitionParked"] is True
    assert "public_ready" in gate["blockedClaims"]


def test_ee_course_a1_models_command_center_rows():
    payload = build_payload()
    rows = {row["rowId"]: row for row in payload["commandCenterRows"]}
    assert rows["ee-course-factory-contract"]["status"] == "private_reviewable_contract"
    assert rows["ee-course-002-intake"]["status"] == "pending_laptop_agent_packet"
    assert rows["ee-esp32-five-course-arc"]["rowType"] == "electronics_curriculum_arc"
    assert rows["ee-arty-a7-transition"]["status"] == "parked_until_esp32_arc_reviewable"
    assert payload["summary"]["commandCenterRowCount"] == 4


def test_ee_course_a1_keeps_laptop_owned_surfaces_untouched():
    payload = build_payload()
    assert payload["summary"]["monogateElectronicsRepoTouched"] is False
    assert payload["summary"]["electronicsSurfaceTouched"] is False
    assert payload["course002IntakeReadiness"]["monogateElectronicsRepoTouched"] is False
    assert payload["course002IntakeReadiness"]["electronicsSurfaceTouched"] is False
    assert payload["artyA7TransitionGate"]["monogateElectronicsRepoTouched"] is False
    assert payload["artyA7TransitionGate"]["electronicsSurfaceTouched"] is False


def test_ee_course_a1_claim_flags_remain_false():
    payload = build_payload()
    assert payload["summary"]["claimFlagsAllFalse"] is True
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_ee_course_a1_writes_outputs(tmp_path):
    built = build_outputs(tmp_path / "results", tmp_path / "reports", tmp_path / "evidence", tmp_path / "feeds")
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    report = Path(built["report_path"]).read_text(encoding="utf-8")
    assert report.startswith("# EE-COURSE-A1")
    assert "Course 002" in report


def test_ee_course_a1_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/ee_course_a1_electronics_course_factory_contract.py",
            "--build",
            "--out-dir",
            str(tmp_path / "results"),
            "--report-dir",
            str(tmp_path / "reports"),
            "--evidence-dir",
            str(tmp_path / "evidence"),
            "--command-feed-dir",
            str(tmp_path / "feeds"),
            "--strict",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "EE_COURSE_A1_ELECTRONICS_COURSE_FACTORY_CONTRACT_OK" in proc.stdout
