"""
Derive SuperBEST v4 costs for information theory equations.
"""
import math

# SuperBEST v4 costs
EXP = 1; LN = 1; RECIP = 1; NEG = 2; MUL = 2; SUB = 2; DIV = 2
SQRT = 2; POW = 3; ADD_POS = 3; ADD_GEN = 11

print("=" * 60)
print("SuperBEST v4 Cost Derivation — Information Theory")
print("=" * 60)

# ----------------------------------------------------------------
# 1. Shannon Entropy H(X) = -Σ p_i * ln(p_i)
# Strategy A: neg(ln(p_i)) first (positive), then mul, then add_pos
#   neg(ln_pi): LN=1 + NEG=2 = 3n per term
#   mul(p_i, neg_ln_pi): MUL=2 => total 5n per term
#   Each term p_i * (-ln(p_i)) >= 0 (since p_i in (0,1), ln<0, neg makes it pos)
#   Sum of N positive terms: (N-1)*ADD_POS = 3(N-1)
#   Total: 5N + 3(N-1) = 8N - 3
def shannon_cost(N):
    per_term = LN + NEG + MUL
    additions = (N-1) * ADD_POS
    return N * per_term + additions

print("\n--- 1. Shannon Entropy H(X) = -sum p_i * ln(p_i) ---")
for N in [2, 4, 10, 256]:
    c = shannon_cost(N)
    print(f"  N={N}: {c}n  [8*{N}-3 = {8*N-3}]")
print("  Formula: 8N - 3")

# ----------------------------------------------------------------
# 2. KL Divergence D_KL(P||Q) = Σ p_i * ln(p_i/q_i)
# Per term: div(p_i, q_i)=DIV=2, ln(ratio)=LN=1, mul(p_i, ln_ratio)=MUL=2 => 5n/term
# Individual terms can be +/- (when p_i < q_i, ln(p/q)<0, term is negative)
# ADD_GEN between terms: 11n
# Total: 5N + 11(N-1) = 16N - 11
def kl_cost(N):
    per_term = DIV + LN + MUL
    additions = (N-1) * ADD_GEN
    return N * per_term + additions

print("\n--- 2. KL Divergence D_KL(P||Q) = sum p_i * ln(p_i/q_i) ---")
for N in [2, 4, 10, 256]:
    c = kl_cost(N)
    print(f"  N={N}: {c}n  [16*{N}-11 = {16*N-11}]")
print("  Formula: 16N - 11")

# ----------------------------------------------------------------
# 3. Cross-Entropy Loss H(P,Q) = -Σ p_i * ln(q_i)
# Per term: neg(ln(q_i)) = LN+NEG = 3n; mul(p_i, neg_ln) = MUL=2 => 5n/term
# Each term = p_i * (-ln(q_i)) >= 0: q_i in (0,1) => ln(q_i)<=0 => -ln>=0, p_i>=0
# Sum of positive terms: (N-1)*ADD_POS
# No outer neg needed
def xent_cost(N):
    per_term = LN + NEG + MUL
    additions = (N-1) * ADD_POS
    return N * per_term + additions

print("\n--- 3. Cross-Entropy Loss H(P,Q) = -sum p_i * ln(q_i) ---")
for N in [2, 4, 10, 256]:
    c = xent_cost(N)
    print(f"  N={N}: {c}n  [8*{N}-3 = {8*N-3}]")
print("  Formula: 8N - 3  (same cost as Shannon entropy; structurally identical)")

# ----------------------------------------------------------------
# 4. Mutual Information I(X;Y) = Σ_xy p(x,y)*ln(p(x,y)/(p(x)*p(y)))
# Per cell: mul(p_x,p_y)=2, div(p_xy,denom)=2, ln=1, mul(p_xy,ln_ratio)=2 => 7n/cell
# Individual terms can be +/- => ADD_GEN
def mi_cost(Xc, Yc):
    n_cells = Xc * Yc
    per_cell = MUL + DIV + LN + MUL
    additions = (n_cells - 1) * ADD_GEN
    return n_cells * per_cell + additions

print("\n--- 4. Mutual Information I(X;Y) = sum_xy p(x,y)*ln(p(x,y)/(p(x)*p(y))) ---")
for (Xc, Yc) in [(2,2), (3,3), (10,10)]:
    n = Xc * Yc
    c = mi_cost(Xc, Yc)
    print(f"  |X|={Xc},|Y|={Yc} ({n} cells): {c}n  [18*{n}-11 = {18*n-11}]")
print("  Formula: 18|X||Y| - 11")

# ----------------------------------------------------------------
# 5. Perplexity PP = exp(-1/N * Σ ln(p_i))
# ln(p_i): N terms of 1n => N
# All ln(p_i) <= 0; sum of negatives: (N-1)*ADD_GEN
# neg(sum): NEG=2
# div(neg_sum, N): DIV=2
# exp(result): EXP=1
# Total: N + 11(N-1) + 2 + 2 + 1 = 12N + 11N - 11 + 5 = wait:
# N*1 + (N-1)*11 + 2 + 2 + 1 = N + 11N - 11 + 5 = 12N - 6
def perplexity_cost(N):
    ln_terms = N * LN
    additions = (N-1) * ADD_GEN
    neg_node = NEG
    div_node = DIV
    exp_node = EXP
    return ln_terms + additions + neg_node + div_node + exp_node

print("\n--- 5. Perplexity PP = exp(-1/N * sum ln(p_i)) ---")
for N in [10, 100, 1000]:
    c = perplexity_cost(N)
    print(f"  N={N}: {c}n  [12*{N}-6 = {12*N-6}]")
print("  Formula: 12N - 6")

# ----------------------------------------------------------------
# 6. Entropy Rate (Markov): H = -Σ_i μ_i * Σ_j P_ij * ln(P_ij)
# Inner H_i = Shannon entropy of row i = 8|S| - 3
# mul(μ_i, H_i): MUL=2 per state
# Outer sum: μ_i*H_i >= 0 (both non-negative) => ADD_POS
# Total: Σ_i (8|S|-3 + 2) + (|S|-1)*ADD_POS
#      = |S|*(8|S|-1) + (|S|-1)*3 = 8S^2 - S + 3S - 3 = 8S^2 + 2S - 3
def entropy_rate_cost(S):
    H_i_cost = 8*S - 3
    inner_with_mul = H_i_cost + MUL
    outer_sum = (S-1) * ADD_POS
    return S * inner_with_mul + outer_sum

print("\n--- 6. Entropy Rate H(Markov) = -sum_i mu_i * sum_j P_ij * ln(P_ij) ---")
for S in [2, 3, 10, 20]:
    c = entropy_rate_cost(S)
    check = 8*S*S + 2*S - 3
    print(f"  |S|={S}: {c}n  [8*{S}^2+2*{S}-3 = {check}]")
print("  Formula: 8|S|^2 + 2|S| - 3")

# ----------------------------------------------------------------
# 7. Conditional Entropy H(Y|X) = -Σ_x Σ_y p(x,y)*ln(p(y|x))
# p(y|x) = p(x,y)/p(x): div(p_xy, p_x)=DIV=2
# ln(p_y_given_x)=LN=1; neg(ln)=NEG=2; mul(p_xy, neg_ln)=MUL=2 => 7n/pair
# Each term p(x,y)*(-ln(p(y|x))) >= 0: p(y|x)<=1 => ln<=0 => -ln>=0, p(x,y)>=0
# ADD_POS for the full sum
def cond_entropy_cost(Xc, Yc):
    n_pairs = Xc * Yc
    per_pair = DIV + LN + NEG + MUL
    additions = (n_pairs - 1) * ADD_POS
    return n_pairs * per_pair + additions

print("\n--- 7. Conditional Entropy H(Y|X) = -sum_xy p(x,y)*ln(p(y|x)) ---")
for (Xc, Yc) in [(2,2), (3,3), (10,10)]:
    n = Xc * Yc
    c = cond_entropy_cost(Xc, Yc)
    check = 10*n - 3
    print(f"  |X|={Xc},|Y|={Yc} ({n} pairs): {c}n  [10*{n}-3 = {check}]")
print("  Formula: 10|X||Y| - 3")

# ----------------------------------------------------------------
# 8. Jensen-Shannon Divergence JSD(P||Q) = H(M) - (H(P)+H(Q))/2
# M_i = (p_i+q_i)/2: add_pos(p_i,q_i)=3n + mul(,0.5)=2n => 5n per i, N terms total
# H(M): 8N-3; H(P): 8N-3; H(Q): 8N-3
# H(P)+H(Q): both >=0 => ADD_POS=3n
# div(HP_HQ, 2): DIV=2n
# sub(H_M, avg_H): SUB=2n
# Total: 5N + (8N-3) + (8N-3) + (8N-3) + 3 + 2 + 2
def jsd_cost(N):
    mixture_nodes = N * (ADD_POS + MUL)
    H_M = 8*N - 3
    H_P = 8*N - 3
    H_Q = 8*N - 3
    combine = ADD_POS + DIV + SUB
    return mixture_nodes + H_M + H_P + H_Q + combine

print("\n--- 8. Jensen-Shannon Divergence JSD(P||Q) = H(M)-(H(P)+H(Q))/2 ---")
for N in [2, 4, 10, 256]:
    c = jsd_cost(N)
    check = 29*N - 2
    print(f"  N={N}: {c}n  [29*{N}-2 = {check}]")
print("  Formula: 29N - 2")

print("\nAll costs confirmed.")
