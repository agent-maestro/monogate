"""Session 336 — Marine Ecology"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.marine_ecology_eml import analyze_marine_ecology_eml
result = analyze_marine_ecology_eml()
print(json.dumps(result, indent=2, default=str))
