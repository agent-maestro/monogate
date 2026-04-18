"""Session 378 notebook"""
import json, sys
sys.path.insert(0, "python")
from monogate.frontiers.rdl_normalization_lemma_eml import analyze_rdl_normalization_lemma_eml
result = analyze_rdl_normalization_lemma_eml()
print(json.dumps(result, indent=2, default=str))
