import { useEffect, useMemo, useRef, useState } from "react";

const C = {
  bg: "#07080f",
  surface: "#0d0e1c",
  border: "#191b2e",
  text: "#cdd0e0",
  muted: "#6f738a",
  accent: "#e8a020",
  blue: "#6ab0f5",
  green: "#5ec47a",
  warn: "#f59e0b",
};

const PRESETS = {
  identity: {
    label: "f(z) = z",
    description: "Baseline phase wheel: color follows the input angle and magnitude contours expand evenly.",
    symmetry: "Rotation of the input rotates the output by the same angle.",
    fn: (z) => z,
  },
  square: {
    label: "f(z) = z²",
    description: "The phase wraps twice and magnitude contours pack faster because |z²| = |z|².",
    symmetry: "A half-turn in the input completes a full color cycle in the output.",
    fn: (z) => cmul(z, z),
  },
  exp: {
    label: "f(z) = exp(z)",
    description: "Imaginary shifts become phase rotations; vertical stripes reveal periodicity.",
    symmetry: "exp(z + 2πi) = exp(z).",
    fn: cexp,
  },
  log: {
    label: "f(z) = ln(z)",
    description: "The principal branch exposes the cut along the negative real axis.",
    symmetry: "Angle becomes imaginary output; branch choice is visible.",
    fn: clog,
  },
  eml_exp: {
    label: "f(z) = eml(z, 1)",
    description: "The one-operator exp route: eml(z, 1) = exp(z) - ln(1).",
    symmetry: "Same periodic phase behavior as exp(z), shown through EML form.",
    fn: (z) => csub(cexp(z), clog({ re: 1, im: 0 })),
  },
  eml_slice: {
    label: "f(z) = eml(z, z + 2)",
    description: "Two-input EML slice: exp(z) - ln(z + 2). The shifted log branch creates a visible defect.",
    symmetry: "Not globally invariant; useful for seeing where EML composition introduces structure.",
    fn: (z) => csub(cexp(z), clog({ re: z.re + 2, im: z.im })),
  },
};

function cmul(a, b) {
  return { re: a.re * b.re - a.im * b.im, im: a.re * b.im + a.im * b.re };
}

function csub(a, b) {
  return { re: a.re - b.re, im: a.im - b.im };
}

function cexp(z) {
  const e = Math.exp(z.re);
  return { re: e * Math.cos(z.im), im: e * Math.sin(z.im) };
}

function clog(z) {
  return { re: Math.log(Math.hypot(z.re, z.im)), im: Math.atan2(z.im, z.re) };
}

function hsvToRgb(h, s, v) {
  const i = Math.floor(h * 6);
  const f = h * 6 - i;
  const p = v * (1 - s);
  const q = v * (1 - f * s);
  const t = v * (1 - (1 - f) * s);
  const mod = i % 6;
  const [r, g, b] =
    mod === 0 ? [v, t, p] :
    mod === 1 ? [q, v, p] :
    mod === 2 ? [p, v, t] :
    mod === 3 ? [p, q, v] :
    mod === 4 ? [t, p, v] :
                [v, p, q];
  return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
}

function colorForValue(value, contours) {
  if (!Number.isFinite(value.re) || !Number.isFinite(value.im)) return [10, 12, 20];
  const phase = Math.atan2(value.im, value.re);
  const hue = (phase + Math.PI) / (2 * Math.PI);
  const mag = Math.hypot(value.re, value.im);
  const logMag = Math.log1p(mag);
  let brightness = 0.58 + 0.32 * Math.tanh(logMag / 2.8);
  if (contours) {
    const contour = Math.abs(Math.sin(logMag * 10));
    if (contour < 0.11) brightness = 0.96;
  }
  return hsvToRgb(hue, 0.86, brightness);
}

function drawField(canvas, preset, options) {
  const ctx = canvas.getContext("2d");
  const width = canvas.width;
  const height = canvas.height;
  const image = ctx.createImageData(width, height);
  const scale = options.scale;
  const fn = PRESETS[preset].fn;

  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const re = ((x / (width - 1)) * 2 - 1) * scale;
      const im = (1 - (y / (height - 1)) * 2) * scale;
      const value = fn({ re, im });
      const [r, g, b] = colorForValue(value, options.contours);
      const idx = (y * width + x) * 4;

      let rr = r;
      let gg = g;
      let bb = b;
      const axis = Math.abs(re) < scale / width || Math.abs(im) < scale / height;
      const unit = Math.abs(Math.hypot(re, im) - 1) < scale / 90;
      const branch = preset === "log" && im > -scale / 100 && im < scale / 100 && re < 0;
      const expPeriod = (preset === "exp" || preset === "eml_exp") && Math.abs(Math.sin(im)) < 0.018;

      if (options.overlay && unit) {
        rr = 250; gg = 250; bb = 245;
      }
      if (options.overlay && expPeriod) {
        rr = 255; gg = 255; bb = 255;
      }
      if (options.overlay && branch) {
        rr = 20; gg = 20; bb = 20;
      }
      if (axis) {
        rr = Math.min(255, rr + 22);
        gg = Math.min(255, gg + 22);
        bb = Math.min(255, bb + 22);
      }
      image.data[idx] = rr;
      image.data[idx + 1] = gg;
      image.data[idx + 2] = bb;
      image.data[idx + 3] = 255;
    }
  }
  ctx.putImageData(image, 0, 0);
}

function FieldCanvas({ preset, scale, contours, overlay }) {
  const ref = useRef(null);

  useEffect(() => {
    if (!ref.current) return;
    drawField(ref.current, preset, { scale, contours, overlay });
  }, [preset, scale, contours, overlay]);

  return (
    <canvas
      ref={ref}
      width={420}
      height={420}
      style={{
        width: "100%",
        maxWidth: 520,
        aspectRatio: "1 / 1",
        borderRadius: 8,
        border: `1px solid ${C.border}`,
        background: C.bg,
        imageRendering: "pixelated",
      }}
      aria-label={`Domain coloring plot for ${PRESETS[preset].label}`}
    />
  );
}

function Chip({ children, active, onClick }) {
  return (
    <button
      onClick={onClick}
      style={{
        border: `1px solid ${active ? C.accent : C.border}`,
        background: active ? "rgba(232,160,32,0.11)" : C.surface,
        color: active ? C.accent : C.muted,
        borderRadius: 999,
        padding: "5px 10px",
        fontSize: 10,
      }}
    >
      {children}
    </button>
  );
}

export default function ComplexFieldTab() {
  const [preset, setPreset] = useState("eml_exp");
  const [scale, setScale] = useState(3);
  const [contours, setContours] = useState(true);
  const [overlay, setOverlay] = useState(true);
  const current = PRESETS[preset];
  const presetRows = useMemo(() => Object.entries(PRESETS), []);

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
          <div>
            <div style={{ fontSize: 14, fontWeight: 700, color: C.accent, marginBottom: 6 }}>
              Complex Field
            </div>
            <div style={{ fontSize: 11, color: C.muted, lineHeight: 1.8, maxWidth: 720 }}>
              Domain coloring for complex EML-adjacent functions. Color is phase, contour bands show magnitude,
              and overlays mark simple symmetry cues.
            </div>
          </div>
          <span style={{ alignSelf: "flex-start", color: C.warn, border: `1px solid ${C.border}`, borderRadius: 999, padding: "4px 9px", fontSize: 10 }}>
            VISUAL PROTOTYPE
          </span>
        </div>
      </div>

      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))",
        gap: 10,
        marginBottom: 14,
      }}>
        <a href="?tab=ir" style={{
          background: C.surface,
          border: `1px solid ${C.border}`,
          borderRadius: 8,
          padding: 12,
          color: C.text,
          textDecoration: "none",
        }}>
          <div style={{ color: C.accent, fontSize: 11, fontWeight: 700, marginBottom: 5 }}>
            Field {"->"} IR bridge
          </div>
          <div style={{ color: C.muted, fontSize: 10, lineHeight: 1.7 }}>
            Open the IR beta view to inspect how expressions become shared nodes, guarded replay frames,
            and lowering sketches.
          </div>
        </a>
        <div style={{
          background: C.surface,
          border: `1px solid ${C.border}`,
          borderRadius: 8,
          padding: 12,
          color: C.muted,
          fontSize: 10,
          lineHeight: 1.7,
        }}>
          Color tracks complex phase. Contours track magnitude. Overlays mark simple axes, unit-circle,
          periodic, and branch-cut cues where relevant.
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "minmax(260px, 1fr) minmax(250px, 330px)", gap: 14, alignItems: "start" }}>
        <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8, padding: 14 }}>
          <FieldCanvas preset={preset} scale={scale} contours={contours} overlay={overlay} />
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8, padding: 14 }}>
            <div style={{ fontSize: 11, color: C.text, fontWeight: 700, marginBottom: 10 }}>Function</div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 7 }}>
              {presetRows.map(([key, item]) => (
                <Chip key={key} active={preset === key} onClick={() => setPreset(key)}>
                  {item.label}
                </Chip>
              ))}
            </div>
          </div>

          <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8, padding: 14 }}>
            <div style={{ color: C.accent, fontSize: 13, fontWeight: 700, marginBottom: 8 }}>{current.label}</div>
            <p style={{ color: C.text, fontSize: 11, lineHeight: 1.7, margin: "0 0 8px" }}>{current.description}</p>
            <p style={{ color: C.muted, fontSize: 10, lineHeight: 1.7, margin: 0 }}>{current.symmetry}</p>
          </div>

          <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8, padding: 14 }}>
            <div style={{ fontSize: 11, color: C.text, fontWeight: 700, marginBottom: 10 }}>Controls</div>
            <label style={{ display: "block", color: C.muted, fontSize: 10, marginBottom: 8 }}>
              Scale: ±{scale.toFixed(1)}
              <input
                type="range"
                min="1.4"
                max="5"
                step="0.1"
                value={scale}
                onChange={(e) => setScale(Number(e.target.value))}
                style={{ width: "100%", marginTop: 8 }}
              />
            </label>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              <Chip active={contours} onClick={() => setContours((v) => !v)}>magnitude contours</Chip>
              <Chip active={overlay} onClick={() => setOverlay((v) => !v)}>symmetry overlays</Chip>
            </div>
          </div>

          <div style={{ background: "rgba(245,158,11,0.06)", border: "1px solid rgba(245,158,11,0.32)", borderRadius: 8, padding: 12 }}>
            <div style={{ color: C.warn, fontSize: 10, fontWeight: 700, marginBottom: 5 }}>Boundary</div>
            <div style={{ color: C.muted, fontSize: 10, lineHeight: 1.7 }}>
              Modular-form visuals inspired this grammar, but this tab does not claim modular discriminant
              implementation, physics validation, or proof results. It is a local EML visualization prototype.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
