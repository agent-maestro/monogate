import React, { useState } from "react";

const TREE_COLOR = {
  "deml(x, 1)": "#4f9cf9",
  "1 - deml(x, 1)": "#f97316",
  "deml(x*x, 1)": "#a855f7",
  "recip(cosh(x))": "#22c55e",
  "eml(alpha*ln(t_c - t), 1)": "#ef4444",
};

const ANALOGIES = [
  {
    tree: "deml(x, 1)",
    nodes: 1,
    backend: "DEML",
    electronics: "RC discharge: V(t) = V₀·exp(−t/τ)",
    astrophysics: "Newtonian cooling: T(t) = T_env + ΔT·exp(−t/τ)",
    finance: "Bond discount: D(T) = exp(−r·T)",
    physics: "Radioactive decay: N(t) = N₀·exp(−λt)",
  },
  {
    tree: "1 - deml(x, 1)",
    nodes: 2,
    backend: "DEML",
    electronics: "RC charging: V(t) = Vₛ·(1 − exp(−t/τ))",
    astrophysics: "Luminosity rise: L(t) = L_max·(1−exp(−t/τ_rise))",
    finance: "Option time-value accumulation shape",
    physics: "—",
  },
  {
    tree: "deml(x², 1)",
    nodes: 2,
    backend: "DEML",
    electronics: "Gaussian filter: h(t) = exp(−t²/σ²)",
    astrophysics: "Heat kernel: G(x,t) = exp(−x²/4t)",
    finance: "BS density core: exp(−d₁²/2)",
    physics: "—",
  },
  {
    tree: "recip(cosh(x))",
    nodes: 2,
    backend: "BEST",
    electronics: "Waveguide soliton mode profile sech(x)",
    astrophysics: "NLS plasma soliton: A(x) = sech(x)",
    finance: "Vol smile core (approx): ~ sech(log-moneyness)",
    physics: "—",
  },
  {
    tree: "eml(α·ln(t_c−t), 1)",
    nodes: 3,
    backend: "EXL",
    electronics: "—",
    astrophysics: "GW chirp amplitude: A(t) ∝ (t_c−t)^(−1/4)",
    finance: "Heston vol envelope: V(T−t) ~ (T−t)^α",
    physics: "—",
  },
];

const DOMAINS = ["electronics", "astrophysics", "finance", "physics"];

const domainColor = {
  electronics: "#facc15",
  astrophysics: "#60a5fa",
  finance: "#34d399",
  physics: "#f472b6",
};

const domainIcon = {
  electronics: "⚡",
  astrophysics: "🌌",
  finance: "📈",
  physics: "⚛",
};

function TreeBadge({ tree }) {
  const color = TREE_COLOR[tree] || "#94a3b8";
  return (
    <span
      style={{
        background: color + "22",
        border: `1px solid ${color}`,
        color,
        borderRadius: 4,
        padding: "2px 8px",
        fontFamily: "monospace",
        fontSize: 12,
        fontWeight: 600,
      }}
    >
      {tree}
    </span>
  );
}

function DomainColumn({ domain, analogy }) {
  const text = analogy[domain];
  if (!text || text === "—") {
    return (
      <div
        style={{
          padding: "10px 12px",
          color: "#475569",
          fontStyle: "italic",
          fontSize: 13,
        }}
      >
        —
      </div>
    );
  }
  const color = domainColor[domain];
  return (
    <div
      style={{
        padding: "10px 12px",
        borderLeft: `3px solid ${color}`,
        background: color + "11",
        borderRadius: 4,
        fontSize: 13,
        color: "#e2e8f0",
      }}
    >
      <span style={{ color, fontWeight: 700, marginRight: 6 }}>
        {domainIcon[domain]}
      </span>
      {text}
    </div>
  );
}

export default function AnalogRenaissanceTab() {
  const [selected, setSelected] = useState(null);

  return (
    <div style={{ padding: "24px 32px", maxWidth: 1100, margin: "0 auto" }}>
      <h2 style={{ color: "#f1f5f9", marginBottom: 4 }}>
        ⚡ EML Analog Renaissance
      </h2>
      <p style={{ color: "#94a3b8", marginBottom: 24, fontSize: 14 }}>
        The same tiny EML trees recur across electronics, astrophysics, finance,
        and physics — only the physical constants change.
      </p>

      <div style={{ overflowX: "auto" }}>
        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
            fontSize: 13,
            color: "#cbd5e1",
          }}
        >
          <thead>
            <tr style={{ borderBottom: "1px solid #334155" }}>
              <th style={{ textAlign: "left", padding: "8px 10px", color: "#94a3b8" }}>
                Tree Shape
              </th>
              <th style={{ textAlign: "center", padding: "8px 10px", color: "#94a3b8" }}>
                Nodes
              </th>
              <th style={{ textAlign: "center", padding: "8px 10px", color: "#94a3b8" }}>
                Backend
              </th>
              {DOMAINS.map((d) => (
                <th
                  key={d}
                  style={{
                    textAlign: "left",
                    padding: "8px 10px",
                    color: domainColor[d],
                  }}
                >
                  {domainIcon[d]} {d}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {ANALOGIES.map((a, i) => (
              <tr
                key={i}
                style={{
                  borderBottom: "1px solid #1e293b",
                  background:
                    selected === i ? "#1e293b" : i % 2 === 0 ? "#0f172a" : "#0d1526",
                  cursor: "pointer",
                  transition: "background 0.15s",
                }}
                onClick={() => setSelected(selected === i ? null : i)}
              >
                <td style={{ padding: "10px 10px", whiteSpace: "nowrap" }}>
                  <TreeBadge tree={a.tree} />
                </td>
                <td style={{ textAlign: "center", padding: "10px 10px" }}>
                  {a.nodes}
                </td>
                <td style={{ textAlign: "center", padding: "10px 10px", color: "#94a3b8" }}>
                  {a.backend}
                </td>
                {DOMAINS.map((d) => (
                  <td key={d} style={{ padding: "8px 10px" }}>
                    <DomainColumn domain={d} analogy={a} />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div
        style={{
          marginTop: 32,
          padding: "20px 24px",
          background: "#0f172a",
          border: "1px solid #1e3a5f",
          borderRadius: 8,
        }}
      >
        <h3 style={{ color: "#60a5fa", marginBottom: 12, fontSize: 16 }}>
          Key Theorem: Universal Decay
        </h3>
        <p style={{ color: "#94a3b8", fontSize: 13, lineHeight: 1.7 }}>
          <code style={{ color: "#4f9cf9" }}>deml(x, 1) = exp(−x)</code> is the
          universal decay tree. With <code>x = t/τ</code> it describes RC
          discharge. With <code>x = t/τ_cool</code> it describes stellar
          Newtonian cooling. With <code>x = r·T</code> it is the bond discount
          factor. All three live in the same 1-node DEML tree — only the
          physical constant naming differs.
        </p>
        <p
          style={{
            marginTop: 12,
            color: "#64748b",
            fontSize: 12,
            fontStyle: "italic",
          }}
        >
          {ANALOGIES.length} tree shapes · {DOMAINS.length} domains ·
          monogate v1.4.0
        </p>
      </div>
    </div>
  );
}
