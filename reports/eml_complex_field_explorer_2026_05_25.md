# EML Complex Field Explorer

Date: 2026-05-25

Status: `LOCAL_VISUAL_PROTOTYPE_READY`

## Result

Explorer now has a `field` tab for complex-domain coloring. It renders
local canvas plots for:

- `f(z) = z`
- `f(z) = z^2`
- `f(z) = exp(z)`
- `f(z) = ln(z)`
- `f(z) = eml(z, 1)`
- `f(z) = eml(z, z + 2)`

Color represents output phase. Contours show magnitude bands. Optional
overlays mark axes, unit circle, log branch behavior, and exp-style
periodic cues.

## Why This Matters

This gives Monogate a visual grammar for inspectable complex
computation:

```text
complex input plane -> function -> phase color -> magnitude contour -> symmetry cue
```

That grammar pairs naturally with the EML IR Inspector:

```text
expression -> IR DAG -> replay frames -> visual field intuition
```

## Boundary

The modular discriminant/domain-coloring article is used as visual
inspiration only. This prototype does not implement the modular
discriminant, does not make physics claims, and does not create a proof
or modular-form result.

No deploy, package publish, marketplace modification, PETAL/API upload,
Hugging Face upload, or hardware action occurred.
