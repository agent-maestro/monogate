"""Session 390 notebook"""
import json, sys
sys.path.insert(0, "python")
from monogate.frontiers.rdl_arxiv_draft_i_eml import analyze_rdl_arxiv_draft_i_eml
result = analyze_rdl_arxiv_draft_i_eml()
print(json.dumps(result, indent=2, default=str))
