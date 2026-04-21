"""Tests for monogate.predict_cost — SuperBEST v5 cost predictor (dict-based API).

v5 changes (ADD-T1, 2026-04-20):
  - add=2n for ALL real x,y (was add_pos=3n)
  - add_gen=2n (was 11n; legacy alias, same as add in v5)
  - recip=1n (was 2n in v3 table; corrected to match EML primitive)
  - div=2n (was 1n in v3 table; corrected)
"""
from __future__ import annotations

import pytest

from monogate.predict_cost import UNIT, PATTERN_BONUS, naive_cost, predict_cost


# ---------------------------------------------------------------------------
# 1. Unit cost table sanity
# ---------------------------------------------------------------------------

class TestUnitTable:
    def test_exp_cost(self):
        assert UNIT['exp'] == 1

    def test_ln_cost(self):
        assert UNIT['ln'] == 1

    def test_mul_cost(self):
        assert UNIT['mul'] == 2

    def test_div_cost(self):
        assert UNIT['div'] == 2  # v5: div=2n

    def test_neg_cost(self):
        assert UNIT['neg'] == 2

    def test_pow_cost(self):
        assert UNIT['pow'] == 3

    def test_add_cost(self):
        assert UNIT['add'] == 2  # v5 (ADD-T1): add=2n for ALL reals

    def test_add_gen_cost(self):
        assert UNIT['add_gen'] == 2  # v5: add_gen is legacy alias for add (was 11n in v3/v4)

    def test_add_pos_cost(self):
        assert UNIT['add_pos'] == 2  # v5: add_pos is legacy alias for add (was 3n in v3/v4)

    def test_recip_cost(self):
        assert UNIT['recip'] == 1  # EML primitive: recip=1n

    def test_sub_cost(self):
        assert UNIT['sub'] == 2

    def test_all_values_positive(self):
        for op, cost in UNIT.items():
            assert cost > 0, f"op '{op}' has non-positive cost {cost}"


# ---------------------------------------------------------------------------
# 2. naive_cost() unit tests
# ---------------------------------------------------------------------------

class TestNaiveCost:
    def test_empty_ops(self):
        # No operations: cost is 0
        assert naive_cost({}) == 0

    def test_single_exp(self):
        assert naive_cost({'exp': 1}) == 1

    def test_single_ln(self):
        assert naive_cost({'ln': 1}) == 1

    def test_single_div(self):
        assert naive_cost({'div': 1}) == 2  # v5: div=2n

    def test_single_mul(self):
        assert naive_cost({'mul': 1}) == 2

    def test_single_neg(self):
        assert naive_cost({'neg': 1}) == 2

    def test_single_pow(self):
        assert naive_cost({'pow': 1}) == 3

    def test_single_add(self):
        assert naive_cost({'add': 1}) == 2  # v5 (ADD-T1): add=2n for ALL reals

    def test_single_add_gen(self):
        assert naive_cost({'add_gen': 1}) == 2  # v5: legacy alias, same as add=2n

    def test_multiple_ops_sum(self):
        # exp(1) + mul(2) + div(2) = 5 in v5
        assert naive_cost({'exp': 1, 'mul': 1, 'div': 1}) == 5

    def test_repeated_op(self):
        # 3 muls: 3*2 = 6
        assert naive_cost({'mul': 3}) == 6

    def test_unknown_op_defaults_to_two(self):
        # Unknown ops default to cost 2
        assert naive_cost({'unknown_op': 1}) == 2

    def test_arrhenius_naive(self):
        # k = A * exp(-Ea/(R*T))
        # v5: div(2) + mul(2)*2 + neg(2) + exp(1) = 2+4+2+1 = 9
        assert naive_cost({'div': 1, 'mul': 2, 'neg': 1, 'exp': 1}) == 9

    def test_wien_displacement(self):
        # b = lambda_max * T — bare product, just mul
        assert naive_cost({'mul': 1}) == 2


# ---------------------------------------------------------------------------
# 3. Pattern bonus table sanity
# ---------------------------------------------------------------------------

class TestPatternBonusTable:
    def test_eml_bonus(self):
        assert PATTERN_BONUS['EML'] == 3

    def test_deml_bonus(self):
        assert PATTERN_BONUS['DEML'] == 5

    def test_exl_bonus(self):
        assert PATTERN_BONUS['EXL'] == 3

    def test_edl_bonus(self):
        assert PATTERN_BONUS['EDL'] == 2

    def test_eal_bonus(self):
        assert PATTERN_BONUS['EAL'] == 4

    def test_lead_bonus(self):
        assert PATTERN_BONUS['LEAd'] == 4

    def test_elad_bonus(self):
        assert PATTERN_BONUS['ELAd'] == 4

    def test_lediv_bonus(self):
        assert PATTERN_BONUS['LEdiv'] == 2

    def test_leprod_bonus(self):
        assert PATTERN_BONUS['LEprod'] == 3

    def test_elsb_bonus(self):
        assert PATTERN_BONUS['ELSb'] == 1

    def test_emn_bonus(self):
        assert PATTERN_BONUS['EMN'] == 3

    def test_all_bonuses_positive(self):
        for name, bonus in PATTERN_BONUS.items():
            assert bonus > 0, f"Pattern '{name}' has non-positive bonus {bonus}"


# ---------------------------------------------------------------------------
# 4. predict_cost() — no patterns
# ---------------------------------------------------------------------------

class TestPredictCostNoPattern:
    def test_returns_int(self):
        result = predict_cost({'exp': 1, 'mul': 1})
        assert isinstance(result, int)

    def test_returns_non_negative(self):
        assert predict_cost({}) >= 0

    def test_empty_ops_zero_cost(self):
        assert predict_cost({}) == 0

    def test_single_exp(self):
        # exp(1) = 1 node
        assert predict_cost({'exp': 1}) == 1

    def test_simple_mul_div(self):
        # mul(2) + div(2) = 4 in v5
        assert predict_cost({'mul': 1, 'div': 1}) == 4

    def test_arrhenius_naive(self):
        # div(2) + mul(2)*2 + neg(2) + exp(1) = 2+4+2+1 = 9; no pattern bonus
        assert predict_cost({'div': 1, 'mul': 2, 'neg': 1, 'exp': 1}) == 9

    def test_boltzmann_entropy(self):
        # S = k_B * ln(Omega) => mul(2) + ln(1) = 3
        assert predict_cost({'mul': 1, 'ln': 1}) == 3

    def test_simple_power_law(self):
        # y = a * x^n => mul(2) + pow(3) = 5
        assert predict_cost({'mul': 1, 'pow': 1}) == 5

    def test_reciprocal(self):
        # recip(x) => cost 1 (EML primitive: recip=1n)
        assert predict_cost({'recip': 1}) == 1

    def test_sharing_reduces_cost(self):
        # shared=2 removes 2 nodes from cost
        base = predict_cost({'exp': 1, 'mul': 2})
        with_sharing = predict_cost({'exp': 1, 'mul': 2}, shared=2)
        assert with_sharing == base - 2

    def test_negative_result_clamped_to_zero(self):
        # shared discount exceeds cost — should clamp to 0, not go negative
        result = predict_cost({'exp': 1}, shared=100)
        assert result == 0


# ---------------------------------------------------------------------------
# 5. predict_cost() — with pattern bonuses
# ---------------------------------------------------------------------------

class TestPredictCostWithPatterns:
    def test_eml_pattern_reduces_cost(self):
        # EML: exp(x) - ln(y) => naive ops: exp(1)+sub(2)+ln(1)=4; bonus=3 => cost=1
        result = predict_cost({'exp': 1, 'sub': 1, 'ln': 1}, patterns=['EML'])
        assert result == 1  # 4 - 3 = 1

    def test_deml_pattern(self):
        # DEML: exp(-x)-ln(y) => naive: exp(1)+neg(2)+sub(2)+ln(1)=6; bonus=5 => cost=1
        result = predict_cost({'exp': 1, 'neg': 1, 'sub': 1, 'ln': 1}, patterns=['DEML'])
        assert result == 1  # 6 - 5 = 1

    def test_exl_pattern(self):
        # EXL: exp(x)*ln(y) => naive: exp(1)+mul(2)+ln(1)=4; bonus=3 => cost=1
        result = predict_cost({'exp': 1, 'mul': 1, 'ln': 1}, patterns=['EXL'])
        assert result == 1

    def test_edl_pattern(self):
        # EDL: exp(x)/ln(y) => naive: exp(1)+div(2)+ln(1)=4; bonus=2 => cost=2
        result = predict_cost({'exp': 1, 'div': 1, 'ln': 1}, patterns=['EDL'])
        assert result == 2

    def test_eal_pattern(self):
        # EAL: exp(x)+ln(y) => naive: exp(1)+add(2)+ln(1)=4; bonus=4 => cost=0
        result = predict_cost({'exp': 1, 'add': 1, 'ln': 1}, patterns=['EAL'])
        assert result == 0

    def test_emn_pattern(self):
        # EMN: exp(x)*exp(y) folded to exp(x+y)
        # naive: exp(2*1=2)+mul(2)+add(2) = 6; bonus=3 => cost=3
        result = predict_cost({'exp': 2, 'mul': 1, 'add': 1}, patterns=['EMN'])
        assert result == 3  # 6 - 3 = 3

    def test_multiple_patterns(self):
        # EML(bonus=3) + EXL(bonus=3) = total bonus 6
        result = predict_cost({'exp': 2, 'ln': 2, 'sub': 1, 'mul': 1},
                               patterns=['EML', 'EXL'])
        # naive = 1+1+1+2+1+2 = 8... actual: exp(2*1=2)+ln(2*1=2)+sub(1*2=2)+mul(1*2=2)=8
        # bonus = 6 => cost = 8 - 6 = 2
        assert result == 2

    def test_unknown_pattern_ignored(self):
        # Unknown pattern name contributes zero bonus
        ops = {'exp': 1, 'mul': 1}
        without = predict_cost(ops)
        with_unknown = predict_cost(ops, patterns=['UNKNOWN_PATTERN'])
        assert with_unknown == without

    def test_empty_patterns_same_as_none(self):
        ops = {'exp': 1, 'ln': 1, 'div': 1}
        assert predict_cost(ops, patterns=[]) == predict_cost(ops, patterns=None)

    def test_pattern_and_sharing_combined(self):
        # EML(bonus=3) + shared=1 => total discount = 4
        ops = {'exp': 1, 'sub': 1, 'ln': 1}  # naive = 4
        result = predict_cost(ops, patterns=['EML'], shared=1)
        assert result == 0  # 4 - 3 - 1 = 0

    def test_leprod_pattern(self):
        # LEprod: ln(exp(x)*y) => naive: ln(1)+exp(1)+mul(2)=4; bonus=3 => cost=1
        result = predict_cost({'ln': 1, 'exp': 1, 'mul': 1}, patterns=['LEprod'])
        assert result == 1

    def test_lead_pattern(self):
        # LEAd: ln(exp(x)+y) => naive: ln(1)+exp(1)+add(2)=4; bonus=4 => cost=0
        result = predict_cost({'ln': 1, 'exp': 1, 'add': 1}, patterns=['LEAd'])
        assert result == 0

    def test_lediv_pattern(self):
        # LEdiv: ln(exp(x)/y) => naive: ln(1)+exp(1)+div(2)=4; bonus=2 => cost=2
        result = predict_cost({'ln': 1, 'exp': 1, 'div': 1}, patterns=['LEdiv'])
        assert result == 2

    def test_elsb_pattern(self):
        # ELSb: exp(x)-y => bonus=1; naive with exp+sub = 1+2=3; cost=2
        result = predict_cost({'exp': 1, 'sub': 1}, patterns=['ELSb'])
        assert result == 2  # 3 - 1 = 2

    def test_result_always_non_negative(self):
        # Applying all patterns should never go below 0
        all_patterns = list(PATTERN_BONUS.keys())
        result = predict_cost({'exp': 1}, patterns=all_patterns)
        assert result >= 0
