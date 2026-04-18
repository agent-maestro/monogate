"""Session 95 — Finance Deep: Volatility & Risk (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.finance_deep_eml import analyze_finance_deep_eml
print(json.dumps(analyze_finance_deep_eml(), indent=2, default=str))
