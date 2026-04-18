"""Session 222 — eml4 fourier formal eml (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.eml4_fourier_formal_eml import analyze_eml4_fourier_formal_eml
print(json.dumps(analyze_eml4_fourier_formal_eml(), indent=2, default=str))
