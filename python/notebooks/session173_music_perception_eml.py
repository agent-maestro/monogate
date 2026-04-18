"""Session 173 — Music & Perception Deep: Timbre, Emotion, EML-∞ (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.music_perception_eml import analyze_music_perception_eml
print(json.dumps(analyze_music_perception_eml(), indent=2, default=str))
