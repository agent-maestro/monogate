"""Session 492 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.dark_energy_cosmological_constant_eml import analyze_dark_energy_cosmological_constant_eml
print(json.dumps(analyze_dark_energy_cosmological_constant_eml(), indent=2, default=str))
