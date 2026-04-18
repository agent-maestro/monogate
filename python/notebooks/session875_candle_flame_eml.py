import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.candle_flame_eml import analyze_candle_flame_eml
result = analyze_candle_flame_eml()
print(json.dumps(result, indent=2, default=str))