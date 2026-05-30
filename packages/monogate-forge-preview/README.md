# monogate-forge-preview

Local scaffold for the FEF-P2 Forge/eFrog compiler-preview quickstart.

This package is not published. It is a bounded clean-room preview scaffold for
one selected fixture path:

```text
selected source fixture -> preview EML surface -> Python/JavaScript emitters
-> deterministic checks -> evidence packet
```

## Allowed

- `monogate-forge-preview capabilities`
- `monogate-forge-preview emit --target python examples/gaussian.py --out build/gaussian.py`
- `monogate-forge-preview emit --target javascript examples/gaussian.py --out build/gaussian.js`
- `monogate-forge-preview check examples/gaussian.py --targets python,javascript`
- `monogate-forge-preview packet examples/gaussian.py --targets python,javascript --out evidence/packet.json`

## Blocked

- Verilog
- Lean proof claims
- zkproof
- `--target all`
- silicon claims
- compiler correctness claims
- runtime speedup claims
- paid checkout/product claims

This scaffold is a bridge toward a public package. It is not a public release.
