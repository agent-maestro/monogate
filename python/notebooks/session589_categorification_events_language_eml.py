import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.categorification_events_language_eml import analyze_categorification_events_language_eml
result = analyze_categorification_events_language_eml()
print(json.dumps(result, indent=2, default=str))
