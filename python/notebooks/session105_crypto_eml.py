"""Session 105 — Cryptography & Information Security (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.crypto_eml import analyze_crypto_eml
print(json.dumps(analyze_crypto_eml(), indent=2, default=str))
