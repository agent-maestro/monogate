"""Session 344 — Music Advanced"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.music_advanced_eml import analyze_music_advanced_eml
result = analyze_music_advanced_eml()
print(json.dumps(result, indent=2, default=str))
