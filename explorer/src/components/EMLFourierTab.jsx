import React, { useState } from "react";

const TARGETS = ["sin", "cos", "exp", "log", "sinh", "cosh"];
const METHODS = ["omp", "lasso"];

const PRECOMPUTED_RESULTS = {
  sin: {
    K: 5,
    mse_train: 8.945e-4,
    mse_test: 2.326e-2,
    n_dict_atoms: 79,
    formula: "0.072·eml(1,eml(eml(x,x),x)) + 0.326·eml(x,eml(eml(x,x),x)) + ...",
    atoms: [
      { formula: "eml(1,eml(eml(x,x),x))", coeff: 0.071837 },
      { formula: "eml(x,eml(eml(x,x),x))", coeff: 0.326227 },
      { formula: "eml(eml(1,x),eml(1,x))", coeff: 0.003296 },
      { formula: "eml(eml(1,eml(1,x)),1)", coeff: 0.141571 },
      { formula: "eml(eml(x,eml(1,x)),x)", coeff: -0.000179 },
    ],
  },
  cos: {
    K: 5,
    mse_train: 1.061e-4,
    mse_test: 3.885e-3,
    n_dict_atoms: 79,
    formula: "K=5 atoms (run search for details)",
    atoms: [],
  },
  exp: {
    K: 1,
    mse_train: 7.094e-31,
    mse_test: 8.037e-31,
    n_dict_atoms: 79,
    formula: "exp(x) is a native EML operation — machine precision at K=1",
    atoms: [{ formula: "eml(x, 1) = exp(x) - ln(1) = exp(x)", coeff: 1.0 }],
  },
  log: {
    K: 1,
    mse_train: 7.447e-32,
    mse_test: 6.023e-32,
    n_dict_atoms: 79,
    formula: "log(x) is a native EML operation — machine precision at K=1",
    atoms: [{ formula: "eml(0, x) = exp(0) - ln(x) = 1 - ln(x) ~ -ln(x)", coeff: -1.0 }],
  },
  sinh: {
    K: 5,
    mse_train: 6.211e-4,
    mse_test: 1.267e-2,
    n_dict_atoms: 79,
    formula: "K=5 atoms (run search for details)",
    atoms: [],
  },
  cosh: {
    K: 5,
    mse_train: 7.949e-6,
    mse_test: 1.185e-4,
    n_dict_atoms: 79,
    formula: "K=5 atoms (run search for details)",
    atoms: [],
  },
};

function MSEBadge({ value }) {
  const color =
    value < 1e-20 ? "#22c55e" :
    value < 1e-6  ? "#84cc16" :
    value < 1e-3  ? "#f59e0b" :
                    "#ef4444";
  return (
    <span style={{
      background: color,
      color: "#000",
      borderRadius: 4,
      padding: "2px 8px",
      fontSize: "0.85em",
      fontFamily: "monospace",
    }}>
      {value.toExponential(2)}
    </span>
  );
}

function SparsityBar({ K, maxK = 8 }) {
  return (
    <div style={{ display: "flex", gap: 4, alignItems: "center" }}>
      {Array.from({ length: maxK }, (_, i) => (
        <div
          key={i}
          style={{
            width: 16,
            height: 16,
            borderRadius: 3,
            background: i < K ? "#6366f1" : "#374151",
            border: "1px solid #4b5563",
          }}
        />
      ))}
      <span style={{ marginLeft: 8, color: "#9ca3af", fontSize: "0.85em" }}>
        K = {K}
      </span>
    </div>
  );
}

export default function EMLFourierTab() {
  const [target, setTarget] = useState("sin");
  const [method, setMethod] = useState("omp");
  const [maxN, setMaxN] = useState(3);
  const [showTheory, setShowTheory] = useState(false);

  const result = PRECOMPUTED_RESULTS[target];

  return (
    <div style={{ padding: "24px", maxWidth: 900, margin: "0 auto" }}>
      <h2 style={{ color: "#f3f4f6", marginBottom: 4 }}>EML Fourier Decomposition</h2>
      <p style={{ color: "#9ca3af", marginBottom: 24 }}>
        Session 31 — Can sin(x) be expressed as a short linear combination of EML trees?
        The <strong>Infinite Zeros Barrier</strong> says no single tree equals sin(x),
        but linear combinations may work.
      </p>

      {/* Controls */}
      <div style={{ display: "flex", gap: 16, flexWrap: "wrap", marginBottom: 24 }}>
        <div>
          <label style={{ color: "#9ca3af", fontSize: "0.85em", display: "block", marginBottom: 4 }}>
            Target function
          </label>
          <div style={{ display: "flex", gap: 8 }}>
            {TARGETS.map(t => (
              <button
                key={t}
                onClick={() => setTarget(t)}
                style={{
                  padding: "6px 14px",
                  borderRadius: 6,
                  border: "1px solid",
                  borderColor: target === t ? "#6366f1" : "#374151",
                  background: target === t ? "#312e81" : "#1f2937",
                  color: target === t ? "#e0e7ff" : "#9ca3af",
                  cursor: "pointer",
                  fontFamily: "monospace",
                }}
              >
                {t}(x)
              </button>
            ))}
          </div>
        </div>

        <div>
          <label style={{ color: "#9ca3af", fontSize: "0.85em", display: "block", marginBottom: 4 }}>
            Method
          </label>
          <div style={{ display: "flex", gap: 8 }}>
            {METHODS.map(m => (
              <button
                key={m}
                onClick={() => setMethod(m)}
                style={{
                  padding: "6px 14px",
                  borderRadius: 6,
                  border: "1px solid",
                  borderColor: method === m ? "#6366f1" : "#374151",
                  background: method === m ? "#312e81" : "#1f2937",
                  color: method === m ? "#e0e7ff" : "#9ca3af",
                  cursor: "pointer",
                  fontSize: "0.85em",
                }}
              >
                {m.toUpperCase()}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Result card */}
      <div style={{
        background: "#111827",
        border: "1px solid #374151",
        borderRadius: 12,
        padding: 24,
        marginBottom: 24,
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 16 }}>
          <div>
            <div style={{ color: "#9ca3af", fontSize: "0.8em", marginBottom: 4 }}>Sparsity</div>
            <SparsityBar K={result.K} />
          </div>
          <div>
            <div style={{ color: "#9ca3af", fontSize: "0.8em", marginBottom: 4 }}>MSE (train)</div>
            <MSEBadge value={result.mse_train} />
          </div>
          <div>
            <div style={{ color: "#9ca3af", fontSize: "0.8em", marginBottom: 4 }}>MSE (test)</div>
            <MSEBadge value={result.mse_test} />
          </div>
          <div>
            <div style={{ color: "#9ca3af", fontSize: "0.8em", marginBottom: 4 }}>Dict size</div>
            <span style={{ color: "#e5e7eb", fontFamily: "monospace" }}>{result.n_dict_atoms} atoms</span>
          </div>
        </div>

        {result.atoms.length > 0 && (
          <div style={{ marginTop: 20 }}>
            <div style={{ color: "#9ca3af", fontSize: "0.85em", marginBottom: 8 }}>Selected atoms</div>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  <th style={{ textAlign: "left", color: "#6b7280", fontSize: "0.8em", paddingBottom: 6 }}>#</th>
                  <th style={{ textAlign: "left", color: "#6b7280", fontSize: "0.8em", paddingBottom: 6 }}>Coefficient</th>
                  <th style={{ textAlign: "left", color: "#6b7280", fontSize: "0.8em", paddingBottom: 6 }}>EML Formula</th>
                </tr>
              </thead>
              <tbody>
                {result.atoms.map((a, i) => (
                  <tr key={i} style={{ borderTop: "1px solid #1f2937" }}>
                    <td style={{ padding: "6px 0", color: "#6b7280", fontSize: "0.85em" }}>{i + 1}</td>
                    <td style={{ padding: "6px 16px 6px 0", color: "#a5b4fc", fontFamily: "monospace", fontSize: "0.85em" }}>
                      {a.coeff >= 0 ? "+" : ""}{a.coeff.toFixed(6)}
                    </td>
                    <td style={{ padding: "6px 0", color: "#e5e7eb", fontFamily: "monospace", fontSize: "0.85em" }}>
                      {a.formula}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Summary table */}
      <div style={{ marginBottom: 24 }}>
        <h3 style={{ color: "#d1d5db", marginBottom: 12 }}>All Targets — N≤3 Dictionary</h3>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.9em" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid #374151" }}>
              {["Target", "K", "MSE (train)", "MSE (test)", "Classification"].map(h => (
                <th key={h} style={{ textAlign: "left", color: "#6b7280", padding: "8px 12px" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {Object.entries(PRECOMPUTED_RESULTS).map(([name, r]) => (
              <tr
                key={name}
                onClick={() => setTarget(name)}
                style={{
                  borderBottom: "1px solid #1f2937",
                  cursor: "pointer",
                  background: target === name ? "#1e1b4b" : "transparent",
                }}
              >
                <td style={{ padding: "8px 12px", color: "#e5e7eb", fontFamily: "monospace" }}>{name}(x)</td>
                <td style={{ padding: "8px 12px", color: "#a5b4fc" }}>{r.K}</td>
                <td style={{ padding: "8px 12px" }}><MSEBadge value={r.mse_train} /></td>
                <td style={{ padding: "8px 12px" }}><MSEBadge value={r.mse_test} /></td>
                <td style={{ padding: "8px 12px", color: "#9ca3af", fontSize: "0.85em" }}>
                  {r.mse_test < 1e-20 ? "EML-native (exact)" :
                   r.mse_test < 1e-4  ? "EML-Fourier (tight)" :
                   r.mse_test < 1e-1  ? "EML-Fourier (partial)" :
                   "EML-Fourier (loose)"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Theory panel */}
      <button
        onClick={() => setShowTheory(!showTheory)}
        style={{
          background: "none",
          border: "1px solid #374151",
          color: "#9ca3af",
          borderRadius: 6,
          padding: "6px 16px",
          cursor: "pointer",
          marginBottom: 12,
        }}
      >
        {showTheory ? "Hide" : "Show"} theory
      </button>

      {showTheory && (
        <div style={{
          background: "#0f172a",
          border: "1px solid #1e3a5f",
          borderRadius: 8,
          padding: 20,
          color: "#94a3b8",
          fontSize: "0.9em",
          lineHeight: 1.7,
        }}>
          <strong style={{ color: "#e2e8f0" }}>EML Fourier Theorem (Session 31)</strong>
          <br />
          <br />
          The Infinite Zeros Barrier proves: no single EML tree T satisfies T(x) = sin(x),
          because sin has infinitely many zeros while every depth-k EML tree has at most 2^k zeros.
          <br /><br />
          But sin(x) may still be expressible as a linear combination:
          <br />
          <code style={{ color: "#93c5fd" }}>sin(x) ≈ c₁·T₁(x) + c₂·T₂(x) + ... + c_K·T_K(x)</code>
          <br /><br />
          <strong style={{ color: "#e2e8f0" }}>Session 31 result:</strong> K=5, MSE_test=2.3e-2.
          Not machine precision, but a real decomposition. exp(x) and log(x) are EML-native
          (K=1, MSE≈1e-31) since they are literally single EML operations.
          <br /><br />
          <strong style={{ color: "#e2e8f0" }}>Method:</strong> OMP (Orthogonal Matching Pursuit)
          over a dictionary of 79 valid EML atoms with N≤3 internal nodes.
          Run <code style={{ color: "#93c5fd" }}>python -m pytest tests/test_eml_fourier.py -v -s</code> for live results.
        </div>
      )}
    </div>
  );
}
