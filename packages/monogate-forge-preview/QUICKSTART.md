# FEF-P2 Clean-Room Quickstart

This quickstart exercises the local `monogate-forge-preview` scaffold from a
fresh virtual environment. It does not require sibling private repos.

```bash
cd packages/monogate-forge-preview
python -m venv /tmp/monogate_forge_preview_cleanroom
/tmp/monogate_forge_preview_cleanroom/bin/python -m pip install --upgrade pip
/tmp/monogate_forge_preview_cleanroom/bin/python -m pip install -e .
/tmp/monogate_forge_preview_cleanroom/bin/monogate-forge-preview capabilities
/tmp/monogate_forge_preview_cleanroom/bin/monogate-forge-preview emit --target python examples/gaussian.py --out build/gaussian.py
/tmp/monogate_forge_preview_cleanroom/bin/monogate-forge-preview emit --target javascript examples/gaussian.py --out build/gaussian.mjs
/tmp/monogate_forge_preview_cleanroom/bin/monogate-forge-preview check examples/gaussian.py --targets python,javascript
/tmp/monogate_forge_preview_cleanroom/bin/monogate-forge-preview packet examples/gaussian.py --targets python,javascript --out evidence/packet.json
```

Expected result:

- capabilities prints Python/JavaScript only
- Python and JavaScript targets are emitted
- deterministic check passes
- evidence packet is written with public/package/correctness/proof/performance
  claim flags false

Blocked:

- Verilog
- Lean proof claims
- zkproof
- target all
- silicon
- compiler correctness
- runtime speedup claims
- checkout/product claims
