import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.bsd_millennium_implications_eml import analyze_bsd_millennium_implications_eml
result = analyze_bsd_millennium_implications_eml()
with open(f'python/results/session368_bsd_millennium_implications_eml.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, default=str)
print(f'Session 368 OK')
