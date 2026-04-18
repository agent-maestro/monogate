"""Session 169 — notebook script"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.financial_math_eml import analyze_financial_math_eml
print(json.dumps(analyze_financial_math_eml(), indent=2, default=str))
