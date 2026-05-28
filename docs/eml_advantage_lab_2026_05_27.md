# EML Advantage Lab

Date: 2026-05-27

The EML Advantage Lab is the new centerline for the EML return phase. It asks a
bounded question:

```text
Where does EML actually help, and where does standard math still win?
```

It synthesizes evidence from:

- R10 cost/stability packets
- R10B runtime bakeoff packets
- R10C scoped semantic proof packets
- R10E formal compiler proof skeleton
- A5 symbolic-regression template search

## Output

The lab emits `EML Advantage Packet v0` records with these axes:

- compression
- runtime
- finite-precision stability
- lowering recommendation
- proof status
- symbolic-search status

Each packet is classified as:

- `eml_win`
- `standard_win`
- `mixed`
- `research_only`
- `blocked`

## Boundary

The lab does not claim general EML superiority. It does not claim public
performance, savings, compiler correctness, theorem discovery, RH proof,
zeta-zero discovery, hardware measurement, or deployment.

The purpose is to find the zones where EML may be uniquely useful without
hiding the zones where it is not.

