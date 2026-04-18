"""Session 193 — Δd Charge Angle 2: Traversal Characterization (TQC, Monads, Toposes) (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.traversal_characterization_eml import analyze_traversal_characterization_eml
print(json.dumps(analyze_traversal_characterization_eml(), indent=2, default=str))
