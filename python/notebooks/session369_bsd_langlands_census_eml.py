import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.bsd_langlands_census_eml import analyze_bsd_langlands_census_eml
result = analyze_bsd_langlands_census_eml()
with open(f'python/results/session369_bsd_langlands_census_eml.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, default=str)
print(f'Session 369 OK')
