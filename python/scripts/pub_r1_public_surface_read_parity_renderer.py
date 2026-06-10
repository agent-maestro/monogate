#!/usr/bin/env python3
"""PUB-R1 public-surface read parity renderer.

Deterministic, no-JS static HTML render of the PUB-R0 canonical brake-side
ledger. Implements PUB-R1 r2 §2 deliverable shape exactly: five content classes
(held lanes, retracted claims, negative results, standing claim rule, Lean
status line). Carries the two-stage drift guard (build-time and post-deploy).

This renderer does not execute the live public deploy. Deploy is gated on the
E5 human-authored authorization artifact and an explicit per-action operator
confirmation.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MONOGATE_NET = ROOT.parent / "monogate-net"
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from scripts import pub_r0_brake_side_ledger_generator as pub_r0  # noqa: E402
from scripts.evidence_artifact_toolkit import (  # noqa: E402
    build_claim_flagged_packet,
    build_command_feed,
    build_evidence_packet,
    render_markdown_report,
    write_json,
)

DATE = "2026-06-10"
STAMP = DATE.replace("-", "_")
PUB_R0_STAMP = "2026_06_10"
SCHEMA_VERSION = "monogate.pub_r1_public_surface_read_parity.v0"
STATUS = "PUB_R1_PUBLIC_SURFACE_READ_PARITY_PASS"
ARTIFACT_ID = "pub-r1-public-surface-read-parity"

PAGE_RELATIVE_PATH = "evidence-status/index.html"
LIVE_URL = "https://monogate.net/evidence-status/"

CONTENT_CLASSES = (
    "held_lanes",
    "retracted_claims",
    "negative_results",
    "standing_claim_rule",
    "lean_status_line",
)

TRUE_CLAIM_FLAGS = {
    "pub_r0_ledger_consumed",
    "five_content_classes_exhaustive",
    "static_no_js_html_rendered_locally",
    "build_time_drift_guard_implemented",
    "post_deploy_probe_implemented",
    "html_byte_derived_from_pub_r0_canonical_json",
    "page_committed_locally_only",
    "public_surface_blocked_until_authorized_deploy",
}

CLAIM_FLAGS = {
    "pub_r0_ledger_consumed": True,
    "five_content_classes_exhaustive": True,
    "static_no_js_html_rendered_locally": True,
    "build_time_drift_guard_implemented": True,
    "post_deploy_probe_implemented": True,
    "html_byte_derived_from_pub_r0_canonical_json": True,
    "page_committed_locally_only": True,
    "public_surface_blocked_until_authorized_deploy": True,
    "live_deploy_executed": False,
    "post_deploy_probe_passed": False,
    "public_surface_updated": False,
    "page_pushed_to_remote": False,
    "additional_content_class_added": False,
    "dashboard_ui_created": False,
    "renderer_correctness_claim": False,
    "ledger_completeness_claim": False,
    "training_cost_estimator_reopened": False,
    "training_cost_estimator_implemented": False,
    "estimate_values_produced": False,
    "training_savings_claim": False,
    "estimator_accuracy_claim": False,
    "product_implementation_started": False,
    "product_roadmap_reopened": False,
    "atlas_reviewer_response_consumed": False,
    "atlas_public_promotion": False,
    "atlas_catalog_completeness_claim": False,
    "public_math_promotion": False,
    "d110_started": False,
    "reviewer_response_consumed": False,
    "reviewer_approval_recorded": False,
    "laptop_artifact_consumed": False,
    "electronics_inbox_reopened": False,
    "electronics_repo_touched": False,
    "laptop_owned_repo_touched": False,
    "machlib_file_changed": False,
    "lean_typecheck_performed": False,
    "runtime_lowering_changed": False,
    "runtime_performance_claim": False,
    "compiler_correctness_claim": False,
    "hardware_readiness_claim": False,
    "silicon_readiness_claim": False,
    "broad_eml_advantage_claim": False,
}

NON_CLAIMS = [
    "PUB-R1 renders a static no-JS HTML page from the PUB-R0 canonical JSON ledger and implements a two-stage drift guard; it does not execute a live public deploy.",
    "PUB-R1 does not push to monogate-net's remote; the operator's per-action deploy confirmation is a separate step recorded in the E5 authorization artifact.",
    "PUB-R1 does not add a sixth content class, add adjectives, add prose beyond the canonical one-liners, or paraphrase any ledger text — every sentence on the page is either a quote of the standing rule, a ledger fact with artifact ID, or navigation.",
    "PUB-R1 does not introduce JavaScript or any dynamic content; the page must be fully readable to a no-JS reader.",
    "PUB-R1 does not reopen training-cost, Atlas, public-math, product-roadmap, or electronics lanes; it merely displays that they are held.",
    "PUB-R1 does not edit MachLib, run Lean type-check, change runtime lowering, touch laptop-owned repos, approve public copy beyond this page, or claim ledger completeness, renderer correctness, runtime performance, compiler correctness, hardware readiness, silicon readiness, or broad EML advantage.",
]


def load_pub_r0_payload(pub_r0_path: Path | None = None) -> dict[str, Any]:
    path = pub_r0_path or (
        ROOT
        / "python/results/pub_r0_brake_side_ledger_generator"
        / f"pub_r0_brake_side_ledger_generator_{PUB_R0_STAMP}.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    pub_r0.validate_payload(payload)
    return payload


def _esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_html(ledger: dict[str, Any], *, pub_r0_artifact_id: str, pub_r0_date: str) -> str:
    """Deterministic HTML render of the PUB-R0 ledger. Pure function.

    Output is byte-stable for a given ledger so the drift guard can re-render
    and compare bytes. No timestamps, no random ids, no environment data.
    """
    lines: list[str] = []
    lines.append("<!doctype html>")
    lines.append('<html lang="en">')
    lines.append("  <head>")
    lines.append('    <meta charset="utf-8" />')
    lines.append(
        '    <meta name="viewport" content="width=device-width, initial-scale=1" />'
    )
    lines.append("    <title>Monogate — Evidence &amp; Claims Status</title>")
    lines.append(
        '    <meta name="description" content="Monogate brake-side ledger: held lanes, retracted claims, negative results, standing claim rule, Lean status." />'
    )
    lines.append('    <link rel="stylesheet" href="../styles.css" />')
    lines.append("  </head>")
    lines.append('  <body>')
    lines.append('    <header class="site-header">')
    lines.append('      <nav class="topbar" aria-label="Primary">')
    lines.append('        <a class="brand-link" href="../">Monogate</a>')
    lines.append('        <div class="top-links">')
    lines.append('          <a href="../">Network</a>')
    lines.append('          <a href="https://monogate.org">monogate.org</a>')
    lines.append("        </div>")
    lines.append("      </nav>")
    lines.append('      <section class="hero" aria-labelledby="page-title">')
    lines.append('        <p class="eyebrow">Evidence &amp; Claims Status</p>')
    lines.append('        <h1 id="page-title">Brake-side ledger</h1>')
    lines.append(
        f'        <p class="lede">Held lanes, retracted claims, negative results, standing rule, Lean status. Byte-derived from <code>{_esc(pub_r0_artifact_id)}</code> ({_esc(pub_r0_date)}).</p>'
    )
    lines.append("      </section>")
    lines.append("    </header>")
    lines.append("    <main>")
    # 1. Held lanes
    lines.append('      <section aria-labelledby="held-title" class="surface-section">')
    lines.append(
        '        <div class="section-heading"><p class="eyebrow">Held lanes</p>'
        '<h2 id="held-title">Held lanes</h2></div>'
    )
    lines.append("        <ul>")
    for row in ledger["heldLanes"]:
        lines.append(
            "          <li>"
            f"<code>{_esc(row['laneId'])}</code>"
            f" — held by <code>{_esc(row['holdingArtifactId'])}</code>"
            f" — {_esc(row['oneLineReason'])}"
            "</li>"
        )
    lines.append("        </ul>")
    lines.append("      </section>")
    # 2. Retracted claims
    lines.append('      <section aria-labelledby="retracted-title" class="surface-section">')
    lines.append(
        '        <div class="section-heading"><p class="eyebrow">Retracted claims</p>'
        '<h2 id="retracted-title">Retracted claims</h2></div>'
    )
    lines.append("        <ul>")
    for row in ledger["retractedClaims"]:
        line_no = row.get("line")
        loc = f"{row['source']}:{line_no}" if line_no is not None else row["source"]
        lines.append(
            "          <li>"
            f"<code>{_esc(row['claimId'])}</code>"
            f" — <code>{_esc(loc)}</code>"
            f" — {_esc(row['oneLineText'])}"
            "</li>"
        )
    lines.append("        </ul>")
    lines.append("      </section>")
    # 3. Negative results
    lines.append('      <section aria-labelledby="negative-title" class="surface-section">')
    lines.append(
        '        <div class="section-heading"><p class="eyebrow">Negative results</p>'
        '<h2 id="negative-title">Negative results</h2></div>'
    )
    lines.append("        <ul>")
    for row in ledger["negativeResults"]:
        line_no = row.get("line")
        loc = f"{row['source']}:{line_no}" if line_no is not None else row["source"]
        lines.append(
            "          <li>"
            f"<code>{_esc(row['claimId'])}</code>"
            f" — <code>{_esc(loc)}</code>"
            f" — {_esc(row['oneLineText'])}"
            "</li>"
        )
    lines.append("        </ul>")
    lines.append("      </section>")
    # 4. Standing claim rule
    lines.append('      <section aria-labelledby="rule-title" class="surface-section">')
    lines.append(
        '        <div class="section-heading"><p class="eyebrow">Standing claim rule</p>'
        '<h2 id="rule-title">Standing claim rule</h2></div>'
    )
    lines.append(f"        <blockquote>{_esc(ledger['standingClaimRule'])}</blockquote>")
    lines.append("      </section>")
    # 5. Lean status line
    ls = ledger["leanStatus"]
    lines.append('      <section aria-labelledby="lean-title" class="surface-section">')
    lines.append(
        '        <div class="section-heading"><p class="eyebrow">Lean status</p>'
        '<h2 id="lean-title">Lean status</h2></div>'
    )
    lines.append("        <ul>")
    lines.append(f"          <li>Lean theorems: <code>{_esc(ls['leanTheoremCount'])}</code></li>")
    lines.append(f"          <li>Lean sorries: <code>{_esc(ls['leanSorryCount'])}</code></li>")
    lines.append(
        f"          <li>MachLib core sorries: <code>{_esc(ls['machlibCoreSorryCount'])}</code></li>"
    )
    lines.append(
        f"          <li>MachLib discovered sorries: <code>{_esc(ls['machlibDiscoveredSorryCount'])}</code></li>"
    )
    lines.append("        </ul>")
    lines.append("      </section>")
    lines.append("    </main>")
    lines.append("    <footer>")
    lines.append(
        f'      <p>Byte-derived from <code>{_esc(pub_r0_artifact_id)}</code> ({_esc(pub_r0_date)}). '
        f'Navigate: <a href="../">monogate.net</a>.</p>'
    )
    lines.append("    </footer>")
    lines.append("  </body>")
    lines.append("</html>")
    lines.append("")
    return "\n".join(lines)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_page(
    *,
    pub_r0_payload: dict[str, Any] | None = None,
    output_path: Path | None = None,
) -> tuple[Path, str, str]:
    payload = pub_r0_payload or load_pub_r0_payload()
    html_text = render_html(
        payload["ledger"],
        pub_r0_artifact_id=payload["artifactId"],
        pub_r0_date=payload["date"],
    )
    out_path = output_path or (MONOGATE_NET / PAGE_RELATIVE_PATH)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_text, encoding="utf-8")
    return out_path, html_text, sha256_hex(html_text.encode("utf-8"))


def build_time_drift_check(
    *,
    pub_r0_payload: dict[str, Any] | None = None,
    page_path: Path | None = None,
) -> dict[str, Any]:
    payload = pub_r0_payload or load_pub_r0_payload()
    page = page_path or (MONOGATE_NET / PAGE_RELATIVE_PATH)
    expected_html = render_html(
        payload["ledger"],
        pub_r0_artifact_id=payload["artifactId"],
        pub_r0_date=payload["date"],
    )
    expected_sha = sha256_hex(expected_html.encode("utf-8"))
    actual_text = page.read_text(encoding="utf-8") if page.exists() else ""
    actual_sha = sha256_hex(actual_text.encode("utf-8")) if actual_text else ""
    return {
        "pagePath": str(page),
        "expectedSha256": expected_sha,
        "actualSha256": actual_sha,
        "drift": actual_sha != expected_sha,
    }


def post_deploy_probe(
    live_url: str = LIVE_URL,
    *,
    pub_r0_payload: dict[str, Any] | None = None,
    timeout_seconds: float = 10.0,
) -> dict[str, Any]:
    payload = pub_r0_payload or load_pub_r0_payload()
    expected_html = render_html(
        payload["ledger"],
        pub_r0_artifact_id=payload["artifactId"],
        pub_r0_date=payload["date"],
    )
    expected_sha = sha256_hex(expected_html.encode("utf-8"))
    result: dict[str, Any] = {
        "liveUrl": live_url,
        "expectedSha256": expected_sha,
        "actualSha256": None,
        "reachable": False,
        "drift": None,
        "error": None,
    }
    try:
        with urllib.request.urlopen(live_url, timeout=timeout_seconds) as response:  # nosec B310
            body = response.read()
        result["reachable"] = True
        result["actualSha256"] = sha256_hex(body)
        result["drift"] = result["actualSha256"] != expected_sha
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        result["error"] = str(exc)
    return result


def build_payload(
    *,
    pub_r0_payload: dict[str, Any] | None = None,
    page_path: Path | None = None,
    skip_drift_check: bool = False,
) -> dict[str, Any]:
    pub_r0_payload = pub_r0_payload or load_pub_r0_payload()
    ledger = pub_r0_payload["ledger"]
    expected_html = render_html(
        ledger,
        pub_r0_artifact_id=pub_r0_payload["artifactId"],
        pub_r0_date=pub_r0_payload["date"],
    )
    expected_sha = sha256_hex(expected_html.encode("utf-8"))
    if skip_drift_check:
        drift_state = {
            "pagePath": str(page_path) if page_path else str(MONOGATE_NET / PAGE_RELATIVE_PATH),
            "expectedSha256": expected_sha,
            "actualSha256": expected_sha,
            "drift": False,
            "checked": False,
        }
    else:
        drift_state = build_time_drift_check(
            pub_r0_payload=pub_r0_payload, page_path=page_path
        )
        drift_state["checked"] = True
    summary = {
        "pubR0ArtifactId": pub_r0_payload["artifactId"],
        "pubR0Date": pub_r0_payload["date"],
        "pageRelativePath": PAGE_RELATIVE_PATH,
        "liveUrl": LIVE_URL,
        "contentClassCount": len(CONTENT_CLASSES),
        "contentClasses": list(CONTENT_CLASSES),
        "expectedHtmlSha256": expected_sha,
        "expectedHtmlByteLength": len(expected_html.encode("utf-8")),
        "ledgerHeldLaneCount": len(ledger["heldLanes"]),
        "ledgerRetractedClaimCount": len(ledger["retractedClaims"]),
        "ledgerNegativeResultCount": len(ledger["negativeResults"]),
        "leanTheoremCount": ledger["leanStatus"]["leanTheoremCount"],
        "leanSorryCount": ledger["leanStatus"]["leanSorryCount"],
        "machlibCoreSorryCount": ledger["leanStatus"]["machlibCoreSorryCount"],
        "machlibDiscoveredSorryCount": ledger["leanStatus"]["machlibDiscoveredSorryCount"],
        "buildTimeDriftCheck": drift_state,
        "liveDeployExecuted": False,
        "postDeployProbePassed": False,
        "publicSurfaceUpdated": False,
        "pagePushedToRemote": False,
        "additionalContentClassAdded": False,
        "laptopOwnedRepoTouched": False,
    }
    return build_claim_flagged_packet(
        schema_version=SCHEMA_VERSION,
        artifact_id=ARTIFACT_ID,
        artifact_type="public_surface_read_parity_renderer",
        status=STATUS,
        date=DATE,
        summary=summary,
        claim_flags=CLAIM_FLAGS,
        true_claim_flags=TRUE_CLAIM_FLAGS,
        non_claims=NON_CLAIMS,
        extra={
            "pubR0Source": pub_r0_payload["artifactId"],
            "renderedHtmlSha256": expected_sha,
        },
    )


def validate_payload(payload: dict[str, Any]) -> None:
    if payload["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected schema")
    if payload["status"] != STATUS:
        raise ValueError("unexpected status")
    summary = payload["summary"]
    if summary["contentClassCount"] != 5:
        raise ValueError("content class count must be exactly 5")
    if list(summary["contentClasses"]) != list(CONTENT_CLASSES):
        raise ValueError("content classes must match CONTENT_CLASSES tuple")
    if summary["additionalContentClassAdded"] is not False:
        raise ValueError("no sixth content class may be added")
    if summary["pageRelativePath"] != PAGE_RELATIVE_PATH:
        raise ValueError("page relative path drift")
    if summary["liveUrl"] != LIVE_URL:
        raise ValueError("live url drift")
    if summary["expectedHtmlByteLength"] <= 0:
        raise ValueError("expected html must be non-empty")
    if summary["expectedHtmlSha256"] != payload["renderedHtmlSha256"]:
        raise ValueError("sha256 drift between summary and extra")
    for key in [
        "liveDeployExecuted",
        "postDeployProbePassed",
        "publicSurfaceUpdated",
        "pagePushedToRemote",
        "additionalContentClassAdded",
        "laptopOwnedRepoTouched",
    ]:
        if summary[key] is not False:
            raise ValueError(f"{key} must remain false")
    for key in TRUE_CLAIM_FLAGS:
        if payload["claimFlags"][key] is not True:
            raise ValueError(f"{key} must be true")
    for key, value in payload["claimFlags"].items():
        if key not in TRUE_CLAIM_FLAGS and value is not False:
            raise ValueError(f"{key} must remain false")


def build_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    return build_evidence_packet(
        artifact_id=payload["artifactId"],
        artifact_type=payload["artifactType"],
        semantic_strength="static_no_js_html_byte_derived_from_pub_r0_with_two_stage_drift_guard_no_live_deploy_claim",
        source=(
            f"python/results/pub_r1_public_surface_read_parity_renderer/"
            f"pub_r1_public_surface_read_parity_renderer_{STAMP}.json"
        ),
        summary=payload["summary"],
        claim_flags=payload["claimFlags"],
        non_claims=payload["nonClaims"],
    )


def build_feed(payload: dict[str, Any]) -> dict[str, Any]:
    return build_command_feed(
        feed_id="pub_r1_public_surface_read_parity_renderer_feed",
        date=DATE,
        status=payload["status"],
        next_action=(
            "The static no-JS page is rendered and committed locally; the build-time "
            "drift guard is green. Live deploy remains gated on a separate E5 human-authored "
            "deploy authorization artifact and an explicit per-action operator confirmation. "
            "After deploy, run pub_r1 post-deploy-probe against monogate.net/evidence-status/."
        ),
        claim_flags=payload["claimFlags"],
        fields={
            "pubR0ArtifactId": payload["summary"]["pubR0ArtifactId"],
            "pageRelativePath": payload["summary"]["pageRelativePath"],
            "liveUrl": payload["summary"]["liveUrl"],
            "contentClassCount": payload["summary"]["contentClassCount"],
            "expectedHtmlSha256": payload["summary"]["expectedHtmlSha256"],
            "expectedHtmlByteLength": payload["summary"]["expectedHtmlByteLength"],
            "buildTimeDriftCheckDrift": payload["summary"]["buildTimeDriftCheck"]["drift"],
            "liveDeployExecuted": payload["summary"]["liveDeployExecuted"],
            "postDeployProbePassed": payload["summary"]["postDeployProbePassed"],
            "publicSurfaceUpdated": payload["summary"]["publicSurfaceUpdated"],
            "pagePushedToRemote": payload["summary"]["pagePushedToRemote"],
            "laptopOwnedRepoTouched": payload["summary"]["laptopOwnedRepoTouched"],
        },
    )


def build_report(payload: dict[str, Any]) -> str:
    return render_markdown_report(
        title="PUB-R1 Public-Surface Read Parity Renderer",
        status=payload["status"],
        summary_rows=[
            ("PUB-R0 source", payload["summary"]["pubR0ArtifactId"]),
            ("page relative path", payload["summary"]["pageRelativePath"]),
            ("live URL", payload["summary"]["liveUrl"]),
            ("content classes", payload["summary"]["contentClassCount"]),
            ("expected HTML SHA-256", payload["summary"]["expectedHtmlSha256"][:12] + "…"),
            ("expected HTML bytes", payload["summary"]["expectedHtmlByteLength"]),
            (
                "build-time drift",
                payload["summary"]["buildTimeDriftCheck"]["drift"],
            ),
            ("live deploy executed", payload["summary"]["liveDeployExecuted"]),
            (
                "post-deploy probe passed",
                payload["summary"]["postDeployProbePassed"],
            ),
            ("public surface updated", payload["summary"]["publicSurfaceUpdated"]),
        ],
        sections=[
            (
                "Content Classes (exhaustive per r2 §2)",
                [f"- `{c}`" for c in payload["summary"]["contentClasses"]],
            ),
            (
                "Guardrails",
                [
                    "- static no-JS HTML, byte-derived from PUB-R0 canonical JSON",
                    "- build-time drift guard: sha256 of rendered HTML matches committed page bytes",
                    "- post-deploy probe: fetch live URL, sha256 compare; not run by this artifact",
                    "- no live deploy without E5 authorization + explicit per-action operator confirmation",
                    "- no sixth content class; no adjectives; no prose beyond canonical one-liners",
                    "- no held-lane reopen; no laptop-owned repo touch",
                ],
            ),
        ],
        non_claims=payload["nonClaims"],
    )


def build_outputs(
    out_dir: Path,
    report_dir: Path,
    evidence_dir: Path,
    command_feed_dir: Path,
    *,
    pub_r0_payload: dict[str, Any] | None = None,
    page_path: Path | None = None,
    skip_drift_check: bool = False,
) -> dict[str, Any]:
    payload = build_payload(
        pub_r0_payload=pub_r0_payload,
        page_path=page_path,
        skip_drift_check=skip_drift_check,
    )
    validate_payload(payload)
    evidence = build_evidence(payload)
    feed = build_feed(payload)
    result_path = out_dir / f"pub_r1_public_surface_read_parity_renderer_{STAMP}.json"
    report_path = report_dir / f"pub_r1_public_surface_read_parity_renderer_{STAMP}.md"
    evidence_path = evidence_dir / "pub_r1_public_surface_read_parity_renderer.json"
    feed_path = (
        command_feed_dir / f"pub_r1_public_surface_read_parity_renderer_feed_{STAMP}.json"
    )
    write_json(result_path, payload)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(payload), encoding="utf-8")
    write_json(evidence_path, evidence)
    write_json(feed_path, feed)
    return {
        "payload": payload,
        "result_path": str(result_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "feed_path": str(feed_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--write-page",
        action="store_true",
        help="Render and write the static HTML page to monogate-net/evidence-status/index.html",
    )
    parser.add_argument(
        "--drift-check",
        action="store_true",
        help="Compare the committed page bytes against a fresh render; non-zero exit on drift",
    )
    parser.add_argument(
        "--post-deploy-probe",
        action="store_true",
        help="Fetch the live URL and compare bytes; non-zero exit on drift or unreachable",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "python/results/pub_r1_public_surface_read_parity_renderer",
    )
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument(
        "--evidence-dir", type=Path, default=ROOT / "reports/evidence_packets"
    )
    parser.add_argument(
        "--command-feed-dir", type=Path, default=ROOT / "command_center_feeds"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.write_page:
        path, _, sha = write_page()
        print(f"PUB_R1_WROTE_PAGE {path} sha256={sha}")
        return 0
    if args.drift_check:
        result = build_time_drift_check()
        print(
            f"PUB_R1_DRIFT_CHECK drift={result['drift']} expected={result['expectedSha256'][:12]} actual={result['actualSha256'][:12]}"
        )
        return 1 if result["drift"] else 0
    if args.post_deploy_probe:
        result = post_deploy_probe()
        print(
            f"PUB_R1_POST_DEPLOY_PROBE reachable={result['reachable']} drift={result['drift']} error={result['error']}"
        )
        return 0 if (result["reachable"] and result["drift"] is False) else 1
    payload = build_payload(skip_drift_check=not (MONOGATE_NET / PAGE_RELATIVE_PATH).exists())
    validate_payload(payload)
    if args.build:
        build_outputs(
            args.out_dir,
            args.report_dir,
            args.evidence_dir,
            args.command_feed_dir,
            skip_drift_check=not (MONOGATE_NET / PAGE_RELATIVE_PATH).exists(),
        )
    print("PUB_R1_PUBLIC_SURFACE_READ_PARITY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
