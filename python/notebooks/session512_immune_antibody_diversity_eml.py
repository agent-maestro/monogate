"""Session 512 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.immune_antibody_diversity_eml import analyze_immune_antibody_diversity_eml
print(json.dumps(analyze_immune_antibody_diversity_eml(), indent=2, default=str))
