"""Session 391 notebook"""
import json, sys
sys.path.insert(0, "python")
from monogate.frontiers.rdl_arxiv_draft_ii_eml import analyze_rdl_arxiv_draft_ii_eml
result = analyze_rdl_arxiv_draft_ii_eml()
print(json.dumps(result, indent=2, default=str))
