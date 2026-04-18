"""Session 84 — QFT Interacting Deep: Wilson RG (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.qft_rg_deep_eml import analyze_qft_rg_deep_eml
print(json.dumps(analyze_qft_rg_deep_eml(), indent=2, default=str))
