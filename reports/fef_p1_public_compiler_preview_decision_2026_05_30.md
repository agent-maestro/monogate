# FEF-P1 Public Compiler Preview Decision

Date: 2026-05-30

Status: `FEF_P1_PUBLIC_COMPILER_PREVIEW_DECISION_RECORDED`

Decision: `select_monogate_forge_preview_package`

FEF-P1 chooses the smallest honest public shape for the Forge/eFrog
compiler preview. It selects a separate package name while keeping all
publication and public-readiness flags false.

## Selected Shape

- Package: `monogate-forge-preview`
- Distribution status: `not_created_not_published`
- Scope: minimum public compiler preview for selected eFrog -> EML -> Forge Python/JavaScript paths

## Option Matrix

| Option | Decision | Reason |
|---|---|---|
| `extend_monogate_package` | `rejected_for_now` | Lowest install friction, but it blurs the public math/optimization package with an immature compiler preview. |
| `monogate_forge_preview_package` | `selected` | Makes the preview explicit, bounded, and separate from both monogate and future Forge Pro. |
| `artifact_only_preview` | `fallback` | Safest if packaging takes longer, but less useful as a public compiler preview. |

## Allowed Preview Commands

- `monogate-forge-preview capabilities`: Print the bounded preview capability map and blocked claims.
- `monogate-forge-preview emit --target python examples/gaussian.py --out build/gaussian.py`: Run the selected source -> EML -> Forge Python preview path.
- `monogate-forge-preview emit --target javascript examples/gaussian.py --out build/gaussian.js`: Run the selected source -> EML -> Forge JavaScript preview path.
- `monogate-forge-preview check examples/gaussian.py --targets python,javascript`: Run deterministic sample-grid checks for the preview slice.
- `monogate-forge-preview packet examples/gaussian.py --targets python,javascript --out evidence/packet.json`: Emit a bounded evidence packet with all public claim flags false.

## Blocked Commands

- `monogate-forge-preview emit --target verilog`: Blocked until FPGA simulation/synthesis/live evidence exists for the public path.
- `monogate-forge-preview emit --target lean --claim-proof`: Blocked until checked proof status exists and no theorem stub is presented as proof.
- `monogate-forge-preview emit --target all`: Blocked because FEF-P0 only covers Python/JavaScript selected-slice evidence.
- `monogate-forge-preview prove-correct`: Blocked because compiler correctness and formal equivalence are not established.
- `monogate-forge-preview benchmark --claim-speedup`: Blocked because FEF-P1 records no public runtime performance claim.

## Boundary

- No package has been created or published.
- No public readiness claim.
- No compiler correctness or formal equivalence claim.
- No Verilog, Lean proof, zkproof, silicon, performance, or checkout claim.
