"""Session 403 notebook"""
import json, sys
sys.path.insert(0, "python")
from monogate.frontiers.rdl_peer_review_sim_eml import analyze_rdl_peer_review_sim_eml
result = analyze_rdl_peer_review_sim_eml()
print(json.dumps(result, indent=2, default=str))
