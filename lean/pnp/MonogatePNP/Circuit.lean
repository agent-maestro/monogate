import Mathlib.Data.Bool.Basic
import Mathlib.Data.Fin.Basic
import Mathlib.Data.Array.Basic

/-!
# Boolean Circuit Library

Defines boolean circuits, their evaluation, and size measure.
This is the core data structure for the P≠NP formalization.

A `Circuit` is a DAG of gates in topological order.
Gates reference previous gates by index (smaller index = earlier in order).
-/

namespace EML.Circuit

/-- Gate kinds. Wire indices reference earlier gates in topological order.
    Input gates reference the circuit's input vector by position. -/
inductive GateKind : Type where
  | input  : ℕ → GateKind       -- i-th input bit (0-indexed)
  | constB : Bool → GateKind    -- constant true/false
  | not    : ℕ → GateKind       -- NOT gate[i]
  | and2   : ℕ → ℕ → GateKind   -- AND gate[i] gate[j]
  | or2    : ℕ → ℕ → GateKind   -- OR  gate[i] gate[j]
  deriving Repr

/-- A boolean circuit on `numInputs` input bits.
    `gates` is in topological order; `outputIdx` indexes into `gates`. -/
structure Circuit where
  numInputs : ℕ
  gates     : Array GateKind
  outputIdx : ℕ
  hOutput   : outputIdx < gates.size := by decide

/-- The size of a circuit = number of non-input gates (standard measure). -/
def Circuit.size (c : Circuit) : ℕ := c.gates.size

/-- Evaluate gate `i` given already-evaluated gate values `vals` and input `inp`. -/
private def evalGate (inp : Array Bool) (vals : Array Bool) : GateKind → Bool
  | .input i    => if h : i < inp.size  then inp[i]  else false
  | .constB b   => b
  | .not i      => if h : i < vals.size then !vals[i] else false
  | .and2 i j   =>
      let a := if h : i < vals.size then vals[i] else false
      let b := if h : j < vals.size then vals[j] else false
      a && b
  | .or2 i j    =>
      let a := if h : i < vals.size then vals[i] else false
      let b := if h : j < vals.size then vals[j] else false
      a || b

/-- Evaluate a circuit on a boolean input vector.
    Gates are evaluated left-to-right (topological order). -/
def Circuit.eval (c : Circuit) (inp : Array Bool) : Bool :=
  let vals := c.gates.foldl (fun acc gk => acc.push (evalGate inp acc gk)) #[]
  if h : c.outputIdx < vals.size then vals[c.outputIdx] else false

/-- A circuit with `n` inputs computes the boolean function `f` if it agrees
    on all inputs. -/
def Circuit.computes (c : Circuit) (f : Array Bool → Bool) : Prop :=
  ∀ inp : Array Bool, inp.size = c.numInputs → c.eval inp = f inp

-- ────────────────────────────────────────────────────────────────────────────
-- Basic circuits (building blocks)
-- ────────────────────────────────────────────────────────────────────────────

/-- Identity circuit: one input, output = input[0]. -/
def idCircuit : Circuit where
  numInputs := 1
  gates     := #[.input 0]
  outputIdx := 0

/-- NOT circuit. -/
def notCircuit : Circuit where
  numInputs := 1
  gates     := #[.input 0, .not 0]
  outputIdx := 1

/-- AND circuit. -/
def andCircuit : Circuit where
  numInputs := 2
  gates     := #[.input 0, .input 1, .and2 0 1]
  outputIdx := 2

/-- OR circuit. -/
def orCircuit : Circuit where
  numInputs := 2
  gates     := #[.input 0, .input 1, .or2 0 1]
  outputIdx := 2

-- ────────────────────────────────────────────────────────────────────────────
-- Size lemmas
-- ────────────────────────────────────────────────────────────────────────────

@[simp] theorem idCircuit_size  : idCircuit.size  = 1 := rfl
@[simp] theorem notCircuit_size : notCircuit.size = 2 := rfl
@[simp] theorem andCircuit_size : andCircuit.size = 3 := rfl
@[simp] theorem orCircuit_size  : orCircuit.size  = 3 := rfl

-- ────────────────────────────────────────────────────────────────────────────
-- Correctness lemmas
-- ────────────────────────────────────────────────────────────────────────────

theorem notCircuit_correct (b : Bool) :
    notCircuit.eval #[b] = !b := by simp [Circuit.eval, evalGate, notCircuit]

theorem andCircuit_correct (a b : Bool) :
    andCircuit.eval #[a, b] = (a && b) := by
  simp [Circuit.eval, evalGate, andCircuit]

theorem orCircuit_correct (a b : Bool) :
    orCircuit.eval #[a, b] = (a || b) := by
  simp [Circuit.eval, evalGate, orCircuit]

end EML.Circuit
