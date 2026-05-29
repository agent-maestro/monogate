# EML Advantage Product Direction Sprints

Date: 2026-05-29

Status: `EML_ADVANTAGE_PRODUCT_DIRECTION_SPRINTS_PASS`

PCC10 is a clean research pause point. This artifact turns that pause into three focused implementation sprints.
It does not add a new EML result, proof, compiler claim, engine claim, or deployment.

| Order | Sprint | Lane | Risk | Why |
|---:|---|---|---|---|
| 1 | `forge_efrog_packet_export_ux` | `compiler_decompiler` | `Medium` | It is least blocked, uses clean existing artifacts, and turns EML research into an inspectable developer workflow. |
| 2 | `mge_glassbox_evidence_mount` | `engine_runtime` | `MediumHigh` | It connects the research to the visible engine experience, but the dirty engine worktree currently has unrelated uncommitted edits, so the first pass should be a handoff/spec artifact. |
| 3 | `machlib_small_witness_selection` | `formal_methods` | `High` | It is valuable, but proof work should begin only after local MachLib inspection confirms the exact namespace and existing theorem surface. |

## Recommended Order

### 1. Forge/eFrog Packet Export UX

Turn the existing Forge/eFrog roundtrip and semantic comparison work into a developer-facing packet export workflow.

Deliverables:
- private packet export spec
- CLI or builder preset for source -> EML -> Forge target evidence
- fixture-backed export example
- claim-boundary report

Blocked claims:
- compiler correctness
- formal equivalence
- broad EML advantage
- runtime performance

### 2. Monogate Engine / Glass Box Evidence Mount

Mount selected EML Advantage and compiler/decompiler evidence into Glass Box as reviewable packets or HUD-linked traces.

Deliverables:
- engine handoff packet
- Glass Box evidence adapter spec
- non-overlapping implementation note for the dirty engine worktree
- private command cockpit row

Blocked claims:
- production runtime
- certified safety
- game-engine completeness
- automatic approval

### 3. MachLib Small Witness Selection

Select one narrow, low-risk EML witness candidate for a proof attempt after inspecting the current MachLib surface.

Deliverables:
- witness candidate decision
- domain assumptions
- Lean file touch-plan
- proof or blocked-proof report after implementation sprint

Blocked claims:
- MachLib witness completion before Lean passes
- general EML correctness
- Forge compiler correctness
- formal equivalence

Recommended witness candidate:

- name: `subtraction_boundary`
- statement: `eml(log(v), exp(u)) = v - u under v > 0`
- reason: It is cleaner than log reconstruction, expresses a useful Atlas boundary, and depends on explicit domain assumptions.

## Boundary

- Private direction plan only.
- No Forge/eFrog behavior change.
- No Monogate Engine behavior change.
- No MachLib proof claim.
- No deployment or public-readiness claim.
