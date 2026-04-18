"""
Session 105 — Cryptography & Information Security: EML Hardness Hierarchy

One-way functions, public-key cryptography, hash functions, and complexity-
theoretic hardness classified by EML depth.

Key theorem: RSA and Diffie-Hellman security rest on EML-2 hardness (discrete
logarithm, integer factorization are EML-2 to compute but EML-∞ to invert without
the key). Hash functions are EML-∞ (preimage resistance). Perfect secrecy (OTP) is
EML-0 (information-theoretic). Elliptic curve DLP is EML-2. Post-quantum lattice
problems are EML-∞.
"""

from __future__ import annotations
import math, json, hashlib
from dataclasses import dataclass, field


EML_INF = float("inf")


@dataclass
class ClassicalCryptography:
    """
    Classical ciphers and information-theoretic security.

    EML structure:
    - One-time pad: C = M ⊕ K → perfect secrecy. I(M;C) = 0: EML-0
    - Caesar cipher: C = (M + k) mod 26: EML-0 (modular addition = affine)
    - Vigenère: EML-0 (polyalphabetic = linear over Z_26)
    - Shannon entropy of plaintext: H(M) = EML-2 (−Σ p·log p)
    - Key entropy for OTP: H(K) ≥ H(M): EML-2 minimum
    - Shannon's perfect secrecy theorem: H(K) = H(M) iff OTP → EML-0 cipher achieves this
    """

    def otp_security(self, message_bits: int) -> dict:
        H_M = message_bits
        H_K_required = message_bits
        return {
            "message_bits": message_bits,
            "H_M_bits": H_M,
            "H_K_required": H_K_required,
            "mutual_information": 0,
            "eml_cipher": 0,
            "eml_key_entropy": 2,
            "reason": "OTP: I(M;C)=0 = perfect secrecy = EML-0 cipher; H(K)≥H(M) = EML-2 bound",
        }

    def caesar_analysis(self, message: str, shift: int = 3) -> dict:
        encrypted = "".join(chr((ord(c) - ord('A') + shift) % 26 + ord('A'))
                            if c.isalpha() else c for c in message.upper())
        return {
            "plaintext": message,
            "ciphertext": encrypted,
            "shift": shift,
            "eml": 0,
            "reason": "C = (M + k) mod 26: affine map over Z_26 = EML-0 (modular arithmetic)",
            "security": "Breakable by frequency analysis — EML-0 offers no computational security",
        }

    def to_dict(self) -> dict:
        return {
            "otp": self.otp_security(128),
            "caesar": self.caesar_analysis("HELLO", 3),
            "shannon_perfect_secrecy": {
                "condition": "H(K) ≥ H(M)",
                "eml_H_K": 2,
                "eml_OTP": 0,
                "insight": "Perfect secrecy is EML-0 operationally but requires EML-2 key entropy",
            },
        }


@dataclass
class PublicKeyCryptography:
    """
    RSA, Diffie-Hellman, and Elliptic Curve Cryptography.

    EML structure:
    - RSA: e·d ≡ 1 (mod φ(n)), n=p·q
      - Encryption: C = M^e mod n: EML-2 (modular exponentiation = exp(e·ln M) mod n)
      - Factoring n: EML-∞ (no polynomial algorithm known)
      - φ(n) = (p-1)(q-1): EML-0 (arithmetic if p,q known)
    - Diffie-Hellman: g^x mod p
      - DH key: K = g^{ab} mod p: EML-2 (modular exponentiation)
      - Discrete log problem: x = log_g(y) mod p: EML-∞ (intractable)
    - Elliptic Curve: y² = x³ + ax + b over F_p
      - Point addition: EML-2 (rational function of coordinates)
      - ECDLP: Q = kP, find k: EML-∞ (harder than DLP per bit)
    - Key insight: Cryptographic hardness = EML-∞ direction of EML-2 operations
    """

    def rsa_encrypt_small(self, M: int, e: int, n: int) -> dict:
        C = pow(M, e, n)
        eml_enc = 2
        return {
            "M": M, "e": e, "n": n,
            "C": C,
            "eml_encryption": eml_enc,
            "eml_decryption_without_key": EML_INF,
            "reason_enc": "C = M^e mod n: modular exp = EML-2 (exp of log)",
            "reason_hard": "Factoring n to recover d: EML-∞ (best known = GNFS ~ exp((ln n)^{1/3}))",
        }

    def dh_exchange(self, g: int, p: int, a: int, b: int) -> dict:
        """Small DH example."""
        A = pow(g, a, p)  # Alice's public key
        B = pow(g, b, p)  # Bob's public key
        K_A = pow(B, a, p)  # Alice computes shared key
        K_B = pow(A, b, p)  # Bob computes shared key
        return {
            "g": g, "p": p,
            "alice_private": a, "alice_public": A,
            "bob_private": b, "bob_public": B,
            "shared_key": K_A,
            "keys_match": K_A == K_B,
            "eml_key_exchange": 2,
            "eml_dlp_attack": EML_INF,
            "reason": "g^x mod p: EML-2 to compute, EML-∞ to invert (DLP)",
        }

    def gnfs_complexity(self, n_bits: int) -> dict:
        """
        General Number Field Sieve complexity for n-bit number:
        L_n[1/3, (64/9)^{1/3}] = exp((c+o(1))·(ln n)^{1/3}·(ln ln n)^{2/3})
        """
        ln_n = n_bits * math.log(2)
        c = (64 / 9) ** (1 / 3)
        exponent = c * ln_n ** (1/3) * math.log(ln_n) ** (2/3)
        log10_ops = exponent * math.log10(math.e)
        return {
            "n_bits": n_bits,
            "gnfs_exponent": round(exponent, 2),
            "log10_operations": round(log10_ops, 1),
            "eml_complexity": 2,
            "reason": "GNFS: exp((ln n)^{1/3}·(ln ln n)^{2/3}) = sub-exponential = EML-2 (two nested logs)",
        }

    def to_dict(self) -> dict:
        return {
            "rsa_example": self.rsa_encrypt_small(42, 65537, 3233),
            "dh_example": self.dh_exchange(2, 23, 6, 15),
            "gnfs": [self.gnfs_complexity(b) for b in [512, 1024, 2048, 4096]],
            "eml_rsa_enc": 2,
            "eml_rsa_security": EML_INF,
            "eml_dlp": EML_INF,
            "eml_ecdlp": EML_INF,
            "hardness_summary": "Cryptographic one-way functions: EML-2 to evaluate, EML-∞ to invert",
        }


@dataclass
class HashFunctionsEML:
    """
    Cryptographic hash functions: SHA-256, collision resistance, preimage resistance.

    EML structure:
    - Hash output h = H(m) ∈ {0,1}^256: looks like EML-∞ (no structure)
    - Preimage resistance: find m' s.t. H(m') = h: EML-∞ (brute force = 2^256 queries)
    - Collision resistance: find m≠m' s.t. H(m)=H(m'): EML-∞ (birthday bound 2^128)
    - Birthday paradox: collisions at ~√(2^256) = 2^128 queries: EML-2 (square root = exp(½·256·ln2))
    - Merkle-Damgård construction: H = f^n(m_1,...,m_n, IV): EML-1 iterated composition
    - Length extension attack on MD: H(m||m') = f(H(m), m'): EML-1 (chain = EML-1 sequence)
    - Random oracle model: ideal hash = EML-∞ (perfectly random function)
    """

    def birthday_bound(self, output_bits: int) -> dict:
        """Collision search by birthday paradox: ~2^{n/2} queries."""
        log2_queries = output_bits / 2
        log10_queries = log2_queries * math.log10(2)
        return {
            "output_bits": output_bits,
            "log2_collision_queries": log2_queries,
            "log10_collision_queries": round(log10_queries, 1),
            "eml_birthday": 2,
            "reason": "Birthday bound 2^{n/2} = exp(n·ln2/2): EML-2 (exp of linear in n)",
        }

    def merkle_damgard_chain(self, n_blocks: int) -> dict:
        """MD: H_i = f(H_{i-1}, m_i), i=1..n."""
        return {
            "n_blocks": n_blocks,
            "chain_depth": n_blocks,
            "eml_per_step": 1,
            "eml_full_chain": 1,
            "reason": "f(H_{i-1}, m_i) iterated: EML-1 sequence (geometric chain of EML-1 steps)",
            "length_extension_vulnerability": True,
        }

    def sha256_avalanche(self) -> dict:
        """Demonstrate avalanche effect: 1-bit change flips ~50% of output bits."""
        m1 = b"hello"
        m2 = b"hellp"
        h1 = hashlib.sha256(m1).hexdigest()
        h2 = hashlib.sha256(m2).hexdigest()
        bits1 = bin(int(h1, 16))[2:].zfill(256)
        bits2 = bin(int(h2, 16))[2:].zfill(256)
        diff = sum(b1 != b2 for b1, b2 in zip(bits1, bits2))
        return {
            "msg1": m1.decode(), "msg2": m2.decode(),
            "hash1": h1[:16] + "...",
            "hash2": h2[:16] + "...",
            "bits_differing": diff,
            "fraction": round(diff / 256, 3),
            "eml": EML_INF,
            "reason": "Avalanche: 1-bit change → ~50% output change = EML-∞ (no structure in output)",
        }

    def to_dict(self) -> dict:
        return {
            "birthday_bounds": [self.birthday_bound(b) for b in [128, 160, 256, 512]],
            "merkle_damgard": self.merkle_damgard_chain(16),
            "sha256_avalanche": self.sha256_avalanche(),
            "eml_hash_output": EML_INF,
            "eml_preimage": EML_INF,
            "eml_collision": EML_INF,
            "eml_birthday_bound": 2,
            "eml_md_chain": 1,
        }


@dataclass
class PostQuantumCryptography:
    """
    Lattice-based, code-based, and hash-based post-quantum schemes.

    EML structure:
    - LWE (Learning with Errors): b = As + e mod q, find s
      - A: EML-0 (public matrix = integers)
      - Noise e ~ Gaussian: EML-1 per component (Gaussian = exp(-x²/2σ²))
      - Hardness: EML-∞ (worst-case lattice problem via gap-SVP)
    - NTRU: polynomial ring Zq[x]/(x^n-1): EML-2 (polynomial operations)
    - Grover's algorithm (quantum): searches in O(2^{n/2}): EML-2 (quadratic speedup)
    - Shor's algorithm (quantum): solves DLP and factoring in poly time: reduces RSA to EML-2 (quantum)
    """

    def lwe_parameters(self, n: int, q: int, sigma: float) -> dict:
        """LWE parameter analysis."""
        noise_entropy = 0.5 * math.log(2 * math.pi * math.e * sigma ** 2) / math.log(2)
        advantage = math.exp(-math.pi * sigma ** 2 / q ** 2)
        return {
            "n": n, "q": q, "sigma": sigma,
            "noise_entropy_bits": round(noise_entropy, 2),
            "distinguishing_advantage": round(advantage, 6),
            "eml_lwe_noise": 1,
            "eml_lwe_hardness": EML_INF,
            "reason_noise": "e ~ Gaussian: EML-1 per component",
            "reason_hard": "LWE hardness ≡ gap-SVP: worst-case lattice problem = EML-∞",
        }

    def grover_speedup(self, n_bits: int) -> dict:
        """Grover's algorithm: O(√N) = O(2^{n/2}) queries."""
        classical_log2 = n_bits
        quantum_log2 = n_bits / 2
        return {
            "n_bits": n_bits,
            "classical_queries_log2": classical_log2,
            "quantum_queries_log2": quantum_log2,
            "speedup_factor": f"2^{{{n_bits // 2}}}",
            "eml_grover": 2,
            "reason": "Grover: O(√N) = O(2^{n/2}): quadratic speedup = EML-2 (halves exponent)",
        }

    def shor_factoring(self, n_bits: int) -> dict:
        """Shor's algorithm: poly(n) quantum gates."""
        classical_log10_ops = (64/9)**(1/3) * (n_bits * math.log(2))**(1/3) * math.log(n_bits)**2 * math.log10(math.e)
        quantum_poly = n_bits ** 3
        return {
            "n_bits": n_bits,
            "classical_log10_ops": round(classical_log10_ops, 1),
            "quantum_gate_count": quantum_poly,
            "eml_shor": 2,
            "reason": "Shor: O(n³) quantum gates = EML-2 (polynomial in n = exp(3·ln n))",
            "implication": "Shor reduces RSA (EML-∞ classical) to EML-2 (quantum polynomial)",
        }

    def to_dict(self) -> dict:
        return {
            "lwe": [self.lwe_parameters(256, 3329, 3.2), self.lwe_parameters(512, 3329, 3.2)],
            "grover": [self.grover_speedup(128), self.grover_speedup(256)],
            "shor": [self.shor_factoring(2048), self.shor_factoring(4096)],
            "pq_eml_summary": {
                "LWE_hardness": EML_INF,
                "NTRU_polynomial_ops": 2,
                "Grover_speedup": 2,
                "Shor_complexity": 2,
            },
            "insight": "Quantum computing moves RSA from EML-∞ to EML-2 — post-quantum crypto needs new EML-∞ problems",
        }


def analyze_crypto_eml() -> dict:
    classical = ClassicalCryptography()
    pubkey = PublicKeyCryptography()
    hashes = HashFunctionsEML()
    pq = PostQuantumCryptography()
    return {
        "session": 105,
        "title": "Cryptography & Information Security: EML Hardness Hierarchy",
        "key_theorem": {
            "theorem": "EML Cryptographic Hardness Theorem",
            "statement": (
                "Perfect secrecy (OTP) is EML-0 operationally (I(M;C)=0). "
                "RSA encryption C=M^e mod n is EML-2 (modular exponentiation). "
                "Factoring and discrete log are EML-∞ (no polynomial algorithm classically). "
                "GNFS is sub-exponential: exp((ln n)^{1/3}·(ln ln n)^{2/3}) = EML-2 (two nested logs). "
                "Hash outputs are EML-∞ (no structure, preimage/collision resistance). "
                "Birthday bound is EML-2 (2^{n/2} = square root). "
                "LWE hardness is EML-∞ (worst-case lattice). "
                "Shor's algorithm reduces factoring to EML-2 (quantum polynomial)."
            ),
        },
        "classical_crypto": classical.to_dict(),
        "public_key": pubkey.to_dict(),
        "hash_functions": hashes.to_dict(),
        "post_quantum": pq.to_dict(),
        "eml_depth_summary": {
            "EML-0": "OTP cipher (perfect secrecy); Caesar/Vigenère; RSA modulus arithmetic given factors",
            "EML-1": "Merkle-Damgård chain (iterated composition); Gaussian LWE noise per component",
            "EML-2": "RSA/DH computation (modular exp); GNFS complexity; birthday bound; Shor/Grover; power-law key sizes",
            "EML-∞": "Factoring n; discrete log; ECDLP; hash preimage/collision; LWE hardness (gap-SVP)",
        },
        "rabbit_hole_log": [
            "Cryptographic hardness = EML asymmetry: the same modular exponentiation that is EML-2 to compute forward is EML-∞ to invert backward. Cryptography exists precisely because EML depth is not preserved under inversion.",
            "GNFS is exactly EML-2: the best classical factoring algorithm runs in exp((ln n)^{1/3}·(ln ln n)^{2/3}). This is two nested logarithms under an exponential = EML-2. RSA's security is that EML-2 classical effort is still enormous for 2048-bit keys.",
            "Shor's algorithm is an EML-depth reduction: quantum computing changes RSA from EML-∞ (classical) to EML-2 (polynomial quantum). Post-quantum cryptography seeks functions that remain EML-∞ even for quantum computers. LWE achieves this via worst-case lattice hardness.",
            "The hash function avalanche effect is EML-∞ by design: cryptographers engineer hash functions to have no EML-finite description of their input-output behavior. The EML-∞ property is the goal of hash design, not an accident.",
        ],
        "connections": {
            "to_session_71": "PRNGs are EML-2 (deterministic recurrence). Hash outputs target EML-∞ (true randomness). Crypto bridges them.",
            "to_session_69": "Algorithmic randomness: hash outputs are computationally EML-∞ (pseudo-random oracle). Kolmogorov complexity analog.",
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze_crypto_eml(), indent=2, default=str))
