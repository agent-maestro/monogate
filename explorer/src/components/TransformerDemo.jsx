// explorer/src/components/TransformerDemo.jsx
// Transformer activation benchmark demo.
// Live JS timing: sin_best (BEST, 63n) vs sin_eml_taylor (EML, 245n).
// Python FFN numbers hardcoded from experiment_10 (Python 3.14, CPU).

import { useState, useEffect } from "react";
import { sin_best } from "../eml.js";

const C = {
  bg: "#07080f", surface: "#0d0e1c", border: "#191b2e",
  text: "#cdd0e0", muted: "#4e5168", accent: "#e8a020",
  blue: "#6ab0f5", green: "#5ec47a", red: "#e05060",
};

// ── EML 8-term sin (same as calc-engine's sin_eml_taylor, no import needed) ──
function sin_eml(x) {
  let sum = 0, xpow = x, fact = 1;
  for (let k = 0; k < 8; k++) {
    sum  += (k % 2 === 0 ? 1 : -1) * xpow / fact;
    xpow *= x * x;
    fact *= (2 * k + 2) * (2 * k + 3);
  }
  return sum;
}

// ── Hardcoded results from Python experiment_10 ───────────────────────────────
const EXP10 = {
  // Section C: FFN forward (d=16, hidden=64, batch=8)
  native_ms: 1.771,
  eml_ms:    4.736,
  best_ms:   5.115,
  eml_vs_best_speedup: 0.93,
  best_overhead: 2.9,
  note: "Python 3.14 · CPU · d=16, 4× hidden=64, batch=8",
  // Section A: single GELU call
  gelu_eml_nodes: 17,
  gelu_best_nodes: 14,
  gelu_savings_pct: 18,
  // Section D: sin vs GELU node savings
  sin_savings_pct: 74,
  sin_speedup_py: 3.26,
};

// ── Python code snippets ───────────────────────────────────────────────────────
const CODE_EML = `# Pure EML arithmetic
from monogate import gelu_eml_approx

def ffn_forward(x, W1, b1, W2, b2):
    # Linear → GELU → Linear
    h = [
        sum(W1[j][i]*x[i] for i in range(d)) + b1[j]
        for j in range(d_hid)
    ]
    h_act = [gelu_eml_approx(v) for v in h]
    return [
        sum(W2[k][j]*h_act[j] for j in range(d_hid)) + b2[k]
        for k in range(d)
    ]

# 17 nodes per GELU call:
#   exp_eml (1n) + add_eml (11n) + recip_eml (5n)`;

const CODE_BEST = `# BEST-routed arithmetic
from monogate import gelu_best_approx

def ffn_forward(x, W1, b1, W2, b2):
    # Same structure — GELU uses EDL recip
    h = [
        sum(W1[j][i]*x[i] for i in range(d)) + b1[j]
        for j in range(d_hid)
    ]
    h_act = [gelu_best_approx(v) for v in h]
    return [
        sum(W2[k][j]*h_act[j] for j in range(d_hid)) + b2[k]
        for k in range(d)
    ]

# 14 nodes per GELU call:
#   exp (1n) + add_eml (11n) + recip_edl (2n)`;

// ── Component ─────────────────────────────────────────────────────────────────
export default function TransformerDemo() {
  const [bench, setBench] = useState(null);  // { us_eml, us_best, speedup, ratio }

  // Run live JS timing once on mount
  useEffect(() => {
    const N  = 2000;
    const xs = Array.from({ length: N }, (_, i) => 0.1 + (i / N) * 2.8);  // (0.1, 2.9] — valid for pow_exl

    // Warm up
    for (let i = 0; i < 50; i++) { sin_eml(xs[i]); sin_best(xs[i]); }

    const t0 = performance.now();
    for (let i = 0; i < N; i++) sin_eml(xs[i]);
    const t_eml = performance.now() - t0;

    const t1 = performance.now();
    for (let i = 0; i < N; i++) sin_best(xs[i]);
    const t_best = performance.now() - t1;

    const us_eml  = (t_eml  / N) * 1000;
    const us_best = (t_best / N) * 1000;

    setBench({
      us_eml,
      us_best,
      speedup: t_eml / t_best,
      eml_nodes:  245,
      best_nodes:  63,
    });
  }, []);

  return (
    <div style={{ color: C.text }}>
      {/* Header */}
      <div style={{ fontSize: 10, color: C.muted, marginBottom: 16, lineHeight: 1.8 }}>
        How BEST routing improves real neural network workloads.
        Live JS benchmark uses <span style={{ color: C.accent }}>sin(x)</span> (245n EML vs 63n BEST).
        Python FFN numbers are from{" "}
        <span style={{ color: C.accent }}>experiment_10</span> using the tanh-GELU formula
        (17n EML vs 14n BEST).
      </div>

      {/* Architecture diagram */}
      <div style={{
        background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8,
        padding: "14px 20px", marginBottom: 16, display: "flex", alignItems: "center",
        gap: 12, flexWrap: "wrap",
      }}>
        <div style={{ fontSize: 9, color: C.muted, textTransform: "uppercase", letterSpacing: "0.08em" }}>
          FFN block:
        </div>
        {["Input x", "Linear (d→4d)", "Activation", "Linear (4d→d)", "Output"].map((label, i, arr) => (
          <div key={label} style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{
              background: i === 2 ? "rgba(232,160,32,0.12)" : "rgba(255,255,255,0.04)",
              border: `1px solid ${i === 2 ? C.accent : C.border}`,
              borderRadius: 5, padding: "5px 10px", fontSize: 10,
              color: i === 2 ? C.accent : C.text,
            }}>
              {label}
              {i === 2 && <div style={{ fontSize: 8, color: C.muted, marginTop: 2 }}>← BEST here</div>}
            </div>
            {i < arr.length - 1 && <span style={{ color: C.muted, fontSize: 14 }}>→</span>}
          </div>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
        {/* Live JS timing */}
        <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8, padding: 14 }}>
          <div style={{ fontSize: 9, color: C.muted, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 12 }}>
            Live JS benchmark — sin(x) activation
          </div>
          <div style={{ fontSize: 8, color: C.muted, marginBottom: 10 }}>
            2 000 calls · same formula, different routing · this browser
          </div>

          {bench ? (
            <>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginBottom: 12 }}>
                {[
                  { label: "EML", us: bench.us_eml,  nodes: bench.eml_nodes,  col: C.muted },
                  { label: "BEST", us: bench.us_best, nodes: bench.best_nodes, col: C.accent },
                ].map(({ label, us, nodes, col }) => (
                  <div key={label} style={{ background: C.bg, borderRadius: 6, padding: "10px 12px" }}>
                    <div style={{ fontSize: 9, color: C.muted, marginBottom: 4 }}>{label}</div>
                    <div style={{ fontSize: 18, fontWeight: 700, color: col }}>{us.toFixed(1)}</div>
                    <div style={{ fontSize: 8, color: C.muted }}>μs/call · {nodes}n</div>
                  </div>
                ))}
              </div>

              <div style={{
                background: "rgba(94,196,122,0.08)", border: "1px solid rgba(94,196,122,0.25)",
                borderRadius: 6, padding: "8px 12px", fontSize: 11,
              }}>
                <span style={{ color: C.green }}>
                  {bench.speedup.toFixed(2)}× faster
                </span>
                <span style={{ color: C.muted, fontSize: 9, marginLeft: 8 }}>
                  ({Math.round((1 - 63/245)*100)}% fewer nodes → {bench.speedup.toFixed(2)}× wall-clock)
                </span>
              </div>

              {/* Bar comparison */}
              <div style={{ marginTop: 12 }}>
                {[
                  { label: "EML sin", n: 245, col: C.muted + "88" },
                  { label: "BEST sin", n: 63, col: C.accent },
                ].map(({ label, n, col }) => (
                  <div key={label} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                    <div style={{ fontSize: 9, color: C.muted, width: 64 }}>{label}</div>
                    <div style={{
                      height: 10, borderRadius: 3,
                      width: `${Math.round((n / 245) * 160)}px`,
                      background: col,
                    }} />
                    <div style={{ fontSize: 9, color: C.muted }}>{n}n</div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div style={{ fontSize: 10, color: C.muted }}>Running benchmark…</div>
          )}
        </div>

        {/* Python FFN results */}
        <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8, padding: 14 }}>
          <div style={{ fontSize: 9, color: C.muted, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 6 }}>
            Python FFN benchmark
          </div>
          <div style={{ fontSize: 8, color: C.muted, marginBottom: 12 }}>
            from experiment_10 (CPU benchmark) · {EXP10.note}
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 6, marginBottom: 12 }}>
            {[
              { label: "native math", ms: EXP10.native_ms, col: C.blue,   sub: "Math.tanh" },
              { label: "EML-GELU",    ms: EXP10.eml_ms,    col: C.muted,  sub: "17 nodes" },
              { label: "BEST-GELU",   ms: EXP10.best_ms,   col: C.accent, sub: "14 nodes" },
            ].map(({ label, ms, col, sub }) => (
              <div key={label} style={{ background: C.bg, borderRadius: 6, padding: "8px 10px" }}>
                <div style={{ fontSize: 8, color: C.muted, marginBottom: 4 }}>{label}</div>
                <div style={{ fontSize: 15, fontWeight: 700, color: col }}>{ms.toFixed(3)}</div>
                <div style={{ fontSize: 8, color: C.muted }}>ms/fwd · {sub}</div>
              </div>
            ))}
          </div>

          <div style={{
            background: "rgba(106,176,245,0.08)", border: "1px solid rgba(106,176,245,0.2)",
            borderRadius: 6, padding: "8px 12px", fontSize: 10, color: C.blue, marginBottom: 10,
          }}>
            18% node reduction (GELU) → {EXP10.eml_vs_best_speedup}× speedup — below Python call overhead
          </div>

          {/* GELU node cost breakdown */}
          <div style={{ fontSize: 9, color: C.muted, marginBottom: 6 }}>GELU node cost breakdown:</div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 4, fontSize: 9 }}>
            {[
              { op: "exp",   eml: 1,  best: 1,  via: "EML" },
              { op: "add",   eml: 11, best: 11, via: "EML" },
              { op: "recip", eml: 5,  best: 2,  via: "EDL" },
            ].map(({ op, eml, best, via }) => (
              <div key={op} style={{
                background: C.bg, borderRadius: 4, padding: "5px 8px",
                border: `1px solid ${C.border}`,
              }}>
                <div style={{ color: C.text }}>{op}</div>
                <div style={{ color: C.accent }}>{best}n <span style={{ fontSize: 7, color: C.muted }}>BEST</span></div>
                <div style={{ color: C.muted }}>{eml}n <span style={{ fontSize: 7 }}>EML</span></div>
                <div style={{ fontSize: 7, color:
                  via === "EDL" ? "#2dd4bf" : via === "EXL" ? "#f59e0b" : "#7c6ff7",
                  marginTop: 2,
                }}>{via}</div>
              </div>
            ))}
          </div>
          <div style={{ marginTop: 8, fontSize: 9, color: C.muted }}>
            Total: <span style={{ color: C.accent }}>14n</span> BEST vs{" "}
            <span style={{ color: C.muted }}>17n</span> EML
          </div>
        </div>
      </div>

      {/* Python code side by side */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 16 }}>
        {[
          { title: "Pure EML", col: C.muted, code: CODE_EML },
          { title: "BEST Optimized", col: C.accent, code: CODE_BEST },
        ].map(({ title, col, code }) => (
          <div key={title} style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8, overflow: "hidden" }}>
            <div style={{
              padding: "8px 14px", borderBottom: `1px solid ${C.border}`,
              fontSize: 9, color: col, textTransform: "uppercase", letterSpacing: "0.08em",
            }}>
              {title}
            </div>
            <pre style={{
              margin: 0, padding: "12px 14px", fontSize: 9, lineHeight: 1.6,
              color: C.muted, fontFamily: "'Space Mono',monospace", overflowX: "auto",
            }}>
              {code}
            </pre>
          </div>
        ))}
      </div>

      {/* Key insight */}
      <div style={{
        background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8,
        padding: "14px 18px", display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16,
      }}>
        <div>
          <div style={{ fontSize: 9, color: C.muted, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 8 }}>
            Key insight: savings must exceed overhead
          </div>
          <div style={{ fontSize: 10, color: C.text, lineHeight: 1.7 }}>
            GELU saves 18% of nodes. In Python, function-call overhead (~5 μs/call)
            swamps that saving — speedup is effectively 1×.
          </div>
          <div style={{ marginTop: 8, fontSize: 10, color: C.text, lineHeight: 1.7 }}>
            sin/cos save <span style={{ color: C.green }}>74%</span> of nodes.
            That reduction is large enough to overcome overhead →{" "}
            <span style={{ color: C.green }}>3.26× wall-clock speedup</span> in Python.
          </div>
        </div>
        <div>
          <div style={{ fontSize: 9, color: C.muted, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 8 }}>
            Savings vs speedup
          </div>
          {[
            { fn: "GELU",    pct: 18, speedup: "~1×",  col: C.muted  },
            { fn: "sin/cos", pct: 74, speedup: "3.26×", col: C.green  },
            { fn: "div",     pct: 93, speedup: "—",     col: C.accent },
            { fn: "pow",     pct: 80, speedup: "4.77×", col: C.accent },
          ].map(({ fn, pct, speedup, col }) => (
            <div key={fn} style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
              <div style={{ width: 48, fontSize: 10, color: C.text }}>{fn}</div>
              <div style={{
                height: 10, borderRadius: 3,
                width: `${Math.round(pct * 1.4)}px`,
                background: col + "88",
                border: `1px solid ${col}44`,
              }} />
              <div style={{ fontSize: 9, color: C.muted }}>{pct}% nodes</div>
              <div style={{ fontSize: 9, color: col, marginLeft: "auto" }}>{speedup}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
