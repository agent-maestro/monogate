"""Session 468 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.open_questions_after_gaps_eml import analyze_open_questions_after_gaps_eml
print(json.dumps(analyze_open_questions_after_gaps_eml(), indent=2, default=str))
