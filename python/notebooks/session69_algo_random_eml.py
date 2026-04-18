"""Session 69 — Algorithmic Randomness in EML (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.algo_random_eml import analyze_algo_random_eml

result = analyze_algo_random_eml()
print(json.dumps(result, indent=2, default=str))
