# AMENDMENT 4 firing specimen — `preventive` is a required ternary

Two files, one entry, one field of difference. **A gate with no firing specimen is unvalidated, not
passing**, and this pair is what validates the AMENDMENT 4 check.

```
python3 check_ledger_append_only.py --ledger-dir specimens/amendment4   # run against each in turn
```

| file | entry | expected |
|---|---|---|
| `convicts.json` | catch-class, timestamped after the amendment, **no `preventive` key** | **FAIL** |
| `acquits.json` | the same entry, plus `"preventive": false` | **PASS** |

`convicts.json` uses a timestamp one hour in the future so the specimen stays on the convicting side of
the pinned cutoff no matter when it is run. Without that, the specimen would expire silently and
re-run as a pass — a specimen that stops firing is worse than none, because it reports success.

## What this specimen does NOT show, and why a third case is unnecessary

It does not show that **pre**-amendment entries survive. That is checked against the live ledger
instead, which carries 18 sessions and many catch entries with no `preventive` key at all: the gate
must pass there, and does. A synthetic third fixture would test the same branch with less evidence
than the real data already provides.

## Why the amendment exists

`preventive` was optional under AMENDMENT 3. A cross-derivation on 2026-07-31 measured **3** entries
carrying the flag against **13** whose descriptions named a decline, a refusal, or a
stop-before-execution — a **4× undercount**. An optional flag is applied by whoever remembers it, and
the party writing the entry is the party a high preventive count flatters.

**Absence and `false` are different facts, and only one of them is a measurement.** The amendment makes
absence impossible going forward; it does not touch the past, where the field stays `undeclared` and
any tally must derive from descriptions.
