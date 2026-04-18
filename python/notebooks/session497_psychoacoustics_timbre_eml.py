"""Session 497 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.psychoacoustics_timbre_eml import analyze_psychoacoustics_timbre_eml
print(json.dumps(analyze_psychoacoustics_timbre_eml(), indent=2, default=str))
