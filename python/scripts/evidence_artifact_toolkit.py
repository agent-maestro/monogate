"""Small shared helpers for claim-bounded evidence artifacts.

This module is intentionally not a broad framework. It only covers the three
repeated shapes that current artifact scripts keep hand-writing:

- claim-flagged JSON payload validation
- markdown report rendering
- command feed construction
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

EVIDENCE_SCHEMA_VERSION = "monogate.evidence_public_packet.v0"


def assert_claim_flags_bounded(
    claim_flags: dict[str, bool],
    true_claim_flags: set[str],
    *,
    required_false_flags: set[str] | None = None,
) -> None:
    missing = true_claim_flags - set(claim_flags)
    if missing:
        raise ValueError(f"missing true claim flags: {sorted(missing)}")
    for key, value in claim_flags.items():
        if not isinstance(value, bool):
            raise ValueError(f"{key} must be bool")
        if key in true_claim_flags:
            if value is not True:
                raise ValueError(f"{key} must be true")
        elif value is not False:
            raise ValueError(f"{key} must remain false")
    for key in required_false_flags or set():
        if claim_flags.get(key) is not False:
            raise ValueError(f"{key} must be present and false")


def build_claim_flagged_packet(
    *,
    schema_version: str,
    artifact_id: str,
    artifact_type: str,
    status: str,
    date: str,
    summary: dict[str, Any],
    claim_flags: dict[str, bool],
    true_claim_flags: set[str],
    non_claims: list[str],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    assert_claim_flags_bounded(claim_flags, true_claim_flags)
    if not non_claims:
        raise ValueError("non_claims must not be empty")
    payload: dict[str, Any] = {
        "schemaVersion": schema_version,
        "artifactId": artifact_id,
        "artifactType": artifact_type,
        "status": status,
        "date": date,
        "summary": summary,
        "claimFlags": dict(claim_flags),
        "nonClaims": list(non_claims),
    }
    if extra:
        for key, value in extra.items():
            if key in payload:
                raise ValueError(f"extra key collides with base payload: {key}")
            payload[key] = value
    return payload


def build_evidence_packet(
    *,
    artifact_id: str,
    artifact_type: str,
    semantic_strength: str,
    source: str,
    summary: dict[str, Any],
    claim_flags: dict[str, bool],
    non_claims: list[str],
) -> dict[str, Any]:
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "artifactId": artifact_id,
        "artifactType": artifact_type,
        "validationStatus": "pass",
        "semanticStrength": semantic_strength,
        "source": source,
        "summary": summary,
        "claimFlags": dict(claim_flags),
        "nonClaims": list(non_claims),
    }


def render_markdown_report(
    *,
    title: str,
    status: str,
    summary_rows: list[tuple[str, Any]],
    non_claims: list[str],
    sections: list[tuple[str, list[str]]] | None = None,
) -> str:
    lines = [f"# {title}", "", f"Status: `{status}`", "", "## Summary", ""]
    for key, value in summary_rows:
        lines.append(f"- {key}: `{value}`")
    for heading, body_lines in sections or []:
        lines.extend(["", f"## {heading}", ""])
        lines.extend(body_lines)
    lines.extend(["", "## Non-Claims", ""])
    lines.extend(f"- {item}" for item in non_claims)
    return "\n".join(lines) + "\n"


def build_command_feed(
    *,
    feed_id: str,
    date: str,
    status: str,
    next_action: str,
    claim_flags: dict[str, bool],
    fields: dict[str, Any] | None = None,
) -> dict[str, Any]:
    feed: dict[str, Any] = {
        "feedId": feed_id,
        "date": date,
        "status": status,
        "nextAction": next_action,
        "claimFlags": dict(claim_flags),
    }
    for key, value in (fields or {}).items():
        if key in feed:
            raise ValueError(f"feed field collides with base field: {key}")
        feed[key] = value
    return feed


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
