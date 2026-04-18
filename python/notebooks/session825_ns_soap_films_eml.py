import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.ns_soap_films_eml import analyze_ns_soap_films_eml
result = analyze_ns_soap_films_eml()
print(json.dumps(result, indent=2, default=str))