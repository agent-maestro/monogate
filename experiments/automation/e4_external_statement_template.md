# E4 external-statement formalization — run `<ID>`

**Status: no tooling built.** This template is the whole instrument for now, deliberately: E4's risk is
not mechanical, and a script would give it a false air of measurement.

## Source

| field | value |
|---|---|
| paper citation | |
| DOI / arXiv | |
| exact statement being formalized (quoted, verbatim) | |
| why this statement | |

## Formalization

| field | value |
|---|---|
| Lean statement | |
| file + line | |
| formalized by | |

## Adversarial statement review

**Reviewed by a party that did NOT write the formalization.** Self-review of statement fidelity is the
same vacuous test as self-authored traps, one level up — the process that misread the paper is the
process being asked whether it misread the paper.

| field | value |
|---|---|
| reviewer | |
| reviewer is not the author | ☐ confirmed |
| different model instance / human | |

Checklist — each answered in writing, not ticked:

1. **Does the Lean statement mean the paper's claim?** State the paper's claim in your own words, then
   state what the Lean statement says, then compare. Do not read them side by side first.
2. What does the Lean statement permit that the paper's claim forbids?
3. What does the paper's claim assert that the Lean statement does not?
4. Are the quantifiers in the same order, and over the same domains?
5. Are the hypotheses the paper's, or convenient weakenings that make the proof go through?
6. If the Lean statement is trivially true (e.g. vacuous hypotheses), would this review have noticed?

| verdict | `FAITHFUL` / `MISFORMALIZED` / `INCONCLUSIVE` |
|---|---|
| notes | |
