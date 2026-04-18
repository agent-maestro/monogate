"""Session 192 — Δd Charge Angle 1: Integral Transforms & Fourier Analysis (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.integral_transforms_eml import analyze_integral_transforms_eml
print(json.dumps(analyze_integral_transforms_eml(), indent=2, default=str))
