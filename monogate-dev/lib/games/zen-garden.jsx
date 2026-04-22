// EML Zen Garden — Flagship 2 for monogate.dev/lab
//
// A living, breathing, interactive complex-plane garden.
// The anti-fractal: smooth, meditative, infinitely tweakable.
//
// Drag floating leaf-nodes around the complex plane. Each node is a
// constant c_i in a linear chain of F16 operators:
//
//   f(z) = op_n ^{d_n}( ... op_1^{d_1}(z, c_1) ... , c_n)
//
// The canvas renders one of three visualizations of f: domain coloring,
// orbit field, or flow field. A continuous drone tracks the tree's output
// at a fixed evaluation point. Audio-reactive mode maps mic/file FFT
// bands onto node parameters — the garden breathes with the music.

import { useState, useRef, useEffect, useCallback } from "react";

// ─── Complex math ────────────────────────────────────────────────────────────

function cExp(r, i) {
  const e = Math.exp(r);
  return [e * Math.cos(i), e * Math.sin(i)];
}

function cLn(r, i) {
  const mag = Math.sqrt(r * r + i * i);
  if (mag < 1e-300) return [-700, 0];
  return [Math.log(mag), Math.atan2(i, r)];
}

const OPS = {
  EML: (zr, zi, cr, ci) => {
    const [er, ei] = cExp(zr, zi);
    const [lr, li] = cLn(cr, ci);
    return [er - lr, ei - li];
  },
  DEML: (zr, zi, cr, ci) => {
    const [er, ei] = cExp(-zr, -zi);
    const [lr, li] = cLn(cr, ci);
    return [er - lr, ei - li];
  },
  EXL: (zr, zi, cr, ci) => {
    const [er, ei] = cExp(zr, zi);
    const [lr, li] = cLn(cr, ci);
    return [er * lr - ei * li, er * li + ei * lr];
  },
  EDL: (zr, zi, cr, ci) => {
    const [er, ei] = cExp(zr, zi);
    const [lr, li] = cLn(cr, ci);
    const d = lr * lr + li * li;
    if (d < 1e-30) return [1e10, 0];
    return [(er * lr + ei * li) / d, (ei * lr - er * li) / d];
  },
  EAL: (zr, zi, cr, ci) => {
    const [er, ei] = cExp(zr, zi);
    const [lr, li] = cLn(cr, ci);
    return [er + lr, ei + li];
  },
  EPL: (zr, zi, cr, ci) => {
    const [lr, li] = cLn(cr, ci);
    const wr = zr * lr - zi * li;
    const wi = zr * li + zi * lr;
    return cExp(wr, wi);
  },
};

const OP_COLORS = {
  EML:  "#4facfe",
  DEML: "#f5576c",
  EXL:  "#0fd38d",
  EDL:  "#fccb52",
  EAL:  "#a18cd1",
  EPL:  "#96e6a1",
};

// Evaluate the tree: apply each node's operator d_i times, starting from z.
function evalTree(tree, zr, zi) {
  let r = zr;
  let i = zi;
  for (const node of tree) {
    const fn = OPS[node.op] || OPS.EML;
    for (let k = 0; k < node.depth; k++) {
      const nr = fn(r, i, node.re, node.im);
      r = nr[0];
      i = nr[1];
      if (!isFinite(r) || !isFinite(i)) return [NaN, NaN];
    }
  }
  return [r, i];
}

// ─── Color helpers ───────────────────────────────────────────────────────────

function hslToRgb(h, s, l) {
  h /= 360; s /= 100; l /= 100;
  let r, g, b;
  if (s === 0) { r = g = b = l; }
  else {
    const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
    const p = 2 * l - q;
    const h2r = (pp, qq, tt) => {
      if (tt < 0) tt += 1;
      if (tt > 1) tt -= 1;
      if (tt < 1 / 6) return pp + (qq - pp) * 6 * tt;
      if (tt < 1 / 2) return qq;
      if (tt < 2 / 3) return pp + (qq - pp) * (2 / 3 - tt) * 6;
      return pp;
    };
    r = h2r(p, q, h + 1 / 3);
    g = h2r(p, q, h);
    b = h2r(p, q, h - 1 / 3);
  }
  return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
}

function domainColor(fr, fi, hueShift) {
  if (!isFinite(fr) || !isFinite(fi)) return [6, 6, 10];
  const mag = Math.sqrt(fr * fr + fi * fi);
  const arg = Math.atan2(fi, fr);
  const h = (((arg * 180) / Math.PI + 180 + hueShift) % 360 + 360) % 360;
  const s = 75;
  const l = 18 + 42 * (1 - 1 / (1 + Math.pow(mag, 0.35)));
  return hslToRgb(h, s, Math.min(80, l));
}

// ─── Nodes + presets ─────────────────────────────────────────────────────────

const DEFAULT_OP = "EML";
const PHI = (1 + Math.sqrt(5)) / 2;

const PRESETS = {
  pure_euler: {
    name: "Pure Euler",
    nodes: [
      { re: 1, im: 0, op: "EML", depth: 1 },
      { re: 0, im: 1, op: "EML", depth: 1 },
      { re: 0, im: 0, op: "EML", depth: 1 },
    ],
    mode: "domain",
  },
  phantom_attractor: {
    name: "Phantom Attractor",
    nodes: [
      { re: 3.17, im: 0, op: "EML", depth: 2 },
      { re: 1,    im: 0, op: "EML", depth: 1 },
    ],
    mode: "domain",
  },
  chaos_lullaby: {
    name: "Chaos Lullaby",
    nodes: [
      { re: -0.7, im: 0.2,  op: "EML",  depth: 2 },
      { re: 0.4,  im: -1.1, op: "DEML", depth: 1 },
      { re: 1.5,  im: 0.5,  op: "EXL",  depth: 1 },
    ],
    mode: "domain",
  },
  golden_spiral: {
    name: "Golden Spiral",
    nodes: [
      { re: PHI,     im: 0,     op: "EXL", depth: 1 },
      { re: 1 / PHI, im: 0,     op: "EML", depth: 2 },
      { re: 0,       im: 1 / PHI, op: "EAL", depth: 1 },
    ],
    mode: "domain",
  },
  breath: {
    name: "Breath",
    nodes: [
      { re: 1, im: 0, op: "EML", depth: 1 },
      { re: 0, im: 1, op: "EAL", depth: 1 },
      { re: 0.5, im: 0.5, op: "EXL", depth: 1 },
    ],
    mode: "domain",
  },
};

// ─── URL hash share/load ────────────────────────────────────────────────────

function encodeState(state) {
  try {
    const json = JSON.stringify(state);
    return typeof window === "undefined"
      ? ""
      : window.btoa(unescape(encodeURIComponent(json)));
  } catch { return ""; }
}

function decodeState(hash) {
  try {
    if (!hash) return null;
    const json = decodeURIComponent(escape(window.atob(hash)));
    const parsed = JSON.parse(json);
    if (!parsed || !Array.isArray(parsed.nodes)) return null;
    return parsed;
  } catch { return null; }
}

// ─── Audio engine ────────────────────────────────────────────────────────────

function createAudio() {
  const Ctx = typeof window === "undefined"
    ? null
    : (window.AudioContext || window.webkitAudioContext);
  if (!Ctx) return null;
  const ctx = new Ctx();
  const master = ctx.createGain();
  master.gain.value = 0.25;
  master.connect(ctx.destination);
  return { ctx, master };
}

// ─── Main component ──────────────────────────────────────────────────────────

const CANVAS_LO = 200;   // while dragging
const CANVAS_HI = 400;   // at rest
const VIEW_R = 2.5;      // complex plane: [-VIEW_R, VIEW_R] on both axes
const RENDER_MODES = ["domain", "orbit", "flow"];

function defaultNodes() {
  return PRESETS.pure_euler.nodes.map((n) => ({ ...n }));
}

export default function ZenGarden() {
  const canvasRef = useRef(null);

  // Core state
  const [nodes, setNodes] = useState(defaultNodes);
  const [renderMode, setRenderMode] = useState("domain");
  const [selectedIdx, setSelectedIdx] = useState(null);  // which node has panel open
  const [dragIdx, setDragIdx] = useState(null);          // which node is being dragged
  const [isDragging, setIsDragging] = useState(false);
  const [preset, setPreset] = useState("pure_euler");
  const [hueShift, setHueShift] = useState(0);
  const [zoom, setZoom] = useState(1);                    // audio-reactive "breath"

  // Audio state
  const [droneOn, setDroneOn] = useState(false);
  const [micOn, setMicOn] = useState(false);
  const [fileUrl, setFileUrl] = useState(null);
  const [audioReactive, setAudioReactive] = useState(false);
  const [masterVol, setMasterVol] = useState(0.25);

  // Refs (audio objects; don't trigger re-render)
  const audioRef = useRef(null);
  const droneRef = useRef(null);          // { osc, gain, panner }
  const analyserRef = useRef(null);
  const micStreamRef = useRef(null);
  const fileSrcRef = useRef(null);
  const fileEltRef = useRef(null);
  const bandsRef = useRef({ bass: 0, mid: 0, treb: 0, rms: 0 });
  const renderPendingRef = useRef(false);
  const nodesRef = useRef(nodes);
  useEffect(() => { nodesRef.current = nodes; }, [nodes]);

  // Derived
  const totalDepth = nodes.reduce((s, n) => s + n.depth, 0);
  const chordCost = nodes.length * 2 + totalDepth;  // soft proxy

  // ── Canvas rendering ─────────────────────────────────────────────────────

  const render = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const size = isDragging ? CANVAS_LO : CANVAS_HI;
    if (canvas.width !== size) {
      canvas.width = size;
      canvas.height = size;
    }
    const ctx = canvas.getContext("2d");
    const tree = nodesRef.current;
    const image = ctx.createImageData(size, size);
    const data = image.data;
    const r = VIEW_R / zoom;

    if (renderMode === "domain") {
      for (let py = 0; py < size; py++) {
        const zi = -r + (py / size) * 2 * r;    // flip y so +Im goes up-screen
        for (let px = 0; px < size; px++) {
          const zr = -r + (px / size) * 2 * r;
          const [fr, fi] = evalTree(tree, zr, zi);
          const [R, G, B] = domainColor(fr, fi, hueShift);
          const idx = (py * size + px) * 4;
          data[idx] = R; data[idx + 1] = G; data[idx + 2] = B; data[idx + 3] = 255;
        }
      }
    } else if (renderMode === "flow") {
      // Dark background, then draw short arrows from z to normalized f(z)
      for (let i = 0; i < data.length; i += 4) {
        data[i] = 8; data[i + 1] = 8; data[i + 2] = 14; data[i + 3] = 255;
      }
      ctx.putImageData(image, 0, 0);
      const step = 16;
      ctx.strokeStyle = "rgba(161,140,209,0.55)";
      ctx.lineWidth = 1;
      for (let py = step / 2; py < size; py += step) {
        for (let px = step / 2; px < size; px += step) {
          const zr = -r + (px / size) * 2 * r;
          const zi = -r + (py / size) * 2 * r;
          const [fr, fi] = evalTree(tree, zr, zi);
          const dx = fr - zr;
          const dy = fi - zi;
          const mag = Math.sqrt(dx * dx + dy * dy) + 1e-9;
          const L = Math.min(step * 0.6, step * 0.6 * Math.log1p(mag) / Math.log1p(mag + 2));
          const ux = (dx / mag) * L;
          const uy = -(dy / mag) * L;  // flip for screen
          ctx.beginPath();
          ctx.moveTo(px, py);
          ctx.lineTo(px + ux, py + uy);
          ctx.stroke();
        }
      }
      return;  // skip the putImageData at the bottom
    } else if (renderMode === "orbit") {
      // Fade background to pitch black, then overlay orbit points
      for (let i = 0; i < data.length; i += 4) {
        data[i] = 4; data[i + 1] = 4; data[i + 2] = 8; data[i + 3] = 255;
      }
      ctx.putImageData(image, 0, 0);
      // Draw orbit tails from a sparse seed grid
      const seedStep = 24;
      const steps = 24;
      ctx.fillStyle = "rgba(96,230,161,0.18)";
      for (let py = seedStep / 2; py < size; py += seedStep) {
        for (let px = seedStep / 2; px < size; px += seedStep) {
          let zr = -r + (px / size) * 2 * r;
          let zi = -r + (py / size) * 2 * r;
          for (let s = 0; s < steps; s++) {
            const [fr, fi] = evalTree(tree, zr, zi);
            if (!isFinite(fr) || !isFinite(fi)) break;
            zr = fr; zi = fi;
            const ox = ((zr + r) / (2 * r)) * size;
            const oy = ((zi + r) / (2 * r)) * size;
            if (ox < 0 || ox >= size || oy < 0 || oy >= size) break;
            ctx.fillRect(ox, oy, 1, 1);
          }
        }
      }
      return;
    }

    ctx.putImageData(image, 0, 0);
  }, [renderMode, hueShift, zoom, isDragging]);

  // Throttled render: one per animation frame.
  useEffect(() => {
    if (renderPendingRef.current) return;
    renderPendingRef.current = true;
    requestAnimationFrame(() => {
      renderPendingRef.current = false;
      render();
    });
  }, [nodes, renderMode, hueShift, zoom, isDragging, render]);

  // ── Coord helpers ────────────────────────────────────────────────────────

  function canvasPxToComplex(px, py, rect) {
    const r = VIEW_R / zoom;
    const zr = -r + (px / rect.width) * 2 * r;
    const zi = -r + (py / rect.height) * 2 * r;
    return [zr, zi];
  }

  function complexToScreenPct(zr, zi) {
    const r = VIEW_R / zoom;
    const x = ((zr + r) / (2 * r)) * 100;
    const y = ((zi + r) / (2 * r)) * 100;
    return { x, y };
  }

  // ── Node dragging ────────────────────────────────────────────────────────

  function handlePointerDownCanvas(e) {
    // Only canvas clicks (not node clicks — those have their own handler)
    // Canvas click on empty space deselects.
    setSelectedIdx(null);
  }

  function beginDrag(idx, e) {
    e.stopPropagation();
    e.preventDefault();
    setDragIdx(idx);
    setIsDragging(true);
    setSelectedIdx(idx);

    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();

    function onMove(ev) {
      const cx = (ev.clientX ?? ev.touches?.[0]?.clientX) - rect.left;
      const cy = (ev.clientY ?? ev.touches?.[0]?.clientY) - rect.top;
      const [re, im] = canvasPxToComplex(cx, cy, rect);
      setNodes((prev) => prev.map((n, i) => (i === idx ? { ...n, re, im } : n)));
    }
    function onUp() {
      setDragIdx(null);
      setIsDragging(false);
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
      window.removeEventListener("touchmove", onMove);
      window.removeEventListener("touchend", onUp);
    }
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
    window.addEventListener("touchmove", onMove, { passive: false });
    window.addEventListener("touchend", onUp);
  }

  function updateNode(idx, patch) {
    setNodes((prev) => prev.map((n, i) => (i === idx ? { ...n, ...patch } : n)));
  }

  function addNode() {
    if (nodes.length >= 6) return;
    setNodes((prev) => [...prev, { re: 0.5, im: 0, op: DEFAULT_OP, depth: 1 }]);
    setSelectedIdx(nodes.length);
  }

  function removeNode(idx) {
    setNodes((prev) => prev.filter((_, i) => i !== idx));
    setSelectedIdx(null);
  }

  // ── Presets ──────────────────────────────────────────────────────────────

  function applyPreset(key) {
    const p = PRESETS[key];
    if (!p) return;
    setPreset(key);
    setNodes(p.nodes.map((n) => ({ ...n })));
    if (p.mode) setRenderMode(p.mode);
    setSelectedIdx(null);
    if (key === "breath") {
      setAudioReactive(true);
      setDroneOn(true);
    }
  }

  // ── Audio: lazy init + drone ─────────────────────────────────────────────

  function ensureAudio() {
    if (audioRef.current) return audioRef.current;
    audioRef.current = createAudio();
    if (audioRef.current) audioRef.current.master.gain.value = masterVol;
    return audioRef.current;
  }

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    const now = audio.ctx.currentTime;
    audio.master.gain.setTargetAtTime(masterVol, now, 0.05);
  }, [masterVol]);

  function startDrone() {
    const audio = ensureAudio();
    if (!audio || droneRef.current) return;
    const osc = audio.ctx.createOscillator();
    const gain = audio.ctx.createGain();
    const panner = audio.ctx.createStereoPanner();
    osc.type = "sine";
    osc.frequency.value = 220;
    gain.gain.value = 0;
    osc.connect(gain).connect(panner).connect(audio.master);
    osc.start();
    // Fade in
    const now = audio.ctx.currentTime;
    gain.gain.linearRampToValueAtTime(0.18, now + 0.25);
    droneRef.current = { osc, gain, panner };
  }

  function stopDrone() {
    const audio = audioRef.current;
    const d = droneRef.current;
    if (!audio || !d) return;
    const now = audio.ctx.currentTime;
    try {
      d.gain.gain.cancelScheduledValues(now);
      d.gain.gain.setValueAtTime(d.gain.gain.value, now);
      d.gain.gain.linearRampToValueAtTime(0, now + 0.2);
      d.osc.stop(now + 0.25);
    } catch { /* already stopped */ }
    droneRef.current = null;
  }

  useEffect(() => {
    if (droneOn) startDrone();
    else stopDrone();
    return () => { if (!droneOn) stopDrone(); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [droneOn]);

  // Update drone from tree output at z = 1 + 0i
  useEffect(() => {
    const audio = audioRef.current;
    const d = droneRef.current;
    if (!audio || !d) return;
    const [fr, fi] = evalTree(nodes, 1, 0);
    const mag = Math.sqrt((fr || 0) ** 2 + (fi || 0) ** 2);
    // Pitch 100–1000 Hz from |Re(f)|
    const freq = isFinite(fr) ? 100 + Math.min(Math.abs(fr), 10) * 90 : 220;
    // Pan from Im(f)
    const pan = isFinite(fi) ? Math.tanh((fi || 0) * 0.6) : 0;
    // Volume from |f|, compressed
    const vol = isFinite(mag) ? 0.12 + 0.18 / (1 + Math.exp(-mag + 1)) : 0.1;
    const now = audio.ctx.currentTime;
    d.osc.frequency.setTargetAtTime(freq, now, 0.05);
    d.panner.pan.setTargetAtTime(pan, now, 0.05);
    d.gain.gain.setTargetAtTime(vol, now, 0.05);
  }, [nodes]);

  // ── Audio-reactive: mic or file → FFT bands → node params ────────────────

  async function toggleMic() {
    if (micOn) {
      if (micStreamRef.current) {
        micStreamRef.current.getTracks().forEach((t) => t.stop());
        micStreamRef.current = null;
      }
      analyserRef.current = null;
      setMicOn(false);
      return;
    }
    const audio = ensureAudio();
    if (!audio) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      micStreamRef.current = stream;
      const src = audio.ctx.createMediaStreamSource(stream);
      const an = audio.ctx.createAnalyser();
      an.fftSize = 1024;
      an.smoothingTimeConstant = 0.6;
      src.connect(an);
      analyserRef.current = an;
      setMicOn(true);
      setAudioReactive(true);
    } catch (err) {
      // Permission denied or unsupported — silently bail out
      setMicOn(false);
    }
  }

  function loadFile(file) {
    const audio = ensureAudio();
    if (!audio || !file) return;
    const url = URL.createObjectURL(file);
    setFileUrl(url);
    const el = new Audio(url);
    el.crossOrigin = "anonymous";
    el.loop = true;
    el.play().catch(() => { /* autoplay blocked */ });
    fileEltRef.current = el;

    try {
      const src = audio.ctx.createMediaElementSource(el);
      const an = audio.ctx.createAnalyser();
      an.fftSize = 1024;
      an.smoothingTimeConstant = 0.6;
      src.connect(an);
      // Also route to output so the user hears the track
      src.connect(audio.master);
      analyserRef.current = an;
      fileSrcRef.current = src;
      setAudioReactive(true);
    } catch {
      /* ignore */
    }
  }

  function stopFile() {
    const el = fileEltRef.current;
    if (el) {
      el.pause();
      el.src = "";
    }
    fileEltRef.current = null;
    fileSrcRef.current = null;
    if (fileUrl) URL.revokeObjectURL(fileUrl);
    setFileUrl(null);
    if (!micOn) analyserRef.current = null;
  }

  // Audio-reactive frame loop: read FFT bands, drive node params.
  useEffect(() => {
    if (!audioReactive || !analyserRef.current) return;
    const an = analyserRef.current;
    const bins = new Uint8Array(an.frequencyBinCount);
    let rafId = 0;

    function frame() {
      an.getByteFrequencyData(bins);
      // Assume sampleRate/2 across bins. For 44.1kHz, half is 22050 Hz.
      const sr = audioRef.current?.ctx.sampleRate || 44100;
      const hzPerBin = (sr / 2) / bins.length;
      let bass = 0, mid = 0, treb = 0, rms = 0;
      let bassCount = 0, midCount = 0, trebCount = 0;
      for (let i = 0; i < bins.length; i++) {
        const hz = i * hzPerBin;
        const v = bins[i] / 255;
        rms += v * v;
        if (hz >= 20 && hz < 200) { bass += v; bassCount++; }
        else if (hz >= 200 && hz < 2000) { mid += v; midCount++; }
        else if (hz >= 2000 && hz < 8000) { treb += v; trebCount++; }
      }
      if (bassCount) bass /= bassCount;
      if (midCount)  mid  /= midCount;
      if (trebCount) treb /= trebCount;
      rms = Math.sqrt(rms / bins.length);

      // Exponential smoothing
      const prev = bandsRef.current;
      const smooth = (p, c) => p * 0.82 + c * 0.18;
      const next = {
        bass: smooth(prev.bass, bass),
        mid:  smooth(prev.mid,  mid),
        treb: smooth(prev.treb, treb),
        rms:  smooth(prev.rms,  rms),
      };
      bandsRef.current = next;

      // Map bands onto node parameters + visual controls
      setNodes((prevNodes) => {
        if (prevNodes.length === 0) return prevNodes;
        const out = prevNodes.map((n) => ({ ...n }));
        if (out[0]) out[0] = { ...out[0], im: (next.bass * 2 - 1) * 2 };
        if (out[1]) out[1] = { ...out[1], re: (next.mid * 2 - 1) * 2 };
        return out;
      });
      setHueShift(next.treb * 360);
      setZoom(1 + next.rms * 0.8);

      rafId = requestAnimationFrame(frame);
    }
    rafId = requestAnimationFrame(frame);
    return () => cancelAnimationFrame(rafId);
  }, [audioReactive, micOn, fileUrl]);

  // Clean up all audio on unmount
  useEffect(() => () => {
    stopDrone();
    if (micStreamRef.current) micStreamRef.current.getTracks().forEach((t) => t.stop());
    if (fileEltRef.current) {
      fileEltRef.current.pause();
      fileEltRef.current.src = "";
    }
    if (fileUrl) URL.revokeObjectURL(fileUrl);
    const audio = audioRef.current;
    if (audio) { try { audio.ctx.close(); } catch { /* ignore */ } }
  }, []);  // eslint-disable-line react-hooks/exhaustive-deps

  // ── URL hash sync ────────────────────────────────────────────────────────

  // Load from URL on mount
  useEffect(() => {
    if (typeof window === "undefined") return;
    const hash = window.location.hash.replace(/^#/, "");
    if (!hash.startsWith("garden=")) return;
    const parsed = decodeState(hash.slice("garden=".length));
    if (parsed) {
      if (Array.isArray(parsed.nodes)) setNodes(parsed.nodes);
      if (parsed.mode) setRenderMode(parsed.mode);
    }
  }, []);

  function exportShareLink() {
    const state = { nodes, mode: renderMode };
    const enc = encodeState(state);
    if (!enc || typeof window === "undefined") return;
    const url = `${window.location.origin}${window.location.pathname}#garden=${enc}`;
    window.history.replaceState(null, "", `#garden=${enc}`);
    if (navigator.clipboard) {
      navigator.clipboard.writeText(url).catch(() => { /* noop */ });
    }
    return url;
  }

  function exportTreeJson() {
    const blob = new Blob([JSON.stringify({ nodes, mode: renderMode }, null, 2)],
                         { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "zen-garden-tree.json";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  // ── UI ───────────────────────────────────────────────────────────────────

  const selected = selectedIdx != null ? nodes[selectedIdx] : null;

  return (
    <div style={S.root}>
      <header style={S.header}>
        <span style={S.brand}>monogate</span>
        <span style={S.subBrand}>zen garden</span>
        <span style={S.formula}>
          {nodes.length} node{nodes.length === 1 ? "" : "s"} · depth {totalDepth} · cost ~{chordCost}n · {renderMode}
        </span>
      </header>

      <div style={S.topBar}>
        {RENDER_MODES.map((m) => (
          <button
            key={m}
            onClick={() => setRenderMode(m)}
            style={{
              ...S.modeBtn,
              background: renderMode === m ? "rgba(255,255,255,0.12)" : "transparent",
              color: renderMode === m ? "#e8e8f0" : "rgba(255,255,255,0.35)",
              borderColor: renderMode === m ? "rgba(255,255,255,0.25)" : "rgba(255,255,255,0.06)",
            }}
          >
            {m === "domain" ? "domain color" : m === "orbit" ? "orbit field" : "flow field"}
          </button>
        ))}

        <div style={S.divider} />

        <select
          value={preset}
          onChange={(e) => applyPreset(e.target.value)}
          style={S.select}
        >
          {Object.entries(PRESETS).map(([k, v]) => (
            <option key={k} value={k}>{v.name}</option>
          ))}
        </select>

        <div style={{ flex: 1 }} />

        <button onClick={exportShareLink} style={S.btn}>share link</button>
        <button onClick={exportTreeJson}  style={S.btn}>export json</button>
      </div>

      <div style={S.mainWrap}>
        <div style={S.canvasWrap} onMouseDown={handlePointerDownCanvas}>
          <canvas
            ref={canvasRef}
            width={CANVAS_HI}
            height={CANVAS_HI}
            style={{
              width: "100%",
              height: "100%",
              display: "block",
              imageRendering: isDragging ? "pixelated" : "auto",
            }}
          />

          {/* Draggable node markers */}
          {nodes.map((n, i) => {
            const pct = complexToScreenPct(n.re, n.im);
            const visible = pct.x >= -6 && pct.x <= 106 && pct.y >= -6 && pct.y <= 106;
            if (!visible) return null;
            const color = OP_COLORS[n.op] || "#ffffff";
            const isSelected = selectedIdx === i;
            return (
              <div
                key={i}
                onMouseDown={(e) => beginDrag(i, e)}
                onTouchStart={(e) => beginDrag(i, e)}
                onClick={(e) => { e.stopPropagation(); setSelectedIdx(i); }}
                style={{
                  position: "absolute",
                  left: `${pct.x}%`,
                  top:  `${pct.y}%`,
                  width: 16, height: 16,
                  transform: "translate(-50%, -50%)",
                  borderRadius: "50%",
                  border: `2px solid ${color}`,
                  background: isSelected ? color : "rgba(10,10,20,0.65)",
                  boxShadow: `0 0 10px ${color}88`,
                  cursor: dragIdx === i ? "grabbing" : "grab",
                  touchAction: "none",
                }}
              />
            );
          })}
        </div>

        {/* Node panel */}
        <aside style={S.panel}>
          <div style={S.panelHeader}>
            <span style={S.panelTitle}>nodes</span>
            <button
              onClick={addNode}
              disabled={nodes.length >= 6}
              style={{ ...S.btn, opacity: nodes.length >= 6 ? 0.3 : 1 }}
            >
              + add
            </button>
          </div>

          {nodes.map((n, i) => {
            const isSel = selectedIdx === i;
            const color = OP_COLORS[n.op] || "#fff";
            return (
              <div
                key={i}
                onClick={() => setSelectedIdx(i)}
                style={{
                  ...S.nodeRow,
                  borderColor: isSel ? color : "rgba(255,255,255,0.08)",
                  background: isSel ? "rgba(255,255,255,0.04)" : "transparent",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span style={{ ...S.dot, background: color }} />
                  <span style={{ fontSize: 11, color: "rgba(255,255,255,0.7)" }}>node {i}</span>
                  <button
                    onClick={(e) => { e.stopPropagation(); removeNode(i); }}
                    style={S.xBtn}
                  >×</button>
                </div>

                {isSel && (
                  <div style={S.nodeFields}>
                    <div style={S.field}>
                      <label style={S.lbl}>re {n.re.toFixed(2)}</label>
                      <input
                        type="range" min={-5} max={5} step={0.01}
                        value={n.re}
                        onChange={(e) => updateNode(i, { re: parseFloat(e.target.value) })}
                        style={S.slider}
                      />
                    </div>
                    <div style={S.field}>
                      <label style={S.lbl}>im {n.im.toFixed(2)}</label>
                      <input
                        type="range" min={-5} max={5} step={0.01}
                        value={n.im}
                        onChange={(e) => updateNode(i, { im: parseFloat(e.target.value) })}
                        style={S.slider}
                      />
                    </div>
                    <div style={S.field}>
                      <label style={S.lbl}>op</label>
                      <select
                        value={n.op}
                        onChange={(e) => updateNode(i, { op: e.target.value })}
                        style={S.select}
                      >
                        {Object.keys(OPS).map((k) => <option key={k} value={k}>{k}</option>)}
                      </select>
                    </div>
                    <div style={S.field}>
                      <label style={S.lbl}>depth {n.depth}</label>
                      <input
                        type="range" min={1} max={4} step={1}
                        value={n.depth}
                        onChange={(e) => updateNode(i, { depth: parseInt(e.target.value, 10) })}
                        style={S.slider}
                      />
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </aside>
      </div>

      <div style={S.bottomBar}>
        <button
          onClick={() => setDroneOn((d) => !d)}
          style={{
            ...S.btn,
            background: droneOn ? "#a18cd1" : "transparent",
            color: droneOn ? "#08080c" : "#a18cd1",
            borderColor: "#a18cd1",
            fontWeight: 600,
          }}
        >
          {droneOn ? "■ drone" : "▶ drone"}
        </button>

        <button
          onClick={toggleMic}
          style={{
            ...S.btn,
            background: micOn ? "#f5576c" : "transparent",
            color: micOn ? "#08080c" : "#f5576c",
            borderColor: "#f5576c",
          }}
        >
          {micOn ? "🎤 stop" : "🎤 mic"}
        </button>

        <label style={{ ...S.btn, cursor: "pointer", display: "inline-block" }}>
          {fileUrl ? "♪ loaded" : "♪ load file"}
          <input
            type="file"
            accept="audio/*"
            style={{ display: "none" }}
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) loadFile(f);
            }}
          />
        </label>
        {fileUrl && <button onClick={stopFile} style={S.btn}>stop file</button>}

        <button
          onClick={() => setAudioReactive((a) => !a)}
          disabled={!micOn && !fileUrl}
          style={{
            ...S.btn,
            background: audioReactive ? "rgba(255,255,255,0.12)" : "transparent",
            color: audioReactive ? "#e8e8f0" : "rgba(255,255,255,0.35)",
            opacity: (!micOn && !fileUrl) ? 0.35 : 1,
          }}
        >
          reactive {audioReactive ? "on" : "off"}
        </button>

        <div style={S.divider} />
        <span style={S.label}>♪ vol</span>
        <input
          type="range" min={0} max={1} step={0.01}
          value={masterVol}
          onChange={(e) => setMasterVol(parseFloat(e.target.value))}
          style={S.slider}
        />

        <div style={{ flex: 1 }} />
        <span style={S.hint}>drag nodes · tap for sliders · share creates a link</span>
      </div>
    </div>
  );
}

// ─── Inline styles ───────────────────────────────────────────────────────────

const FONT = "'IBM Plex Mono', 'SF Mono', 'Fira Code', monospace";

const S = {
  root: {
    background: "#08080c", color: "#e8e8f0", fontFamily: FONT,
    minHeight: "100vh", display: "flex", flexDirection: "column",
  },
  header: {
    padding: "20px 24px 12px", display: "flex", alignItems: "baseline",
    gap: 16, flexWrap: "wrap", borderBottom: "1px solid rgba(255,255,255,0.06)",
  },
  brand: {
    fontSize: 13, fontWeight: 600, letterSpacing: "0.15em",
    textTransform: "uppercase", color: "#a18cd1", opacity: 0.9,
  },
  subBrand: { fontSize: 13, color: "rgba(255,255,255,0.3)" },
  formula: { fontSize: 11, color: "rgba(255,255,255,0.15)", marginLeft: "auto" },

  topBar: {
    display: "flex", gap: 6, padding: "12px 24px",
    flexWrap: "wrap", alignItems: "center",
  },
  modeBtn: {
    borderRadius: 4, padding: "5px 12px", fontSize: 11, fontFamily: FONT,
    cursor: "pointer", border: "1px solid", textTransform: "capitalize",
  },
  divider: { width: 1, height: 20, background: "rgba(255,255,255,0.08)", margin: "0 4px" },

  select: {
    background: "rgba(255,255,255,0.04)", color: "rgba(255,255,255,0.85)",
    border: "1px solid rgba(255,255,255,0.08)", borderRadius: 4,
    padding: "5px 10px", fontSize: 11, fontFamily: FONT, cursor: "pointer",
  },

  mainWrap: {
    flex: 1, display: "flex", gap: 12, padding: "0 24px 12px",
    alignItems: "stretch", flexWrap: "wrap",
  },
  canvasWrap: {
    flex: "1 1 420px",
    minWidth: 280,
    maxWidth: 520,
    aspectRatio: "1 / 1",
    position: "relative",
    borderRadius: 6, overflow: "hidden",
    border: "1px solid rgba(255,255,255,0.06)",
    background: "#04040a",
  },
  panel: {
    flex: "1 1 220px",
    minWidth: 220,
    maxWidth: 320,
    padding: "0 0 4px",
    display: "flex", flexDirection: "column", gap: 6,
  },
  panelHeader: {
    display: "flex", alignItems: "center", justifyContent: "space-between",
    padding: "4px 0 2px",
  },
  panelTitle: {
    fontSize: 10, color: "rgba(255,255,255,0.4)",
    letterSpacing: "0.1em", textTransform: "uppercase",
  },

  nodeRow: {
    border: "1px solid",
    borderRadius: 5,
    padding: "8px 10px",
    cursor: "pointer",
    transition: "background 0.15s, border-color 0.15s",
  },
  nodeFields: { marginTop: 8, display: "flex", flexDirection: "column", gap: 6 },
  field: { display: "flex", alignItems: "center", gap: 8 },
  lbl: { fontSize: 10, color: "rgba(255,255,255,0.4)", width: 58 },
  slider: { flex: 1, accentColor: "#a18cd1" },
  dot: { width: 8, height: 8, borderRadius: "50%" },
  xBtn: {
    marginLeft: "auto",
    background: "transparent", border: "1px solid rgba(255,255,255,0.08)",
    color: "rgba(255,255,255,0.4)", borderRadius: 3,
    width: 20, height: 20, fontSize: 14, lineHeight: "18px",
    cursor: "pointer", fontFamily: FONT,
  },

  bottomBar: {
    padding: "8px 24px 16px", display: "flex", gap: 8,
    alignItems: "center", flexWrap: "wrap",
  },
  btn: {
    background: "transparent", color: "rgba(255,255,255,0.55)",
    border: "1px solid rgba(255,255,255,0.08)", borderRadius: 4,
    padding: "4px 12px", fontSize: 11, fontFamily: FONT, cursor: "pointer",
  },
  label: { fontSize: 11, color: "rgba(255,255,255,0.3)", marginRight: 4 },
  hint: { fontSize: 10, color: "rgba(255,255,255,0.15)", letterSpacing: "0.1em" },
};
