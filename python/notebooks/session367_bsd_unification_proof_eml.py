import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.bsd_unification_proof_eml import analyze_bsd_unification_proof_eml
result = analyze_bsd_unification_proof_eml()
with open(f'python/results/session367_bsd_unification_proof_eml.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, default=str)
print(f'Session 367 OK')
