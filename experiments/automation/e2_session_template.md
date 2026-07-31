# E2 session pre-registration — session `<ID>`

**Fill the PRE-SESSION block and commit it BEFORE the session starts.** A session with no committed
pre-registration is not scorable and is recorded as excluded — excluded, not silently dropped, because
a study that quietly discards its unscorable sessions is choosing its own denominator.

## PRE-SESSION (before any work)

| field | value |
|---|---|
| session id | |
| date | |
| arm (from `e2_schedule.json`, do not choose) | `E2-ai` / `E2-human` |
| target named | |
| who named it | |
| expected finding | |
| predicted class | `closure` / `surprise` / `falsification` / `dead_end` |

**Contamination check** — tick both or the session is void:
- [ ] This arm's target was selected without sight of the other arm's target list for this period.
- [ ] The arm came from the committed schedule, not from a judgement made today.

## POST-SESSION (scored after)

| field | value |
|---|---|
| actual finding(s) | |
| actual class(es) | |
| prediction correct? | |
| artifact link | |

Log the session's interventions and findings with `ledger.py` using the arm above. The ledger, not this
file, is what `report` counts.
