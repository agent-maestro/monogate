"""Session 516 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.neuroplasticity_learning_eml import analyze_neuroplasticity_learning_eml
print(json.dumps(analyze_neuroplasticity_learning_eml(), indent=2, default=str))
