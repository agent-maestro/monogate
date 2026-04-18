"""Session 518 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.volcanic_eruption_dynamics_eml import analyze_volcanic_eruption_dynamics_eml
print(json.dumps(analyze_volcanic_eruption_dynamics_eml(), indent=2, default=str))
