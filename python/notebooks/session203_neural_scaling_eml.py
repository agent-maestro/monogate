"""Session 203 — Neural Scaling Laws & ML Emergence (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.neural_scaling_eml import analyze_neural_scaling_eml
print(json.dumps(analyze_neural_scaling_eml(), indent=2, default=str))
