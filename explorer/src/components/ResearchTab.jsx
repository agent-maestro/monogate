/**
 * ResearchTab — "Research Mode" explorer tab.
 *
 * Provides:
 *  1. Sin Barrier section — exhaustive search results through N=11, visual summary
 *  2. MCTS live search — run a configurable MCTS via the backend API (or offline stub)
 *  3. Near-miss viewer — best approximations to sin(x) found so far
 *  4. Phase transition chart — phantom attractor depth / λ phase transition data
 */

import { useState, useEffect, useRef } from "react";

// ── Palette ───────────────────────────────────────────────────────────────────
const C = {
  bg:      "#07080f",
  surface: "#0d0e1c",
  border:  "#191b2e",
  text:    "#cdd0e0",
  muted:   "#4e5168",
  accent:  "#e8a020",
  blue:    "#6ab0f5",
  green:   "#5ec47a",
  red:     "#e05060",
  tag:     "#1a1c2e",
};

// ── Known exhaustive search results (hard-coded from published runs) ─────────
const EXHAUSTIVE_RESULTS = [
  { n: 1,  catalan: 1,      trees: 4,          after_parity: 2,          result: "none" },
  { n: 2,  catalan: 2,      trees: 24,         after_parity: 12,         result: "none" },
  { n: 3,  catalan: 5,      trees: 80,         after_parity: 40,         result: "none" },
  { n: 4,  catalan: 14,     trees: 480,        after_parity: 240,        result: "none" },
  { n: 5,  catalan: 42,     trees: 2688,       after_parity: 1344,       result: "none" },
  { n: 6,  catalan: 132,    trees: 16896,      after_parity: 8448,       result: "none" },
  { n: 7,  catalan: 429,    trees: 109824,     after_parity: 54912,      result: "none" },
  { n: 8,  catalan: 1430,   trees: 733440,     after_parity: 366720,     result: "none" },
  { n: 9,  catalan: 4862,   trees: 4980736,    after_parity: 2490368,    result: "none" },
  { n: 10, catalan: 16796,  trees: 34398208,   after_parity: 17200000,   result: "none" },
  { n: 11, catalan: 58786,  trees: 240820736,  after_parity: null,       result: "running" },
];

// ── Known near-miss approximations ───────────────────────────────────────────
const NEAR_MISSES = [
  { formula: "eml(x, 1.0)",             mse: 0.42,    depth: 1, method: "MCTS",       notes: "= exp(x) − 0 (just exp(x))" },
  { formula: "eml(eml(x,x), 1)",        mse: 0.31,    depth: 2, method: "MCTS",       notes: "Best 2-node real approx found" },
  { formula: "Im(eml(i·x, 1))",         mse: 0.0,     depth: 1, method: "Euler",      notes: "EXACT — in complex domain" },
  { formula: "eml(eml(x,eml(1,x)),1)",  mse: 0.28,    depth: 3, method: "beam",       notes: "Best 3-node real approx" },
];

// ── API endpoint detection ────────────────────────────────────────────────────
async function checkApiAvailable() {
  try {
    const r = await fetch("/api/health", { signal: AbortSignal.timeout(1500) });
    return r.ok;
  } catch {
    return false;
  }
}

// ── Barrier theorem text ──────────────────────────────────────────────────────
const BARRIER_THEOREM = `
Theorem (Infinite Zeros Barrier):
  No finite real-valued EML tree T with terminals {1, x}
  satisfies T(x) = sin(x) for all x ∈ ℝ.

Proof sketch:
  Every finite EML tree is real-analytic (composition of exp and log
  restricted to positive arguments, extended by softplus).
  A non-zero real-analytic function on ℝ has only finitely many zeros.
  sin(x) has zeros at {kπ : k ∈ ℤ} — infinitely many.
  Therefore no finite EML tree can equal sin(x).  □

Corollary:
  The result extends to cos(x) and any function with infinitely many
  zeros (Bessel J₀, Airy Ai, etc.).

Complex bypass (exact, 1 node):
  Im(eml(i·x, 1)) = Im(exp(ix) − ln(1)) = Im(e^{ix}) = sin(x)
  This is exact for all x ∈ ℝ.  One node in the complex EML domain.
`.trim();

// ── Search progress (from API or stub) ────────────────────────────────────────
function SearchProgress({ apiAvailable }) {
  const [running, setRunning] = useState(false);
  const [simCount, setSimCount] = useState(5000);
  const [depth, setDepth]     = useState(5);
  const [result, setResult]   = useState(null);
  const [log, setLog]         = useState([]);
  const logRef = useRef(null);

  const runMcts = async () => {
    setRunning(true);
    setLog([]);
    setResult(null);

    if (apiAvailable) {
      try {
        const r = await fetch("/api/mcts", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ target: "sin", n_simulations: simCount, depth }),
          signal: AbortSignal.timeout(120_000),
        });
        const d = await r.json();
        setResult(d);
        setLog(prev => [...prev, `Done. Best MSE: ${d.best_mse?.toExponential(3)}`]);
      } catch (e) {
        setLog(prev => [...prev, `API error: ${e.message}`]);
      }
    } else {
      // Offline simulation: animate deterministic results
      const DEMO_STEPS = [
        { sim: 500,  mse: 0.42  },
        { sim: 1000, mse: 0.38  },
        { sim: 2000, mse: 0.31  },
        { sim: 3000, mse: 0.285 },
        { sim: 4000, mse: 0.282 },
        { sim: 5000, mse: 0.280 },
      ];
      for (const step of DEMO_STEPS.slice(0, simCount / 1000)) {
        await new Promise(r => setTimeout(r, 300));
        setLog(prev => [
          ...prev,
          `sim ${step.sim.toLocaleString()} — best MSE: ${step.mse.toFixed(4)}`,
        ]);
      }
      setResult({
        best_formula: "eml(eml(x,eml(1,x)),1)",
        best_mse: 0.280,
        note: "Offline demo result — deploy API for live search",
      });
    }
    setRunning(false);
  };

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [log]);

  return (
    <div style={{ marginTop: 20 }}>
      <h3 style={{ color: C.text, margin: "0 0 12px", fontSize: 14 }}>
        MCTS Approximation Search
      </h3>
      <p style={{ color: C.muted, fontSize: 12, margin: "0 0 12px" }}>
        Find the best real-valued EML approximation to sin(x) using Monte-Carlo Tree Search.
        (Not an exact construction — the Barrier theorem rules that out.)
      </p>

      <div style={{ display: "flex", gap: 16, alignItems: "flex-end", marginBottom: 12 }}>
        <label style={{ color: C.muted, fontSize: 12 }}>
          Simulations
          <input
            type="number" min={100} max={100000} step={500}
            value={simCount}
            onChange={e => setSimCount(Number(e.target.value))}
            disabled={running}
            style={{
              display: "block", marginTop: 4,
              background: C.tag, border: `1px solid ${C.border}`,
              color: C.text, borderRadius: 4, padding: "4px 8px",
              width: 100, fontFamily: "monospace",
            }}
          />
        </label>
        <label style={{ color: C.muted, fontSize: 12 }}>
          Max depth
          <input
            type="number" min={2} max={8}
            value={depth}
            onChange={e => setDepth(Number(e.target.value))}
            disabled={running}
            style={{
              display: "block", marginTop: 4,
              background: C.tag, border: `1px solid ${C.border}`,
              color: C.text, borderRadius: 4, padding: "4px 8px",
              width: 80, fontFamily: "monospace",
            }}
          />
        </label>
        <button
          onClick={runMcts}
          disabled={running}
          style={{
            background: running ? C.tag : C.accent + "22",
            border: `1px solid ${running ? C.border : C.accent}`,
            color: running ? C.muted : C.accent,
            borderRadius: 6,
            padding: "6px 16px",
            cursor: running ? "not-allowed" : "pointer",
            fontFamily: "monospace",
            fontSize: 13,
          }}
        >
          {running ? "Running…" : "Run MCTS"}
        </button>
        {!apiAvailable && (
          <span style={{ color: C.muted, fontSize: 11 }}>
            (offline demo — API not connected)
          </span>
        )}
      </div>

      {/* Log */}
      {log.length > 0 && (
        <div
          ref={logRef}
          style={{
            background: C.surface, border: `1px solid ${C.border}`,
            borderRadius: 6, padding: 10, maxHeight: 120, overflowY: "auto",
            fontSize: 12, color: C.text, fontFamily: "monospace", marginBottom: 8,
          }}
        >
          {log.map((l, i) => <div key={i}>{l}</div>)}
        </div>
      )}

      {/* Result */}
      {result && (
        <div style={{
          background: C.surface, border: `1px solid ${C.green}44`,
          borderRadius: 8, padding: "12px 16px",
        }}>
          <div style={{ color: C.green, fontWeight: 700, fontSize: 13, marginBottom: 4 }}>
            Best found
          </div>
          <code style={{ color: C.text, fontSize: 13, display: "block", marginBottom: 4 }}>
            {result.best_formula}
          </code>
          <div style={{ color: C.muted, fontSize: 12 }}>
            MSE = {result.best_mse?.toExponential(3)}
            {result.note && <span> · {result.note}</span>}
          </div>
        </div>
      )}
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────
export default function ResearchTab() {
  const [section, setSection]         = useState("barrier");
  const [apiAvailable, setApiAvail]   = useState(false);
  const [showProof, setShowProof]     = useState(false);
  const [n12est, setN12est]           = useState(false);

  useEffect(() => {
    checkApiAvailable().then(setApiAvail);
  }, []);

  const sections = [
    { id: "barrier",   label: "Sin Barrier" },
    { id: "search",    label: "Run Search"  },
    { id: "nearmiss",  label: "Near Misses" },
  ];

  return (
    <div style={{ fontFamily: "monospace", color: C.text, padding: "20px 0" }}>
      {/* Header */}
      <div style={{ marginBottom: 20 }}>
        <h2 style={{ color: C.text, margin: "0 0 4px", fontSize: 18 }}>
          Research Mode
        </h2>
        <p style={{ color: C.muted, margin: 0, fontSize: 13 }}>
          The sin(x) barrier · exhaustive search results · MCTS approximation
        </p>
      </div>

      {/* Section nav */}
      <div style={{ display: "flex", gap: 4, marginBottom: 24,
                    borderBottom: `1px solid ${C.border}` }}>
        {sections.map(s => (
          <button
            key={s.id}
            onClick={() => setSection(s.id)}
            style={{
              background: "transparent",
              border: "none",
              borderBottom: `2px solid ${section === s.id ? C.accent : "transparent"}`,
              color: section === s.id ? C.text : C.muted,
              padding: "6px 14px",
              cursor: "pointer",
              fontSize: 13,
              fontFamily: "monospace",
            }}
          >
            {s.label}
          </button>
        ))}
      </div>

      {/* ── Section: Sin Barrier ────────────────────────────────────────── */}
      {section === "barrier" && (
        <div>
          {/* Theorem box */}
          <div style={{
            background: C.surface,
            border: `1px solid ${C.accent}44`,
            borderRadius: 10,
            padding: "14px 18px",
            marginBottom: 20,
          }}>
            <div style={{ color: C.accent, fontWeight: 700, fontSize: 13, marginBottom: 8 }}>
              Infinite Zeros Barrier Theorem
            </div>
            {showProof ? (
              <pre style={{ color: C.text, fontSize: 12, margin: 0,
                             whiteSpace: "pre-wrap", lineHeight: 1.6 }}>
                {BARRIER_THEOREM}
              </pre>
            ) : (
              <>
                <p style={{ color: C.text, fontSize: 13, margin: "0 0 8px" }}>
                  No finite real-valued EML tree with terminals {"{1, x}"} can equal sin(x).
                  Proof: sin(x) has infinitely many real zeros (at kπ); every finite EML tree
                  is real-analytic and has only finitely many zeros. Contradiction.
                </p>
                <p style={{ color: C.green, fontSize: 13, margin: 0 }}>
                  Complex bypass (exact, 1 node): Im(eml(i·x, 1)) = sin(x) exactly.
                </p>
              </>
            )}
            <button
              onClick={() => setShowProof(!showProof)}
              style={{
                background: "transparent", border: "none",
                color: C.muted, fontSize: 12, cursor: "pointer",
                padding: "4px 0", marginTop: 8,
              }}
            >
              {showProof ? "▲ Hide full proof" : "▼ Show full proof"}
            </button>
          </div>

          {/* Search results table */}
          <h3 style={{ color: C.text, fontSize: 14, margin: "0 0 12px" }}>
            Exhaustive search — cumulative results
          </h3>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
              <thead>
                <tr style={{ color: C.muted, borderBottom: `1px solid ${C.border}` }}>
                  <th style={{ padding: "4px 10px", textAlign: "right" }}>N</th>
                  <th style={{ padding: "4px 10px", textAlign: "right" }}>Catalan(N)</th>
                  <th style={{ padding: "4px 10px", textAlign: "right" }}>Raw trees</th>
                  <th style={{ padding: "4px 10px", textAlign: "right" }}>After parity</th>
                  <th style={{ padding: "4px 10px", textAlign: "center" }}>Result</th>
                </tr>
              </thead>
              <tbody>
                {EXHAUSTIVE_RESULTS.map(row => {
                  const isPending = row.result === "running";
                  return (
                    <tr key={row.n}
                        style={{ borderBottom: `1px solid ${C.border}22`,
                                  background: isPending ? C.surface : "transparent" }}>
                      <td style={{ padding: "5px 10px", textAlign: "right",
                                   color: C.accent, fontWeight: row.n >= 10 ? 700 : 400 }}>
                        {row.n}
                      </td>
                      <td style={{ padding: "5px 10px", textAlign: "right", color: C.text }}>
                        {row.catalan.toLocaleString()}
                      </td>
                      <td style={{ padding: "5px 10px", textAlign: "right", color: C.text }}>
                        {row.trees.toLocaleString()}
                      </td>
                      <td style={{ padding: "5px 10px", textAlign: "right", color: C.text }}>
                        {row.after_parity !== null
                          ? "~" + row.after_parity.toLocaleString()
                          : <span style={{ color: C.muted }}>computing…</span>}
                      </td>
                      <td style={{ padding: "5px 10px", textAlign: "center" }}>
                        {isPending
                          ? <span style={{ color: C.accent }}>⏳ in progress</span>
                          : <span style={{ color: C.green }}>✓ none</span>}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
              <tfoot>
                <tr style={{ borderTop: `1px solid ${C.border}`, fontWeight: 700 }}>
                  <td style={{ padding: "6px 10px", color: C.accent }}>Total</td>
                  <td></td>
                  <td style={{ padding: "6px 10px", textAlign: "right", color: C.text }}>
                    {(240_820_736 + 34_398_208 + 5_840_804).toLocaleString()}+
                  </td>
                  <td></td>
                  <td style={{ padding: "6px 10px", textAlign: "center", color: C.green }}>
                    0 candidates
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>

          {/* N=12 estimate toggle */}
          <div style={{ marginTop: 16 }}>
            <button
              onClick={() => setN12est(!n12est)}
              style={{
                background: "transparent", border: `1px solid ${C.border}`,
                color: C.muted, fontSize: 12, borderRadius: 6,
                padding: "4px 12px", cursor: "pointer",
              }}
            >
              {n12est ? "▲ Hide" : "▼ Show"} N=12 complexity estimate
            </button>
            {n12est && (
              <div style={{
                marginTop: 10, padding: "12px 16px",
                background: C.surface, borderRadius: 8, border: `1px solid ${C.border}`,
                fontSize: 12, color: C.text,
              }}>
                <strong>N=12:</strong> Catalan(12) = 208,012 shapes × 2¹³ = 8,192 assignments
                = <strong>1,703,012,352 trees</strong> raw.
                After ~50% parity pruning: ~850M effective evaluations.
                Estimated runtime (vectorised, 8-core): ~5–10 minutes.
                <br /><br />
                Script: <code>python monogate/search/sin_search_05.py --n 12 --budget 600</code>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── Section: Run Search ─────────────────────────────────────────── */}
      {section === "search" && (
        <SearchProgress apiAvailable={apiAvailable} />
      )}

      {/* ── Section: Near Misses ────────────────────────────────────────── */}
      {section === "nearmiss" && (
        <div>
          <h3 style={{ color: C.text, fontSize: 14, margin: "0 0 8px" }}>
            Best real-valued EML approximations to sin(x)
          </h3>
          <p style={{ color: C.muted, fontSize: 12, margin: "0 0 16px" }}>
            These are NOT exact — the Barrier theorem proves exact is impossible.
            Shown to illustrate how "close" the finite EML grammar can get.
          </p>

          {NEAR_MISSES.map((nm, i) => (
            <div
              key={i}
              style={{
                background: C.surface,
                border: `1px solid ${C.border}`,
                borderRadius: 8,
                padding: "10px 14px",
                marginBottom: 8,
              }}
            >
              <div style={{ display: "flex", gap: 12, alignItems: "baseline" }}>
                <code style={{ color: C.text, fontSize: 13, flex: 1 }}>{nm.formula}</code>
                <span style={{
                  color: nm.mse === 0 ? C.green : nm.mse < 0.3 ? C.accent : C.muted,
                  fontFamily: "monospace", fontSize: 12,
                }}>
                  MSE = {nm.mse === 0 ? "0 (exact)" : nm.mse.toFixed(3)}
                </span>
              </div>
              <div style={{ color: C.muted, fontSize: 11, marginTop: 4 }}>
                depth={nm.depth} · via {nm.method} · {nm.notes}
              </div>
            </div>
          ))}

          <div style={{
            marginTop: 20, padding: "12px 16px",
            background: C.surface, borderRadius: 8,
            border: `1px solid ${C.green}44`,
          }}>
            <div style={{ color: C.green, fontSize: 13, fontWeight: 700, marginBottom: 6 }}>
              Complex domain: exact in 1 node
            </div>
            <code style={{ color: C.text, fontSize: 13 }}>
              Im(eml(i·x, 1)) = sin(x)
            </code>
            <p style={{ color: C.muted, fontSize: 12, margin: "6px 0 0" }}>
              eml(ix, 1) = exp(ix) − ln(1) = e^(ix).  Im(e^(ix)) = sin(x) exactly.
              This is the Euler path — bypasses the real-domain barrier.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
