#!/usr/bin/env python3
"""Build a local static inspector for EML IR v0 artifacts.

The inspector turns the existing EML IR pipeline output into a browser-readable
artifact: expression -> DAG -> replay timeline -> internal evidence card.
It is local-only and does not change compiler behavior or public savings
claims.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_ir_pipeline import BOUNDARIES, run_pipeline, validate_ir  # noqa: E402


INSPECTOR_BOUNDARIES = {
    **BOUNDARIES,
    "local_static_viewer": True,
    "external_network_required": False,
    "dag_savings_public_claim": False,
    "observatory_card_public_ready": False,
    "production_marketplace_modified": False,
}


def _plain_language_frame(frame: dict[str, Any]) -> str:
    state = frame["lifecycle_state"]
    guard = frame["guard_action"]
    kernel = frame["kernel_id"]
    if state == "INIT":
        return "The EML IR program enters the local replay runtime."
    if state == "READY":
        return "Stable DAG node identifiers are assigned before execution frames begin."
    if state == "RUNNING" and guard == "ANNOTATE":
        return f"The `{kernel}` node ran with an annotation because the prototype cannot prove this domain condition."
    if state == "RUNNING":
        return f"The `{kernel}` node ran as a static expression step."
    if state == "END":
        return "The output node was reached and the trace emitted an explicit END frame."
    if state == "PARKED":
        return "The replay packet parked at an explicit terminal boundary."
    return f"The frame entered lifecycle state `{state}`."


def _program_view(row: dict[str, Any]) -> dict[str, Any]:
    ir = row["ir"]
    validate_ir(ir)
    node_ids = {node["id"] for node in ir["nodes"]}
    edges = []
    for node in ir["nodes"]:
        for arg in node["args"]:
            if arg not in node_ids:
                raise ValueError(f"missing node edge source {arg}")
            edges.append({"from": arg, "to": node["id"], "op": node["op"]})
    reused_nodes = [
        {
            "id": node["id"],
            "op": node["op"],
            "source": node["source"],
            "reuse_count": node["reuse_count"],
        }
        for node in ir["nodes"]
        if node["reuse_count"] > 1
    ]
    guard_counts: dict[str, int] = {}
    timeline = []
    for frame in ir["replay_packet"]["frames"]:
        guard_counts[frame["guard_action"]] = guard_counts.get(frame["guard_action"], 0) + 1
        timeline.append(
            {
                "frame_id": frame["frame_id"],
                "tick": frame["monotonic_tick"],
                "state": frame["lifecycle_state"],
                "kernel_id": frame["kernel_id"],
                "guard_action": frame["guard_action"],
                "guard_reason": frame["guard_reason"],
                "replay_hash": frame["replay_hash"],
                "what_happened": _plain_language_frame(frame),
            }
        )
    return {
        "program_id": row["program_id"],
        "family": row["family"],
        "expression": row["expression"],
        "why": row["why"],
        "tree_superbest_nodes": ir["tree_superbest_nodes"],
        "dag_superbest_nodes": ir["dag_superbest_nodes"],
        "extra_superbest_savings_nodes": ir["extra_superbest_savings_nodes"],
        "tree_eml_nodes": ir["tree_eml_nodes"],
        "dag_eml_nodes": ir["dag_eml_nodes"],
        "node_count": len(ir["nodes"]),
        "edge_count": len(edges),
        "frame_count": ir["replay_packet"]["frame_count"],
        "terminal_state": ir["replay_packet"]["terminal_state"],
        "nodes": ir["nodes"],
        "edges": edges,
        "reused_nodes": reused_nodes,
        "lowering": ir["lowering"],
        "guard_counts": guard_counts,
        "timeline": timeline,
        "public_safety_note": (
            "Tree SuperBEST costs are the public-safe baseline. DAG/IR savings "
            "are internal prototype evidence until lowering semantics are reviewed."
        ),
    }


def build_inspector_model(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or run_pipeline()
    programs = [_program_view(row) for row in payload["programs"]]
    best = max(programs, key=lambda row: row["extra_superbest_savings_nodes"])
    total_frames = sum(row["frame_count"] for row in programs)
    return {
        "inspector_id": "eml_ir_inspector_v0_2026_05_25",
        "status": "EML_IR_INSPECTOR_READY",
        "date": "2026-05-25",
        "source_pipeline": payload["pipeline_id"],
        "program_count": len(programs),
        "total_replay_frames": total_frames,
        "best_program_id": best["program_id"],
        "best_extra_superbest_savings_nodes": best["extra_superbest_savings_nodes"],
        "programs": programs,
        "public_safe_mode": {
            "tree_superbest_public_safe": True,
            "dag_ir_savings_internal_prototype": True,
            "new_public_savings_claim": False,
        },
        "boundaries": INSPECTOR_BOUNDARIES,
    }


def build_observatory_card(model: dict[str, Any]) -> dict[str, Any]:
    return {
        "card_id": "eml_ir_inspector_v0_2026_05_25",
        "title": "EML IR Inspector v0",
        "status": "INTERNAL_EVIDENCE_CARD_READY",
        "surface": "eml_ir_substrate",
        "summary": "Local static inspector for expression DAGs, replay frames, guard annotations, and internal DAG savings evidence.",
        "source_pipeline": model["source_pipeline"],
        "program_count": model["program_count"],
        "total_replay_frames": model["total_replay_frames"],
        "best_program_id": model["best_program_id"],
        "evidence_paths": [
            "demo/eml_ir_inspector_v0_2026_05_25/index.html",
            "demo/eml_ir_inspector_v0_2026_05_25/inspector_model_2026_05_25.json",
            "reports/eml_ir_inspector_v0_2026_05_25.md",
        ],
        "internal_only": True,
        "public_ready": False,
        "marketplace_ready": False,
        "new_public_savings_claim": False,
        "deploy_performed": False,
        "package_publish_performed": False,
        "production_marketplace_modified": False,
    }


def build_action_queue(model: dict[str, Any]) -> dict[str, Any]:
    return {
        "queue_id": "eml_ir_inspector_action_queue_2026_05_25",
        "status": "ACTION_QUEUE_READY",
        "items": [
            {
                "id": "eml_ir_browser_bridge",
                "priority": "high",
                "action": "Wire the static inspector model into the Explorer UI behind an internal/prototype label.",
            },
            {
                "id": "eml_ir_lowering_contract",
                "priority": "high",
                "action": "Specify deterministic node ordering, replay hashing, primitive set, and tree-vs-DAG semantics.",
            },
            {
                "id": "eml_ir_capcard_candidate",
                "priority": "medium",
                "action": "Promote the inspector packet into a CapCard internal candidate only after claim-language review.",
            },
            {
                "id": "eml_ir_public_copy_gate",
                "priority": "medium",
                "action": "Keep DAG savings internal until the lowering pass is productized and public copy is synced.",
            },
        ],
        "internal_only": True,
        "deploy_performed": False,
        "package_publish_performed": False,
    }


def render_report(model: dict[str, Any]) -> str:
    lines = [
        "# EML IR Inspector v0",
        "",
        "Date: 2026-05-25",
        "",
        f"Status: `{model['status']}`",
        "",
        "This is the first local viewer packet for EML IR as inspectable bytecode. It turns the existing expression -> DAG -> replay pipeline into a static browser artifact.",
        "",
        "## Summary",
        "",
        f"- Programs: {model['program_count']}",
        f"- Total replay frames: {model['total_replay_frames']}",
        f"- Best internal prototype savings fixture: `{model['best_program_id']}`",
        f"- Extra DAG savings for best fixture: {model['best_extra_superbest_savings_nodes']} SuperBEST nodes",
        "",
        "## Program Table",
        "",
        "| Program | Family | Tree BEST | DAG BEST | Extra DAG Savings | Reused Nodes | Frames |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for program in model["programs"]:
        lines.append(
            f"| `{program['program_id']}` | {program['family']} | {program['tree_superbest_nodes']} | "
            f"{program['dag_superbest_nodes']} | {program['extra_superbest_savings_nodes']} | "
            f"{len(program['reused_nodes'])} | {program['frame_count']} |"
        )
    lines.extend(
        [
            "",
            "## What The Inspector Shows",
            "",
            "- Expression source and family.",
            "- IR DAG node cards and dependency edges.",
            "- Reused subexpressions and why they matter.",
            "- Replay timeline with lifecycle states, guard annotations, and hash neighborhoods.",
            "- Lowered Python and JavaScript sketches from the existing lowering pass.",
            "",
            "## Public Copy Boundary",
            "",
            "Tree SuperBEST costs remain the public-safe baseline. DAG/IR savings in this packet are internal prototype evidence and should not become public headline claims until the lowering contract and product surface are reviewed.",
            "",
            "## Files",
            "",
            "- `demo/eml_ir_inspector_v0_2026_05_25/index.html`",
            "- `demo/eml_ir_inspector_v0_2026_05_25/inspector_model_2026_05_25.json`",
            "- `demo/eml_ir_inspector_v0_2026_05_25/observatory_card_2026_05_25.json`",
            "- `demo/eml_ir_inspector_v0_2026_05_25/action_queue_2026_05_25.json`",
            "",
            "## Boundaries",
            "",
            "- Internal local static viewer only.",
            "- No deploy.",
            "- No package publish.",
            "- No compiler behavior changed.",
            "- No canonical SuperBEST row table changed.",
            "- No production marketplace modification.",
            "- No public theorem/proof/open-problem claim.",
            "",
        ]
    )
    return "\n".join(lines)


def _json_script(model: dict[str, Any]) -> str:
    return json.dumps(model, indent=2, sort_keys=True).replace("</", "<\\/")


def render_html(model: dict[str, Any]) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>EML IR Inspector v0</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #141414;
      --muted: #626a73;
      --line: #d8dde5;
      --panel: #f6f8fb;
      --accent: #0b6bcb;
      --guard: #985f00;
      --ok: #146c43;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: #ffffff;
    }}
    header {{
      padding: 28px clamp(18px, 4vw, 48px) 20px;
      border-bottom: 1px solid var(--line);
    }}
    h1 {{ margin: 0 0 8px; font-size: clamp(26px, 4vw, 42px); letter-spacing: 0; }}
    h2 {{ font-size: 20px; margin: 0 0 12px; }}
    h3 {{ font-size: 15px; margin: 0 0 8px; }}
    p {{ line-height: 1.55; }}
    main {{ padding: 24px clamp(18px, 4vw, 48px) 40px; }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 12px;
      margin: 18px 0 22px;
    }}
    .metric, .panel, .node, .frame {{
      border: 1px solid var(--line);
      background: var(--panel);
      border-radius: 8px;
    }}
    .metric {{ padding: 14px; }}
    .metric strong {{ display: block; font-size: 24px; }}
    .metric span {{ color: var(--muted); font-size: 13px; }}
    .layout {{
      display: grid;
      grid-template-columns: minmax(220px, 320px) 1fr;
      gap: 18px;
      align-items: start;
    }}
    .panel {{ padding: 16px; }}
    .program-list {{ display: grid; gap: 8px; }}
    button {{
      width: 100%;
      text-align: left;
      border: 1px solid var(--line);
      background: #fff;
      border-radius: 6px;
      padding: 10px;
      cursor: pointer;
      color: var(--ink);
    }}
    button.active {{ border-color: var(--accent); box-shadow: inset 3px 0 0 var(--accent); }}
    .chips {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0; }}
    .chip {{ border: 1px solid var(--line); border-radius: 999px; padding: 4px 9px; font-size: 12px; background: #fff; }}
    .chip.guard {{ color: var(--guard); }}
    .chip.ok {{ color: var(--ok); }}
    .nodes {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; }}
    .node {{ padding: 10px; min-height: 96px; }}
    .node code, .frame code {{ word-break: break-word; }}
    .timeline {{ display: grid; gap: 8px; }}
    .frame {{ padding: 10px; }}
    .frame strong {{ display: inline-block; min-width: 76px; }}
    pre {{
      margin: 0;
      overflow-x: auto;
      background: #111827;
      color: #f9fafb;
      border-radius: 8px;
      padding: 12px;
      font-size: 12px;
    }}
    .muted {{ color: var(--muted); }}
    .warning {{ border-left: 4px solid var(--guard); padding-left: 12px; }}
    @media (max-width: 820px) {{
      .layout {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>EML IR Inspector v0</h1>
    <p class="muted">Local static inspector for expression DAGs, SuperBEST tree-vs-DAG costs, replay frames, and guard annotations.</p>
  </header>
  <main>
    <section class="summary" id="summary"></section>
    <section class="layout">
      <aside class="panel">
        <h2>Programs</h2>
        <div class="program-list" id="program-list"></div>
      </aside>
      <section class="panel" id="detail"></section>
    </section>
  </main>
  <script type="application/json" id="inspector-data">{_json_script(model)}</script>
  <script>
    const model = JSON.parse(document.getElementById('inspector-data').textContent);
    const summary = document.getElementById('summary');
    const list = document.getElementById('program-list');
    const detail = document.getElementById('detail');
    let selected = model.programs[0].program_id;

    function metric(label, value) {{
      return `<div class="metric"><strong>${{value}}</strong><span>${{label}}</span></div>`;
    }}

    summary.innerHTML = [
      metric('programs', model.program_count),
      metric('replay frames', model.total_replay_frames),
      metric('best fixture', model.best_program_id),
      metric('extra DAG savings', model.best_extra_superbest_savings_nodes)
    ].join('');

    function renderList() {{
      list.innerHTML = model.programs.map(p => `
        <button class="${{p.program_id === selected ? 'active' : ''}}" data-program="${{p.program_id}}">
          <strong>${{p.program_id}}</strong><br>
          <span class="muted">${{p.family}} · Tree ${{p.tree_superbest_nodes}} · DAG ${{p.dag_superbest_nodes}}</span>
        </button>
      `).join('');
      list.querySelectorAll('button').forEach(button => {{
        button.addEventListener('click', () => {{
          selected = button.dataset.program;
          render();
        }});
      }});
    }}

    function renderDetail() {{
      const p = model.programs.find(item => item.program_id === selected);
      const reused = p.reused_nodes.length ? p.reused_nodes.map(n => `<span class="chip">${{n.id}} ${{n.op || 'input'}} reused ${{n.reuse_count}}x</span>`).join('') : '<span class="chip">No repeated subexpression</span>';
      const guardChips = Object.entries(p.guard_counts).map(([k, v]) => `<span class="chip ${{k === 'PASS' ? 'ok' : 'guard'}}">${{k}} ${{v}}</span>`).join('');
      detail.innerHTML = `
        <h2>${{p.program_id}}</h2>
        <p class="muted">${{p.why}}</p>
        <p><code>${{p.expression}}</code></p>
        <div class="chips">
          <span class="chip">Tree BEST ${{p.tree_superbest_nodes}}</span>
          <span class="chip">DAG BEST ${{p.dag_superbest_nodes}}</span>
          <span class="chip">Extra savings ${{p.extra_superbest_savings_nodes}}</span>
          <span class="chip">Frames ${{p.frame_count}}</span>
          ${{guardChips}}
        </div>
        <p class="warning">${{p.public_safety_note}}</p>
        <h3>Reused Subexpressions</h3>
        <div class="chips">${{reused}}</div>
        <h3>IR DAG Nodes</h3>
        <div class="nodes">
          ${{p.nodes.map(n => `
            <div class="node">
              <strong>${{n.id}}</strong> <span class="muted">${{n.kind}}</span><br>
              <code>${{n.source}}</code><br>
              <span class="muted">op=${{n.op || 'none'}} · reuse=${{n.reuse_count}} · args=${{n.args.join(', ') || 'none'}}</span>
            </div>
          `).join('')}}
        </div>
        <h3>Replay Timeline</h3>
        <div class="timeline">
          ${{p.timeline.map(f => `
            <div class="frame">
              <strong>${{f.state}}</strong>
              <span class="chip ${{f.guard_action === 'PASS' ? 'ok' : 'guard'}}">${{f.guard_action}}</span>
              <span class="muted">tick ${{f.tick}} · ${{f.kernel_id}}</span>
              <p>${{f.what_happened}}</p>
              <code>${{f.replay_hash.slice(0, 24)}}...</code>
            </div>
          `).join('')}}
        </div>
        <h3>Lowered Python Sketch</h3>
        <pre>${{p.lowering.python_source.replace(/[&<>]/g, ch => ({{'&':'&amp;','<':'&lt;','>':'&gt;'}}[ch]))}}</pre>
      `;
    }}

    function render() {{
      renderList();
      renderDetail();
    }}
    render();
  </script>
</body>
</html>
"""


def render_readme(model: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# EML IR Inspector v0",
            "",
            "Open `index.html` in a browser to inspect the local EML IR examples.",
            "",
            "This packet is internal-only. It shows DAG/IR savings as prototype evidence, not public headline claims.",
            "",
            "## Contents",
            "",
            "- `index.html` — static local inspector, no external network.",
            "- `inspector_model_2026_05_25.json` — machine-readable inspector model.",
            "- `observatory_card_2026_05_25.json` — internal evidence-card summary.",
            "- `action_queue_2026_05_25.json` — next steps for productizing the bridge.",
            "",
            "## Summary",
            "",
            f"- Programs: {model['program_count']}",
            f"- Replay frames: {model['total_replay_frames']}",
            f"- Best fixture: `{model['best_program_id']}`",
            "",
            "## Boundaries",
            "",
            "- No deploy.",
            "- No package publish.",
            "- No compiler behavior change.",
            "- No canonical SuperBEST row-table change.",
            "- No new public theorem/proof/open-problem claim.",
            "",
        ]
    )


def write_outputs(model: dict[str, Any], out_dir: Path, report_path: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "inspector_model_2026_05_25.json").write_text(
        json.dumps(model, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out_dir / "observatory_card_2026_05_25.json").write_text(
        json.dumps(build_observatory_card(model), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out_dir / "action_queue_2026_05_25.json").write_text(
        json.dumps(build_action_queue(model), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out_dir / "index.html").write_text(render_html(model), encoding="utf-8")
    (out_dir / "README.md").write_text(render_readme(model), encoding="utf-8")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_report(model), encoding="utf-8")


def validate_model(model: dict[str, Any]) -> None:
    if model["status"] != "EML_IR_INSPECTOR_READY":
        raise ValueError("inspector status mismatch")
    if model["program_count"] < 10:
        raise ValueError("expected at least 10 programs")
    if model["total_replay_frames"] <= model["program_count"]:
        raise ValueError("expected replay frames")
    if model["public_safe_mode"]["new_public_savings_claim"] is not False:
        raise ValueError("must not create public savings claim")
    for key, value in INSPECTOR_BOUNDARIES.items():
        if model["boundaries"].get(key) is not value:
            raise ValueError(f"boundary mismatch: {key}")
    for program in model["programs"]:
        node_ids = {node["id"] for node in program["nodes"]}
        for edge in program["edges"]:
            if edge["from"] not in node_ids or edge["to"] not in node_ids:
                raise ValueError("edge references missing node")
        if program["timeline"][-1]["state"] != "PARKED":
            raise ValueError("program must terminally park")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=ROOT / "demo/eml_ir_inspector_v0_2026_05_25")
    parser.add_argument("--report", type=Path, default=ROOT / "reports/eml_ir_inspector_v0_2026_05_25.md")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    model = build_inspector_model()
    validate_model(model)
    if args.strict:
        if model["best_extra_superbest_savings_nodes"] <= 0:
            raise SystemExit("strict mode requires positive internal DAG savings fixture")
        if model["boundaries"]["deploy_performed"] is not False:
            raise SystemExit("deploy must be false")
    write_outputs(model, args.out_dir, args.report)
    print("EML_IR_INSPECTOR_OK")
    print(
        "programs={program_count} frames={total_replay_frames} best={best_program_id} extra={best_extra_superbest_savings_nodes}".format(
            **model
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
