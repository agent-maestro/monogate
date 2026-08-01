# AMENDMENT 6 dual-labelling — specimen, and the reason the live record is empty

```
python3 ledger.py dual --session <id> --arm <arm> --index <n> --kind <k> --actor <a> [--note …]
```

**The instrument was smoke-tested and then its output was DELETED.** On first use the AI supplied a
label to check the plumbing — and an AI-supplied "human" label is **vacuous and worse than none**: it
manufactures agreement with the very labeller it was built to audit, and that agreement figure would
then be quoted as the correction factor for the by-actor ratio. The test label was removed rather than
kept as "just a smoke test", because a contaminated calibration instrument reports confidently.

So: `ledger/dual/` does not exist yet, and `report` prints
**`INTER-RATER AGREEMENT: [UNAVAILABLE] — not zero agreement, UNMEASURED`**, per house rule 4.

## What the tool enforces, and what it cannot

**Enforces:**
* labels land in `ledger/dual/<session>.json`, **never inside the entry** — a second labeller who can
  edit the first labeller's record is not a second labeller;
* **one label per entry**, refused thereafter — a label revised after seeing the disagreement is not
  an independent label;
* the index must exist in the session being labelled.

**Cannot enforce:** who is typing. The command prints a warning to stderr saying so on every
invocation. This is an attestation, the same grade as `actor`, and belongs on the same list of limits
no gate here can cover.

## Why the disagreement rate is the point

The agreement figure corrects the by-actor ratio. But **the disagreements are the more interesting
output**: *how differently do the human and the AI perceive who did what* is a sharper question than the
ratio it corrupts, and it is one no amount of additional n can answer without a second rater.
