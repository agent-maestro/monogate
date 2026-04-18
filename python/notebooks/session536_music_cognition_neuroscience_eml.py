import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.music_cognition_neuroscience_eml import analyze_music_cognition_neuroscience_eml
result = analyze_music_cognition_neuroscience_eml()
print(json.dumps(result, indent=2, default=str))
