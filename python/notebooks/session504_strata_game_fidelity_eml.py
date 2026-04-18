"""Session 504 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.strata_game_fidelity_eml import analyze_strata_game_fidelity_eml
print(json.dumps(analyze_strata_game_fidelity_eml(), indent=2, default=str))
