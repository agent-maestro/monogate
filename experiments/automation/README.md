# Research-automation experiments

Instruments for testing one claim about this project:

> **The inner loop of mathematical research (prove/refute a stated conjecture) is automating; the outer
> loop (select targets, judge significance, catch plausible-wrong and misformalized statements) is not.**

Full pre-registered protocol: [`PROTOCOL.md`](PROTOCOL.md). Firing specimens: [`SPECIMENS.md`](SPECIMENS.md).
Gate blindness: [`GATE_REGISTRY.md`](GATE_REGISTRY.md).

**Nothing here has been measured.** Every prediction slot in the protocol is empty by design — a bar is
committed before the measurement it judges, never after. The instruments were built by AI; the
experiments are run, and the predictions written, by the orchestrator.

## Arms

| arm | what it tests | status |
|---|---|---|
| **E1** | Intervention ledger | LIVE at commit |
| **E2** | AI-selected frontier ablation | NOT STARTED |
| **E3** | Trap set | NOT STARTED. Traps not authored |
| **E4** | External-statement formalization | NOT STARTED. No tooling built |
| **E5** | Open-problem attempt: `1/x ∉ EML` at any depth | NOT STARTED as an experiment. THE UNDERLYING WORK IS NOT NEW — see baseline below |

_5 arms, computed from PROTOCOL.md by `status.py`._

## Live now

E1 only. `ledger.py` logs interventions and findings; `ledger.py report` computes every ratio from the
files it just read — no number in this directory is transcribed by hand.

```
ledger.py log     --session S --arm baseline --kind direction --desc "..."
ledger.py finding --session S --arm baseline --class closure --desc "..." --artifact URL
ledger.py report
```

## What would make this program worthless

Stated up front, because each has a specific defence and the defences are the point:

| failure | defence |
|---|---|
| predictions written after seeing results | slots committed empty; amendments recorded, never silent |
| arm assignment following the results | `e2_schedule.json` frozen by hash at first E2 session |
| the answer key edited after scoring | key hashed into `manifest.json` before evaluation; mismatch is a hard failure |
| the system under test authoring its own traps | procedural, stated verbatim in PROTOCOL.md — **no gate can catch this** |
| sessions quietly not logged | partially: `SUSPECT` flag. **The gate is blind to a session never logged.** |
| an AI grading whether humans or AI caught each error | the retrospective is explicitly not automated; see `retrospective/TEMPLATE.md` |

The last three are the ones to watch. Two of them cannot be mechanised at all, and saying so here is
cheaper than discovering it in the results.
