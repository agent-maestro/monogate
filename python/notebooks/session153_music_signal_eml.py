"""Session 153 — Music & Signal Processing (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.music_signal_eml import analyze_music_signal_eml
print(json.dumps(analyze_music_signal_eml(), indent=2, default=str))
