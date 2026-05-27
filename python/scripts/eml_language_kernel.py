#!/usr/bin/env python3
"""EML Language Kernel v0 parser and normalizer.

This is a front door for EML examples. It normalizes a tiny line-oriented
language into EML Expression Packet v0 without changing Forge/compiler
behavior or making public savings/proof claims.
"""

from __future__ import annotations

import argparse
import ast
import copy
import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "python") not in sys.path:
    sys.path.insert(0, str(ROOT / "python"))

from scripts.eml_packet_builder import DEFAULT_CLAIM_FLAGS, validate_expression_packet  # noqa: E402

DATE = "2026-05-27"
SCHEMA_VERSION = "monogate.eml_language_kernel.v0"
RESULT_SCHEMA_VERSION = "monogate.eml_language_kernel.result.v0"


class EmlLanguageError(ValueError):
    pass


def _parse_expr(text: str) -> ast.AST:
    return ast.parse(text, mode="eval").body


def _unparse(node: ast.AST) -> str:
    return ast.unparse(ast.fix_missing_locations(node))


class _Normalizer(ast.NodeTransformer):
    def __init__(self, lets: dict[str, ast.AST]):
        self.lets = lets

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id in self.lets:
            return copy.deepcopy(self.lets[node.id])
        return node

    def visit_Call(self, node: ast.Call) -> ast.AST:
        self.generic_visit(node)
        if not isinstance(node.func, ast.Name):
            return node
        if node.func.id == "softplus":
            if len(node.args) != 1:
                raise EmlLanguageError("softplus expects one argument")
            x = node.args[0]
            return ast.Call(
                func=ast.Name(id="ln", ctx=ast.Load()),
                args=[
                    ast.BinOp(
                        left=ast.Constant(value=1),
                        op=ast.Add(),
                        right=ast.Call(func=ast.Name(id="exp", ctx=ast.Load()), args=[x], keywords=[]),
                    )
                ],
                keywords=[],
            )
        if node.func.id == "eml":
            if len(node.args) != 2:
                raise EmlLanguageError("eml expects two arguments")
            x, y = node.args
            return ast.BinOp(
                left=ast.Call(func=ast.Name(id="exp", ctx=ast.Load()), args=[x], keywords=[]),
                op=ast.Sub(),
                right=ast.Call(func=ast.Name(id="ln", ctx=ast.Load()), args=[y], keywords=[]),
            )
        return node


def normalize_expression(text: str, lets: dict[str, ast.AST] | None = None) -> str:
    tree = _parse_expr(text)
    normalized = _Normalizer(lets or {}).visit(tree)
    return _unparse(normalized)


def _expr_ast(node: ast.AST) -> dict[str, Any]:
    if isinstance(node, ast.Name):
        return {"kind": "var", "name": node.id}
    if isinstance(node, ast.Constant):
        return {"kind": "const", "value": node.value}
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return {"kind": "op", "op": "neg", "args": [_expr_ast(node.operand)]}
    if isinstance(node, ast.BinOp):
        op = {
            ast.Add: "add",
            ast.Sub: "sub",
            ast.Mult: "mul",
            ast.Div: "div",
            ast.Pow: "pow",
        }.get(type(node.op))
        if op is None:
            raise EmlLanguageError(f"unsupported binary operator: {type(node.op).__name__}")
        return {"kind": "op", "op": op, "args": [_expr_ast(node.left), _expr_ast(node.right)]}
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        return {"kind": "op", "op": node.func.id, "args": [_expr_ast(arg) for arg in node.args]}
    raise EmlLanguageError(f"unsupported AST node: {ast.dump(node)}")


def _parse_input(line: str) -> dict[str, Any]:
    match = re.match(
        r"^input\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s+unit\s+(?P<unit>\S+)(?:\s+range\s+(?P<min>-?\d+(?:\.\d+)?)\s+(?P<max>-?\d+(?:\.\d+)?))?$",
        line,
    )
    if not match:
        raise EmlLanguageError(f"invalid input declaration: {line}")
    item: dict[str, Any] = {"name": match.group("name"), "unit": match.group("unit")}
    if match.group("min") is not None:
        item["range"] = {"min": float(match.group("min")), "max": float(match.group("max"))}
    return item


def _parse_guard(text: str, lets: dict[str, ast.AST]) -> dict[str, Any]:
    match = re.match(r"^(positive|nonzero|range)\((.*)\)$", text.strip())
    if not match:
        raise EmlLanguageError(f"invalid guard: {text}")
    kind, body = match.group(1), match.group(2)
    if kind == "range":
        parts = [part.strip() for part in body.split(",")]
        if len(parts) != 3:
            raise EmlLanguageError("range guard expects input, min, max")
        return {
            "kind": "range",
            "expression": parts[0],
            "min": float(parts[1]),
            "max": float(parts[2]),
        }
    normalized = normalize_expression(body, lets)
    return {"kind": kind, "expression": normalized}


def parse_program(source: str) -> dict[str, Any]:
    program_id = ""
    family = ""
    meaning = ""
    source_repo = "monogate"
    inputs: list[dict[str, Any]] = []
    lets: list[dict[str, str]] = []
    let_asts: dict[str, ast.AST] = {}
    guards: list[dict[str, Any]] = []
    return_expr = ""

    for raw_line in source.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("program "):
            program_id = line.split(None, 1)[1].strip()
        elif line.startswith("family "):
            family = line.split(None, 1)[1].strip()
        elif line.startswith("meaning "):
            meaning = line.split(None, 1)[1].strip()
        elif line.startswith("source_repo "):
            source_repo = line.split(None, 1)[1].strip()
        elif line.startswith("input "):
            inputs.append(_parse_input(line))
        elif line.startswith("let "):
            match = re.match(r"^let\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$", line)
            if not match:
                raise EmlLanguageError(f"invalid let declaration: {line}")
            name, expr = match.group(1), match.group(2)
            normalized = normalize_expression(expr, let_asts)
            let_asts[name] = _parse_expr(normalized)
            lets.append({"name": name, "expression": expr, "normalized_expression": normalized})
        elif line.startswith("guard "):
            guards.append(_parse_guard(line.split(None, 1)[1], let_asts))
        elif line.startswith("return "):
            return_expr = line.split(None, 1)[1].strip()
        else:
            raise EmlLanguageError(f"unknown declaration: {line}")

    if not program_id or not family or not return_expr or not inputs:
        raise EmlLanguageError("program, family, input, and return are required")
    normalized = normalize_expression(return_expr, let_asts)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "program_id": program_id,
        "family": family,
        "source": source,
        "physical_meaning": meaning or f"EML language program {program_id}.",
        "source_repo": source_repo,
        "normalized_expression": normalized,
        "inputs": inputs,
        "guards": guards,
        "lets": lets,
        "ast": _expr_ast(_parse_expr(normalized)),
        "claim_flags": dict(DEFAULT_CLAIM_FLAGS),
        "nonClaims": [
            "EML Language Kernel output is candidate-only.",
            "Normalization does not change Forge/compiler behavior.",
            "No public savings, formal verification, or theorem claim is made.",
        ],
    }


def language_to_expression_packet(program: dict[str, Any]) -> dict[str, Any]:
    packet = {
        "schemaVersion": "monogate.eml_expression_packet.v0",
        "program_id": program["program_id"],
        "family": program["family"],
        "expression": program["normalized_expression"],
        "inputs": [item["name"] for item in program["inputs"]],
        "units": {item["name"]: item["unit"] for item in program["inputs"]},
        "safe_ranges": {
            item["name"]: item["range"]
            for item in program["inputs"]
            if "range" in item
        },
        "physical_meaning": program["physical_meaning"],
        "source_repo": program["source_repo"],
        "simulated_trace_samples": [],
        "claim_flags": dict(DEFAULT_CLAIM_FLAGS),
        "language_kernel": {
            "schemaVersion": SCHEMA_VERSION,
            "guards": program["guards"],
            "lets": program["lets"],
            "source_program_id": program["program_id"],
        },
    }
    validate_expression_packet(packet)
    return packet


def render_report(program: dict[str, Any], packet: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"# EML Language Kernel Result: {program['program_id']}",
            "",
            f"Date: {DATE}",
            "",
            "Status: `EML_LANGUAGE_KERNEL_CANDIDATE_PASS`",
            "",
            "## Normalized Expression",
            "",
            f"`{program['normalized_expression']}`",
            "",
            "## Guards",
            "",
            *[
                f"- `{guard['kind']}` on `{guard['expression']}`"
                for guard in program["guards"]
            ],
            "",
            "## Emitted Packet",
            "",
            f"- Program: `{packet['program_id']}`",
            f"- Inputs: `{', '.join(packet['inputs'])}`",
            f"- Safe ranges: `{len(packet['safe_ranges'])}`",
            "",
            "## Non-Claims",
            "",
            "- No Forge/compiler behavior change.",
            "- No public savings claim.",
            "- No formal verification or theorem claim.",
            "- No package publish or deploy.",
            "",
        ]
    )


def build_one(source_path: Path, out_dir: Path, packet_dir: Path, report_dir: Path) -> dict[str, Any]:
    program = parse_program(source_path.read_text(encoding="utf-8"))
    packet = language_to_expression_packet(program)
    stamp = DATE.replace("-", "_")
    out_dir.mkdir(parents=True, exist_ok=True)
    packet_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    program_path = out_dir / f"{program['program_id']}_language_{stamp}.json"
    packet_path = packet_dir / f"{program['program_id']}_expression_packet_{stamp}.json"
    report_path = report_dir / f"{program['program_id']}_language_kernel_{stamp}.md"
    program_path.write_text(json.dumps(program, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    packet_path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(program, packet), encoding="utf-8")
    return {
        "program": program,
        "packet": packet,
        "paths": {
            "language": str(program_path),
            "expression_packet": str(packet_path),
            "report": str(report_path),
        },
    }


def build_fixtures(fixtures_dir: Path, out_dir: Path, packet_dir: Path, report_dir: Path) -> dict[str, Any]:
    built = [build_one(path, out_dir, packet_dir, report_dir) for path in sorted(fixtures_dir.glob("*.eml"))]
    manifest = {
        "schemaVersion": "monogate.eml_language_kernel_fixture_manifest.v0",
        "date": DATE,
        "status": "EML_LANGUAGE_KERNEL_FIXTURES_PASS",
        "count": len(built),
        "programs": [
            {
                "program_id": item["program"]["program_id"],
                "family": item["program"]["family"],
                "normalized_expression": item["program"]["normalized_expression"],
                "guard_count": len(item["program"]["guards"]),
                "let_count": len(item["program"]["lets"]),
                "paths": item["paths"],
            }
            for item in built
        ],
        "claimFlags": dict(DEFAULT_CLAIM_FLAGS),
    }
    manifest_path = out_dir / f"eml_language_kernel_manifest_{DATE.replace('-', '_')}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"manifest": manifest, "manifest_path": str(manifest_path), "built": built}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--program", type=Path, help="Single .eml program")
    parser.add_argument("--fixtures-dir", type=Path, default=ROOT / "python/fixtures/eml_language_programs")
    parser.add_argument("--build-fixtures", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "python/results/eml_language_kernel")
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "python/results/eml_language_packets")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports/eml_language_kernel")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    if args.build_fixtures:
        result = build_fixtures(args.fixtures_dir, args.out_dir, args.packet_dir, args.report_dir)
        if args.strict and result["manifest"]["count"] < 5:
            raise SystemExit("strict mode requires at least 5 EML language fixtures")
        print("EML_LANGUAGE_KERNEL_FIXTURES_OK")
        print(f"programs={result['manifest']['count']}")
        print(f"manifest={result['manifest_path']}")
        return 0

    if not args.program:
        raise SystemExit("--program or --build-fixtures is required")
    built = build_one(args.program, args.out_dir, args.packet_dir, args.report_dir)
    print("EML_LANGUAGE_KERNEL_OK")
    print(json.dumps(built["paths"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

