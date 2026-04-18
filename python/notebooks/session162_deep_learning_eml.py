"""Session 162 — Deep Learning (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.deep_learning_eml import analyze_deep_learning_eml
print(json.dumps(analyze_deep_learning_eml(), indent=2, default=str))
