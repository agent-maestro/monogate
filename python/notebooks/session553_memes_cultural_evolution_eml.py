import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.memes_cultural_evolution_eml import analyze_memes_cultural_evolution_eml
result = analyze_memes_cultural_evolution_eml()
print(json.dumps(result, indent=2, default=str))
