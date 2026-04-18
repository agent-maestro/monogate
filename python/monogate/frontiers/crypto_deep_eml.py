"""
Session 125 — Cryptography Deep: One-Way Functions, Pseudorandomness & EML-Based Primitives

One-way functions as EML asymmetry instances, PRF/PRP constructions, zero-knowledge proofs,
elliptic curve cryptography, lattice-based cryptography, and EML-native cryptographic primitives.

Key theorem: RSA one-way function f(x) = x^e mod n is EML-2 (modular exponentiation = EML-2
in the exponent). Its inverse requires factoring = EML-∞ (classical hardness). ECC discrete
log is EML-∞ (group law composition). Lattice short vector = EML-∞. The EML Cryptographic
Asymmetry Theorem: every secure one-way function exhibits EML depth asymmetry d(f) < d(f⁻¹).
"""

from __future__ import annotations
import math, json
from dataclasses import dataclass

EML_INF = float("inf")


@dataclass
class OneWayFunctions:
    """
    One-way functions as EML asymmetry instances.

    EML structure:
    - RSA forward: C = M^e mod n: EML-2 (modular pow = exp(e·ln M) mod n)
    - RSA inverse: M = C^d mod n where d = e⁻¹ mod φ(n): requires factoring n = EML-∞
    - DLP forward: y = g^x mod p: EML-2 (discrete exponentiation)
    - DLP inverse: x = log_g y mod p: EML-∞ (classical best: index calculus)
    - Hash preimage: y = H(x), find x given y: EML-∞
    - Commitment: Com(m,r) = H(m||r): EML-1 (collision-free = EML-1 binding)
    """

    def rsa_forward(self, M: int, e: int, n: int) -> dict:
        """C = M^e mod n: forward RSA (modular exponentiation)."""
        C = pow(M, e, n)
        log_complexity = math.log(max(e, 1))
        return {
            "M": M, "e": e, "n": n,
            "C": C,
            "log_e": round(log_complexity, 4),
            "eml_forward": 2,
            "eml_inverse": "∞",
            "reason": (
                "RSA forward M^e mod n: discrete exponentiation = EML-2. "
                "Inverse requires factoring n = EML-∞ (classical hardness assumption)."
            ),
        }

    def discrete_log_complexity(self, p: int) -> dict:
        """Index calculus DLP complexity: L_p[1/2, 1] = exp(√(ln p · ln ln p))."""
        ln_p = math.log(p)
        ln_ln_p = math.log(ln_p) if ln_p > 0 else 0
        L = math.exp(math.sqrt(ln_p * ln_ln_p))
        return {
            "p": p,
            "ln_p": round(ln_p, 4),
            "subexponential_complexity_L": round(L, 2),
            "eml_complexity_expression": 2,
            "eml_hardness": "∞",
            "reason": "L_p[1/2,1]=exp(√(ln p·ln ln p)): double log inside exp = EML-2. DLP hardness = EML-∞.",
        }

    def hash_preimage_eml(self) -> dict:
        """Hash preimage resistance = EML-∞."""
        return {
            "forward_H": "EML-1 (compression = Merkle-Damgård chain = EML-1)",
            "preimage_resistance": "EML-∞ (no EML-finite formula inverts random oracle)",
            "collision_resistance": "EML-∞ (birthday bound 2^{n/2} = EML-2 bound on EML-∞ search)",
            "second_preimage": "EML-∞",
            "commitment_binding": "EML-1 (computationally binding under EML-∞ preimage hardness)",
        }

    def eml_cryptographic_asymmetry_theorem(self) -> dict:
        """EML Asymmetry Theorem applied to one-way functions."""
        return {
            "theorem": "EML Cryptographic Asymmetry Theorem",
            "statement": (
                "A function f is one-way iff d(f) < d(f⁻¹) in the EML hierarchy. "
                "d(forward) = 2 (EML-2 computation); d(inverse) = ∞ (EML-∞ search). "
                "The depth gap d(f⁻¹) - d(f) ≥ ∞ - 2 is what makes cryptography possible."
            ),
            "instances": {
                "RSA": "d(M^e mod n) = 2; d(factor n) = ∞",
                "DLP": "d(g^x mod p) = 2; d(log_g y) = ∞",
                "hash": "d(H(x)) = 1; d(H⁻¹(y)) = ∞",
                "lattice": "d(Ax+e) = 0 (linear); d(recover x) = ∞ (LWE hardness)",
            },
            "connection_to_s111": "EML Asymmetry Theorem (S111): d(exp)=1 < d(ln)=2 is the mathematical analog. Cryptography = applied EML asymmetry.",
        }

    def to_dict(self) -> dict:
        return {
            "rsa": [self.rsa_forward(M, 65537, 3233) for M in [2, 7, 100, 200]],
            "dlp_complexity": [self.discrete_log_complexity(p) for p in [101, 1009, 10007]],
            "hash_eml": self.hash_preimage_eml(),
            "asymmetry_theorem": self.eml_cryptographic_asymmetry_theorem(),
        }


@dataclass
class EllipticCurveCryptography:
    """
    Elliptic curve cryptography and ECDLP.

    EML structure:
    - Point addition (chord-and-tangent): EML-2 (rational functions of coordinates)
    - Scalar multiplication [k]P: EML-2 (double-and-add, O(log k) steps each EML-2)
    - ECDLP: given Q=[k]P, find k: EML-∞ (best: Pohlig-Hellman + Pollard rho)
    - Bilinear pairing e(P,Q): EML-3 (Weil pairing = complex trig on curve = EML-3)
    - Edwards curve: x²+y²=1+dx²y²: EML-2 (affine coordinates = EML-2 arithmetic)
    - Curve order #E(F_p) = p+1-t, |t|≤2√p: EML-2 (Hasse bound = EML-2 control)
    """

    def point_double(self, x: float, y: float, a: float = -1.0) -> dict:
        """Doubling formula for Weierstrass y²=x³+ax+b: λ=(3x²+a)/(2y)."""
        if y == 0:
            return {"error": "point at infinity"}
        lam = (3 * x**2 + a) / (2 * y)
        x3 = lam**2 - 2 * x
        y3 = lam * (x - x3) - y
        return {
            "P": (x, y),
            "lambda": round(lam, 4),
            "2P": (round(x3, 4), round(y3, 4)),
            "eml": 2,
            "reason": "λ=(3x²+a)/(2y): rational of quadratic = EML-2 (chord-and-tangent formula).",
        }

    def hasse_bound(self, p: int) -> dict:
        """Hasse: |#E - (p+1)| ≤ 2√p."""
        bound = 2 * math.sqrt(p)
        return {
            "p": p,
            "hasse_bound": round(bound, 2),
            "n_min": round(p + 1 - bound),
            "n_max": round(p + 1 + bound),
            "eml": 2,
            "reason": "#E ∈ [p+1-2√p, p+1+2√p]: √p = EML-2 (square root of prime = EML-2).",
        }

    def ecdlp_complexity(self, log2_p: int) -> dict:
        """Pollard rho ECDLP: O(√p) = exp(n/2) where n = bit-length."""
        n_bits = log2_p
        ops = 2 ** (n_bits / 2)
        return {
            "n_bits": n_bits,
            "operations_sqrt_p": ops,
            "log2_operations": n_bits / 2,
            "eml_expression": 2,
            "eml_hardness": "∞",
            "reason": "Complexity √p=exp(n/2): EML-2 (half-exponent). ECDLP hardness = EML-∞.",
        }

    def pairing_eml(self) -> dict:
        """Weil/Tate pairing e: G₁×G₂→Gₜ: EML-3."""
        return {
            "pairing_type": "Weil/Tate",
            "eml": 3,
            "reason": (
                "Bilinear pairing e(P,Q) involves Miller's algorithm: evaluates a rational "
                "function f_P along a divisor, using trig-like oscillatory evaluation on the curve. "
                "The final exponentiation (Frobenius) gives EML-3 structure."
            ),
            "applications": {
                "BLS_signature": "EML-3 signature scheme",
                "IBE": "Identity-based encryption via pairings = EML-3",
                "zk_SNARK_pairing": "Pairing check in Groth16 = EML-3",
            },
        }

    def to_dict(self) -> dict:
        return {
            "point_doubling": [self.point_double(x, y) for x, y in [(1.0, 2.0), (2.0, 3.0)]],
            "hasse_bound": [self.hasse_bound(p) for p in [101, 1009, 10007]],
            "ecdlp_complexity": [self.ecdlp_complexity(n) for n in [128, 256, 384, 521]],
            "pairing": self.pairing_eml(),
            "eml_point_arithmetic": 2,
            "eml_ecdlp": "∞",
            "eml_pairing": 3,
        }


@dataclass
class ZeroKnowledgeAndLattice:
    """
    Zero-knowledge proofs and lattice cryptography EML classification.

    EML structure:
    - Schnorr ZK: commit R=g^r (EML-2), challenge e (EML-0), response s=r+e·x (EML-0)
    - ZK soundness: exp(-k·log p) probability of cheating: EML-2 (exponential in security param)
    - LWE problem: given (A,b=Ax+e mod q): find x: EML-∞ (worst-case lattice hardness)
    - LWE encryption: c = (As + e₁, bᵀs + e₂ + ⌊q/2⌋·m): EML-0 (linear arithmetic)
    - Regev reduction: EML-∞ (quantum-hard)
    - NTRU: polynomial multiplication in Z[x]/(x^n-1): EML-2 (convolution = EML-2)
    - Ring-LWE: same hardness as LWE but structured: EML-∞
    """

    def schnorr_protocol(self, x: float, r: float, e: float) -> dict:
        """Schnorr: commit R=g^r, challenge e, response s=r+e·x."""
        s = r + e * x
        return {
            "secret_x": x,
            "random_r": r,
            "challenge_e": e,
            "response_s": round(s, 4),
            "commit_eml": 2,
            "challenge_eml": 0,
            "response_eml": 0,
            "soundness_eml": 2,
            "reason": "Commit g^r=EML-2; challenge=EML-0; response=EML-0; soundness exp(-k)=EML-2.",
        }

    def lwe_encryption_eml(self) -> dict:
        """LWE public key encryption EML depth."""
        return {
            "keygen": {
                "A_matrix": "EML-0 (uniform random — EML-∞ as source of randomness)",
                "s_secret": "EML-0 (small random vector)",
                "e_error": "EML-∞ (Gaussian noise drawn from D_{Z,σ})",
                "b_As_e": "EML-0 (linear = EML-0 arithmetic mod q)",
            },
            "encryption": {
                "c1_As1_e1": "EML-0",
                "c2_bTs_e2_msg": "EML-0 (linear with message encoding)",
            },
            "hardness": "EML-∞ (finding s given (A,b=As+e) = hard lattice problem)",
            "quantum_hardness": "EML-∞ (Regev reduction: quantum = classical worst-case SVP = EML-∞)",
        }

    def ntru_convolution(self, f: list[float], g: list[float]) -> dict:
        """NTRU: f*g in Z[x]/(x^n-1): cyclic convolution."""
        n = len(f)
        h = [0.0] * n
        for i in range(n):
            for j in range(n):
                h[(i + j) % n] += f[i] * g[j]
        return {
            "f": f,
            "g": g,
            "f_star_g_mod_xn_minus_1": [round(v, 2) for v in h],
            "eml": 2,
            "reason": "Cyclic convolution = polynomial multiplication = EML-2 (quadratic in coefficients).",
        }

    def to_dict(self) -> dict:
        return {
            "schnorr": [self.schnorr_protocol(x, r, e)
                        for x, r, e in [(3.0, 7.0, 2.0), (5.0, 11.0, 3.0)]],
            "lwe": self.lwe_encryption_eml(),
            "ntru": self.ntru_convolution([1, 1, 0], [1, -1, 0]),
            "eml_schnorr_commit": 2,
            "eml_lwe_arithmetic": 0,
            "eml_lwe_hardness": "∞",
            "eml_ntru_multiplication": 2,
            "eml_ring_lwe_hardness": "∞",
        }


def analyze_crypto_deep_eml() -> dict:
    owf = OneWayFunctions()
    ecc = EllipticCurveCryptography()
    zkl = ZeroKnowledgeAndLattice()
    return {
        "session": 125,
        "title": "Cryptography Deep: One-Way Functions, Pseudorandomness & EML-Based Primitives",
        "key_theorem": {
            "theorem": "EML Cryptographic Asymmetry Theorem",
            "statement": (
                "Every computationally secure one-way function f exhibits EML depth asymmetry: "
                "d(f) < d(f⁻¹). "
                "RSA: d(M^e mod n) = 2 < d(factor n) = ∞. "
                "DLP: d(g^x mod p) = 2 < d(log_g y) = ∞. "
                "Hash: d(H) = 1 < d(H⁻¹) = ∞. "
                "LWE: d(Ax+e) = 0 < d(recover x) = ∞. "
                "ECDLP: d([k]P) = 2 < d(find k) = ∞. "
                "Bilinear pairing e(P,Q) is EML-3. "
                "Schnorr commitment g^r is EML-2; soundness probability exp(-k) is EML-2. "
                "Cryptography is the engineering discipline of EML depth asymmetry."
            ),
        },
        "one_way_functions": owf.to_dict(),
        "elliptic_curve_crypto": ecc.to_dict(),
        "zero_knowledge_lattice": zkl.to_dict(),
        "eml_depth_summary": {
            "EML-0": "LWE arithmetic Ax+e mod q (linear); Schnorr challenge; hash input alphabet",
            "EML-1": "Hash Merkle-Damgård chain (compression = EML-1); commitment binding",
            "EML-2": "RSA/DLP forward M^e (EML-2 exp); Schnorr commit g^r; ECDLP complexity √p; NTRU convolution; Hasse bound √p",
            "EML-3": "Bilinear pairing e(P,Q) (Weil/Tate via Miller = EML-3)",
            "EML-∞": "Factoring n; DLP inverse; hash preimage; ECDLP; LWE hardness; Shor's algorithm barrier (quantum changes EML-2→EML-∞)",
        },
        "rabbit_hole_log": [
            "The EML Cryptographic Asymmetry Theorem is the engineering instantiation of the Mathematical Asymmetry Theorem (S111): d(exp)=1 < d(ln)=2. Cryptography exploits the same structural asymmetry — it is easy to exponentiate (EML-2) but hard to take discrete logarithms (EML-∞). The gap between EML-2 (forward) and EML-∞ (inverse) IS the security of public-key cryptography. Every cryptographic hardness assumption is a claim that a particular EML depth gap is real.",
            "Lattice cryptography (LWE) exhibits the LARGEST EML depth gap: encryption is EML-0 (linear arithmetic Ax+e mod q — the simplest possible EML depth!) but decryption without the key is EML-∞ (SVP/CVP hardness). The gap is EML-∞ - 0 = ∞ — larger than RSA (EML-∞ - 2). This is why LWE is conjectured quantum-safe: even Shor's algorithm can't reduce LWE below EML-∞.",
            "Bilinear pairings are EML-3: the Weil pairing e: G₁×G₂→Gₜ uses Miller's algorithm which evaluates rational functions along curve divisors — the oscillatory structure of divisor theory on Riemann surfaces (S115) is EML-3. This makes pairing-based cryptography (IBE, BLS signatures, zk-SNARKs via Groth16) inherently EML-3. The pairing check in Groth16 is: e(A,B)=e(α,β)·e(L,γ)·e(C,δ) — three EML-3 operations confirming the proof.",
        ],
        "connections": {
            "to_session_105": "S105 covered RSA/GNFS/LWE at overview. S125 adds ECDLP, pairings (EML-3), Schnorr, EML Asymmetry Theorem application.",
            "to_session_111": "EML Asymmetry Theorem (S111) d(exp)=1 < d(ln)=2 = mathematical basis for all cryptographic hardness.",
            "to_session_115": "Bilinear pairings = elliptic curve EML-3 (divisor theory on curves = EML-3, as in S115 mirror symmetry).",
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze_crypto_deep_eml(), indent=2, default=str))
