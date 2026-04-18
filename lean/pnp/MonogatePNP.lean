-- MonogatePNP: Lean 4 formalization of P ≠ NP via Kolmogorov route
-- EML Research Program · T926/T932
--
-- Proof strategy (T232 anchor):
--   1. Boolean circuits formalized (Circuit.lean)
--   2. P = poly-size circuit families (CircuitFamily.lean)
--   3. MIN-CIRCUIT-SIZE ∈ NP (MinCircuitSize.lean)
--   4. K(x) uncomputable [Mathlib] (Kolmogorov.lean)
--   5. P=NP → MIN-CIRCUIT-SIZE ∈ P → K computable → ⊥  (PNP.lean)

import MonogatePNP.Circuit
import MonogatePNP.CircuitFamily
import MonogatePNP.MinCircuitSize
import MonogatePNP.Kolmogorov
import MonogatePNP.PNP
