import Lake
open Lake DSL

package «monogate-pnp» where

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "v4.14.0"

lean_lib «MonogatePNP» where
  roots := #[`MonogatePNP]
