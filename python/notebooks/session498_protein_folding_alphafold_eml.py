"""Session 498 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.protein_folding_alphafold_eml import analyze_protein_folding_alphafold_eml
print(json.dumps(analyze_protein_folding_alphafold_eml(), indent=2, default=str))
