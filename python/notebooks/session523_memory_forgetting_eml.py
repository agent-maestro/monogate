"""Session 523 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.memory_forgetting_eml import analyze_memory_forgetting_eml
print(json.dumps(analyze_memory_forgetting_eml(), indent=2, default=str))
