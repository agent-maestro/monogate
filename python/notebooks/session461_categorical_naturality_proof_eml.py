"""Session 461 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.categorical_naturality_proof_eml import analyze_categorical_naturality_proof_eml
print(json.dumps(analyze_categorical_naturality_proof_eml(), indent=2, default=str))
