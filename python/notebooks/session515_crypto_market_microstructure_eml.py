"""Session 515 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.crypto_market_microstructure_eml import analyze_crypto_market_microstructure_eml
print(json.dumps(analyze_crypto_market_microstructure_eml(), indent=2, default=str))
