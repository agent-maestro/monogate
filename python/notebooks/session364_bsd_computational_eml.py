import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.bsd_computational_eml import analyze_bsd_computational_eml
result = analyze_bsd_computational_eml()
with open(f'python/results/session364_bsd_computational_eml.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, default=str)
print(f'Session 364 OK')
