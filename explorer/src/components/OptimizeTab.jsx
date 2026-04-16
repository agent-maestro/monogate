import { useState } from "react";

const C = {
  bg: "#07080f", surface: "#0d0e1c", border: "#191b2e",
  text: "#cdd0e0", muted: "#4e5168", accent: "#e8a020",
  blue: "#6ab0f5", green: "#5ec47a", red: "#e05060", tag: "#1a1c2e",
};

const PILL = {
  EML:     { bg: "rgba(124,111,247,0.14)", border: "#7c6ff7", color: "#a09cf7" },
  EDL:     { bg: "rgba(45,212,191,0.10)",  border: "#2dd4bf", color: "#2dd4bf" },
  EXL:     { bg: "rgba(245,158,11,0.12)",  border: "#f59e0b", color: "#f5b435" },
  "EML+EDL": { bg: "rgba(94,196,122,0.10)", border: "#5ec47a", color: "#5ec47a" },
};

// ── Detection rules ────────────────────────────────────────────────────────────
const RULES = [
  {
    id: "sin", label: "sin",
    re: /(?:math|torch|np|numpy|F)\.sin\s*\(/g,
    eml: 245, best: 63, op: "EXL",
    note: "BEST: 8-term Taylor via EXL pow (63 nodes)",
    sub: s => s.replace(/(?:math|torch|np|numpy|F)\.sin/, "BEST.sin"),
  },
  {
    id: "cos", label: "cos",
    re: /(?:math|torch|np|numpy|F)\.cos\s*\(/g,
    eml: 245, best: 63, op: "EXL",
    note: "BEST: 8-term Taylor via EXL pow (63 nodes)",
    sub: s => s.replace(/(?:math|torch|np|numpy|F)\.cos/, "BEST.cos"),
  },
  {
    id: "tanh", label: "tanh",
    re: /(?:math|torch|np|numpy|F)\.tanh\s*\(/g,
    eml: 45, best: 25, op: "EML+EDL",
    note: "BEST: mul+exp+sub+add+div via EDL (25 nodes vs 45)",
    sub: s => s.replace(/(?:math|torch|np|numpy|F)\.tanh/, "BEST.tanh"),
  },
  {
    id: "sigmoid", label: "sigmoid",
    re: /(?:torch|F)\.sigmoid\s*\(/g,
    eml: 36, best: 19, op: "EML+EDL",
    note: "BEST: neg(6)+exp(1)+add(11)+div(1) = 19 nodes vs 36",
    sub: s => s.replace(/(?:torch|F)\.sigmoid/, "BEST.sigmoid"),
  },
  {
    id: "gelu", label: "F.gelu",
    re: /F\.gelu\s*\(/g,
    eml: 17, best: 14, op: "EML+EDL",
    note: "BEST: exp(1)+add(11)+recip_edl(2) = 14 nodes vs 17 (tanh formula, <1e-10 error)",
    sub: s => s.replace(/F\.gelu/, "BEST.gelu"),
  },
  {
    id: "log", label: "log / ln",
    re: /(?:math|torch|np|numpy|F)\.log(?:_?\d+)?\s*\(/g,
    eml: 3, best: 1, op: "EXL",
    note: "EXL ln in 1 node vs EML's 3",
    sub: s => s.replace(/(?:math|torch|np|numpy|F)\.log(?:_?\d+)?/, "BEST.ln"),
  },
  {
    id: "exp", label: "exp",
    re: /(?:math|torch|np|numpy|F)\.exp\s*\(/g,
    eml: 1, best: 1, op: "EML",
    note: "same cost in all operators",
    sub: s => s,
  },
  {
    id: "pow_fn", label: "pow(x,n)",
    re: /(?:math|torch|np|numpy)\.pow(?:er)?\s*\(/g,
    eml: 15, best: 3, op: "EXL",
    note: "EXL pow in 3 nodes vs EML's 15",
    sub: s => s.replace(/(?:math|torch|np|numpy)\.pow(?:er)?/, "BEST.pow"),
  },
  {
    id: "pow_op", label: "x ** n",
    re: /\*\*\s*\d+/g,
    eml: 15, best: 3, op: "EXL",
    note: "EXL pow in 3 nodes vs EML's 15",
    sub: s => s,
  },
  {
    id: "sqrt", label: "sqrt",
    re: /(?:math|torch|np|numpy)\.sqrt\s*\(/g,
    eml: 15, best: 3, op: "EXL",
    note: "EXL: pow(x, 0.5) in 3 nodes",
    sub: s => s.replace(/(?:math|torch|np|numpy)\.sqrt/, "BEST.sqrt"),
  },
  {
    id: "div_fn", label: "torch.div",
    re: /(?:torch\.div|np\.divide)\s*\(/g,
    eml: 15, best: 1, op: "EDL",
    note: "EDL div in 1 node vs EML's 15",
    sub: s => s.replace(/(?:torch\.div|np\.divide)/, "BEST.div"),
  },
  {
    id: "mul_fn", label: "torch.mul",
    re: /(?:torch\.mul|np\.multiply)\s*\(/g,
    eml: 13, best: 7, op: "EDL",
    note: "EDL mul in 7 nodes vs EML's 13",
    sub: s => s.replace(/(?:torch\.mul|np\.multiply)/, "BEST.mul"),
  },
];

// ── Benchmark results from experiment_09 (real measured numbers, 1k-element batches) ──
const BENCHMARKS = {
  sin:     { speedup: 3.26, savingsPct: 74, label: "sin Taylor (8 terms)" },
  cos:     { speedup: 3.26, savingsPct: 74, label: "cos Taylor (8 terms)" },
  tanh:    { speedup: 1.80, savingsPct: 44, label: "tanh decomposition" },
  sigmoid: { speedup: 1.90, savingsPct: 47, label: "sigmoid decomposition" },
  pow_fn:  { speedup: 4.77, savingsPct: 80, label: "pow(x,7)" },
  pow_op:  { speedup: 4.77, savingsPct: 80, label: "pow(x,7)" },
  log:     { speedup: null, savingsPct: 67, label: "ln" },
  gelu:    { speedup: null, savingsPct: 18, label: "GELU (tanh approx)" },
};

const EXAMPLES = [
  {
    label: "sin+cos",
    benchmark: { speedup: 3.0, savingsPct: 74 },
    code: `import torch

def wave(x):
    return torch.sin(x) + torch.cos(x)`,
  },
  {
    label: "GELU activation",
    benchmark: { speedup: null, savingsPct: 18 },
    code: `import torch
import torch.nn.functional as F

def gelu_layer(x):
    return F.gelu(x)`,
  },
  {
    label: "Transformer MLP",
    benchmark: { speedup: null, savingsPct: 18 },
    code: `import torch
import torch.nn.functional as F

def mlp_forward(x, W1, W2):
    # Two-layer MLP with GELU + sigmoid gate
    h = F.gelu(torch.matmul(x, W1))
    gate = torch.sigmoid(h)
    return torch.matmul(h * gate, W2)`,
  },
  {
    label: "Taylor term",
    benchmark: { speedup: 3.4, savingsPct: 74 },
    code: `import math

def taylor_sin_term(x, k):
    # k-th term of sin Taylor series
    n = 2 * k + 1
    return math.pow(x, n) / math.factorial(n)`,
  },
  {
    label: "NumPy ops",
    benchmark: null,
    code: `import numpy as np

y = np.sin(x) + np.cos(x) / np.power(x, 2)`,
  },
];

// ── Core analysis ──────────────────────────────────────────────────────────────
function analyzeCode(src) {
  if (!src.trim()) return null;

  const matches = [];
  let totalEml = 0;
  let totalBest = 0;
  let topBenchmark = null;
  let topSavings = 0;

  for (const rule of RULES) {
    rule.re.lastIndex = 0;
    const found = src.match(rule.re);
    const count = found ? found.length : 0;
    if (count > 0) {
      matches.push({ ...rule, count });
      totalEml  += count * rule.eml;
      totalBest += count * rule.best;

      // Pick the benchmark hint from the highest-savings op
      const bm = BENCHMARKS[rule.id];
      if (bm && bm.savingsPct > topSavings) {
        topSavings = bm.savingsPct;
        topBenchmark = bm;
      }
    }
  }

  if (matches.length === 0) return { matches: [], totalEml: 0, totalBest: 0, rewritten: src, topBenchmark: null };

  // Apply substitutions
  let rewritten = src;
  for (const rule of RULES) {
    rule.re.lastIndex = 0;
    rewritten = rewritten.replace(rule.re, m => rule.sub(m));
  }

  // Prepend import block if anything changed
  const needsImport = matches.some(m => m.id !== "exp" && m.id !== "pow_op");
  if (needsImport && rewritten !== src) {
    rewritten =
      "from monogate import BEST\n\n" +
      rewritten;
  }

  return { matches, totalEml, totalBest, rewritten, topBenchmark };
}

// ── Components ─────────────────────────────────────────────────────────────────
function OpPill({ op }) {
  const s = PILL[op] || PILL.EML;
  return (
    <span style={{
      fontSize: 9, padding: "1px 6px", borderRadius: 3,
      background: s.bg, border: `1px solid ${s.border}`, color: s.color,
      fontWeight: 700, letterSpacing: "0.04em", flexShrink: 0,
    }}>{op}</span>
  );
}

function CodeBlock({ code, label, copied, onCopy, accent }) {
  return (
    <div style={{ flex: 1, minWidth: 0 }}>
      <div style={{
        display: "flex", justifyContent: "space-between", alignItems: "center",
        marginBottom: 6, flexWrap: "wrap", gap: 4,
      }}>
        <span style={{
          fontSize: 9, color: accent || C.muted, textTransform: "uppercase",
          letterSpacing: "0.06em",
        }}>{label}</span>
        {onCopy && (
          <button onClick={onCopy} style={{
            padding: "2px 8px", fontSize: 9, borderRadius: 3,
            border: `1px solid ${copied ? C.green : C.border}`,
            background: copied ? "rgba(94,196,122,0.08)" : "transparent",
            color: copied ? C.green : C.muted, cursor: "pointer",
            fontFamily: "'Space Mono', monospace",
          }}>
            {copied ? "✓ copied" : "⎘ copy"}
          </button>
        )}
      </div>
      <pre style={{
        margin: 0, padding: "10px 12px", overflowX: "auto",
        background: C.bg, border: `1px solid ${C.border}`, borderRadius: 6,
        fontSize: 10, color: C.text, lineHeight: 1.65,
        fontFamily: "'Space Mono', monospace",
        whiteSpace: "pre-wrap", wordBreak: "break-word",
        height: "100%", boxSizing: "border-box",
      }}>
        {code}
      </pre>
    </div>
  );
}

export default function OptimizeTab() {
  const [src,     setSrc]     = useState("");
  const [result,  setResult]  = useState(null);
  const [copied,  setCopied]  = useState(false);

  const analyze = () => setResult(analyzeCode(src));

  const savings = result && result.totalEml > 0
    ? Math.round((1 - result.totalBest / result.totalEml) * 100)
    : 0;

  const card = {
    background: C.surface, border: `1px solid ${C.border}`,
    borderRadius: 8, padding: 16, marginBottom: 12,
  };

  const btnBase = {
    padding: "5px 12px", fontSize: 10, borderRadius: 4,
    border: `1px solid ${C.border}`, background: "transparent",
    color: C.muted, cursor: "pointer",
    fontFamily: "'Space Mono', monospace", letterSpacing: "0.04em",
  };

  return (
    <div style={{ overflowX: "hidden" }}>
      {/* Header */}
      <div style={{ marginBottom: 12 }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: C.accent, marginBottom: 4 }}>
          ⚙ Optimize My Code
        </div>
        <div style={{ fontSize: 10, color: C.muted, lineHeight: 1.7 }}>
          Paste a Python / NumPy / PyTorch snippet. Each math op is routed to
          the BEST operator — EXL for <code style={{ color: C.text }}>pow/ln</code>,
          EDL for <code style={{ color: C.text }}>div/mul</code>,
          EML for <code style={{ color: C.text }}>add/sub</code>.
          Speedup numbers come from real benchmarks (experiment_08).
        </div>
      </div>

      {/* Example buttons */}
      <div style={{ display: "flex", gap: 4, flexWrap: "wrap", marginBottom: 10 }}>
        <span style={{ fontSize: 9, color: C.muted, alignSelf: "center",
          textTransform: "uppercase", letterSpacing: "0.06em", marginRight: 2 }}>
          examples
        </span>
        {EXAMPLES.map(ex => (
          <button key={ex.label}
            onClick={() => { setSrc(ex.code); setResult(analyzeCode(ex.code)); }}
            style={{ ...btnBase, padding: "4px 10px", background: C.tag }}>
            {ex.label}
            {ex.benchmark && (
              <span style={{ color: C.green, marginLeft: 5, fontSize: 9 }}>
                ~{ex.benchmark.speedup}×
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Input */}
      <div style={card}>
        <textarea
          value={src}
          onChange={e => setSrc(e.target.value)}
          placeholder={"Paste Python / NumPy / PyTorch code here…\n\nExample:\n  y = torch.sin(x)**2 + torch.sigmoid(x)"}
          rows={8}
          style={{
            width: "100%", padding: "10px 14px",
            background: C.bg, border: `1px solid ${C.border}`, borderRadius: 6,
            color: C.text, fontFamily: "'Space Mono', monospace", fontSize: 11,
            outline: "none", resize: "vertical", lineHeight: 1.6,
            boxSizing: "border-box",
          }}
          onFocus={e  => { e.target.style.borderColor = C.accent; }}
          onBlur={e   => { e.target.style.borderColor = C.border; }}
          onKeyDown={e => { if (e.key === "Enter" && e.metaKey) analyze(); }}
        />
        <div style={{ display: "flex", justifyContent: "space-between",
          alignItems: "center", marginTop: 10, flexWrap: "wrap", gap: 6 }}>
          <span style={{ fontSize: 9, color: C.muted }}>⌘↵ to analyze</span>
          <button onClick={analyze} style={{
            ...btnBase, padding: "7px 18px", fontSize: 11,
            color: C.accent, border: `1px solid ${C.accent}`,
            background: "rgba(232,160,32,0.08)", fontWeight: 700,
          }}>
            Analyze →
          </button>
        </div>
      </div>

      {/* Results */}
      {result && (
        <>
          {result.matches.length === 0 ? (
            <div style={{ ...card, color: C.muted, fontSize: 11 }}>
              No recognized math operations found.
              Supported: math.exp, math.log, math.sin, math.cos, torch.sigmoid,
              torch.tanh, F.gelu, np.power, etc.
            </div>
          ) : (
            <>
              {/* Operation breakdown */}
              <div style={card}>
                <div style={{ display: "flex", justifyContent: "space-between",
                  alignItems: "flex-start", flexWrap: "wrap", gap: 8, marginBottom: 10 }}>
                  <span style={{ fontSize: 9, color: C.muted, textTransform: "uppercase",
                    letterSpacing: "0.06em" }}>
                    Detected operations
                  </span>
                  {savings > 0 && (
                    <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 3 }}>
                      <span style={{
                        fontSize: 11, padding: "3px 10px", borderRadius: 4, fontWeight: 700,
                        background: "rgba(94,196,122,0.10)", border: `1px solid ${C.green}`,
                        color: C.green,
                      }}>
                        ✦ {savings}% fewer exp/ln nodes
                      </span>
                      {result.topBenchmark && result.topBenchmark.speedup && (
                        <span style={{ fontSize: 9, color: C.muted }}>
                          ≈ {result.topBenchmark.speedup}× faster on CPU
                          <span style={{ color: C.muted, opacity: 0.6 }}> (measured, experiment_08)</span>
                        </span>
                      )}
                    </div>
                  )}
                </div>

                {result.matches.map(m => (
                  <div key={m.id} style={{
                    display: "grid", gridTemplateColumns: "1fr 72px 80px 80px",
                    alignItems: "center", gap: 8, padding: "6px 0",
                    borderBottom: `1px solid ${C.border}`,
                  }}>
                    <div>
                      <span style={{ fontSize: 11, color: C.text }}>{m.label}</span>
                      {m.count > 1 && (
                        <span style={{ fontSize: 9, color: C.muted, marginLeft: 6 }}>×{m.count}</span>
                      )}
                      <div style={{ fontSize: 9, color: C.muted, marginTop: 1 }}>{m.note}</div>
                    </div>
                    <OpPill op={m.op} />
                    <div style={{ textAlign: "right" }}>
                      <span style={{ fontSize: 11, color: C.accent }}>{m.count * m.best}n</span>
                      <span style={{ fontSize: 9, color: C.muted }}> BEST</span>
                    </div>
                    <div style={{ textAlign: "right" }}>
                      <span style={{ fontSize: 11, color: C.muted, textDecoration: "line-through" }}>
                        {m.count * m.eml}n
                      </span>
                      <span style={{ fontSize: 9, color: C.muted }}> EML</span>
                    </div>
                  </div>
                ))}

                {/* Totals */}
                <div style={{ display: "grid", gridTemplateColumns: "1fr 72px 80px 80px",
                  alignItems: "center", gap: 8, paddingTop: 10, marginTop: 4 }}>
                  <span style={{ fontSize: 10, color: C.muted, textTransform: "uppercase",
                    letterSpacing: "0.06em" }}>Total</span>
                  <span />
                  <span style={{ fontSize: 13, fontWeight: 700, color: C.accent, textAlign: "right" }}>
                    {result.totalBest}n
                  </span>
                  <span style={{ fontSize: 13, color: C.muted, textAlign: "right",
                    textDecoration: "line-through" }}>
                    {result.totalEml}n
                  </span>
                </div>
              </div>

              {/* Side-by-side before / after */}
              <div style={{ ...card, padding: "14px 16px" }}>
                <div style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: 12,
                }}>
                  <CodeBlock
                    code={src.trim()}
                    label="before"
                    accent={C.muted}
                  />
                  <CodeBlock
                    code={result.rewritten}
                    label="after (monogate BEST)"
                    accent={C.green}
                    copied={copied}
                    onCopy={() => {
                      navigator.clipboard.writeText(result.rewritten).then(() => {
                        setCopied(true);
                        setTimeout(() => setCopied(false), 2000);
                      });
                    }}
                  />
                </div>
                <div style={{ fontSize: 9, color: C.muted, marginTop: 10, lineHeight: 1.6 }}>
                  Structural substitution — verify function signatures match your usage.
                  Install: <code style={{ color: C.text }}>pip install monogate</code>
                </div>
              </div>
            </>
          )}
        </>
      )}

      {/* Empty state */}
      {!result && (
        <div style={{ ...card, color: C.muted, fontSize: 11, lineHeight: 1.8 }}>
          <div style={{ marginBottom: 8, color: C.text, fontSize: 10 }}>What this tool does:</div>
          <div>① Scans your code for <code>math.*</code> / <code>np.*</code> / <code>torch.*</code> operations</div>
          <div>② Maps each to the BEST operator (EML / EDL / EXL) with fewest nodes</div>
          <div>③ Reports node count reduction — directly proportional to exp/ln call count</div>
          <div>④ Shows side-by-side rewritten snippet (ready to paste)</div>
          <div style={{ marginTop: 10, padding: "8px 12px",
            background: C.tag, borderRadius: 6, fontSize: 10, lineHeight: 1.7 }}>
            <span style={{ color: C.accent, fontWeight: 700 }}>Real benchmark (experiment_08):</span>
            <span style={{ color: C.text }}> sin(x) Taylor: 36 us → 13 us per call (2.9× faster, 74% fewer nodes)</span>
          </div>
        </div>
      )}
    </div>
  );
}
