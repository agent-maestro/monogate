"""Session 92 — Music Deep: Timbre, Psychoacoustics & Generative Composition (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.music_deep_eml import analyze_music_deep_eml
print(json.dumps(analyze_music_deep_eml(), indent=2, default=str))
