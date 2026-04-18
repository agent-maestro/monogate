import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.bsd_self_referential_eml import analyze_bsd_self_referential_eml
result = analyze_bsd_self_referential_eml()
with open(f'python/results/session365_bsd_self_referential_eml.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, default=str)
print(f'Session 365 OK')
