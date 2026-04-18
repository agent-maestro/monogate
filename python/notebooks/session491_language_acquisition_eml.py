"""Session 491 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.language_acquisition_eml import analyze_language_acquisition_eml
print(json.dumps(analyze_language_acquisition_eml(), indent=2, default=str))
