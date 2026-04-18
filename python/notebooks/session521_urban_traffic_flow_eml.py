"""Session 521 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.urban_traffic_flow_eml import analyze_urban_traffic_flow_eml
print(json.dumps(analyze_urban_traffic_flow_eml(), indent=2, default=str))
