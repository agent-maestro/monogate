"""Session 382 notebook"""
import json, sys
sys.path.insert(0, "python")
from monogate.frontiers.rdl_numerical_campaign_eml import analyze_rdl_numerical_campaign_eml
result = analyze_rdl_numerical_campaign_eml()
print(json.dumps(result, indent=2, default=str))
