-- EML-R7 MachLib obligation stubs for sigmoid_derivative_v0
-- Candidate-only artifact generated from EML packet obligations.
-- This file contains no proofs and makes no theorem/proof claim.

namespace Monogate
namespace EML
namespace GeneratedObligations

-- Source expression: (1 / (1 + exp(-x))) * (1 - (1 / (1 + exp(-x))))

/-- Candidate obligation: Division node requires evidence that the denominator is not zero over declared inputs/ranges. -/
def sigmoidDerivativeV0DenominatorNonzero0 : String := "sigmoid_derivative_v0:domain:n5:div-denominator-nonzero"

/-- Candidate obligation: Input x declares range [-12.0, 12.0]; downstream runtime or proof work must preserve this boundary. -/
def sigmoidDerivativeV0InputRangeRespected1 : String := "sigmoid_derivative_v0:range:x:declared-safe-range"

end GeneratedObligations
end EML
end Monogate
