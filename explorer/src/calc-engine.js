// calc-engine.js — safe recursive descent parser for BEST Calc
// No eval(), no new Function(), no with() — pure JS parser.

import { sin_best, cos_best } from "./eml.js";

// ── Error type ──────────────────────────────────────────────────────────────────
export class ParseError extends Error {}

// ── 8-term Taylor sin/cos for EML mode (matches sin_best term count) ───────────
function sin_eml_taylor(x) {
  // sin = x - x³/6 + x⁵/120 - … (8 terms)
  let sum = 0, xpow = x, fact = 1;
  for (let k = 0; k < 8; k++) {
    sum += (k % 2 === 0 ? 1 : -1) * xpow / fact;
    xpow *= x * x;
    fact *= (2 * k + 2) * (2 * k + 3);
  }
  return sum;
}

function cos_eml_taylor(x) {
  // cos = 1 - x²/2 + x⁴/24 - … (8 terms)
  let sum = 0, xpow = 1, fact = 1;
  for (let k = 0; k < 8; k++) {
    sum += (k % 2 === 0 ? 1 : -1) * xpow / fact;
    xpow *= x * x;
    fact *= (2 * k + 1) * (2 * k + 2);
  }
  return sum;
}

// ── Node costs and operator labels per mode ────────────────────────────────────
// SuperBEST FINAL (2026-04-20): neg=2n, mul=3n, sub=3n, add=3n
export const NODE_COSTS = {
  best: { sin:63, cos:63, exp:1, ln:1, pow:3, mul:3, div:1, add:3, sub:3, neg:2, sqrt:3, abs:6 },
  eml:  { sin:245, cos:245, exp:1, ln:3, pow:15, mul:13, div:15, add:11, sub:5, neg:6, sqrt:15, abs:9 },
  exl:  { ln:1, pow:3, sqrt:3 },
  edl:  { div:1, mul:3, neg:2 },
};

export const OP_SOURCE_BEST = {
  sin:"EXL", cos:"EXL", exp:"EML", ln:"EXL", pow:"EXL",
  mul:"EXL", div:"EDL", add:"EAL", sub:"EML", neg:"EXL", sqrt:"EXL", abs:"EXL",
};

function getOpLabel(name, mode) {
  if (mode === "eml") return "EML";
  if (mode === "exl") return "EXL";
  if (mode === "edl") return "EDL";
  return OP_SOURCE_BEST[name] || "EML";
}

function nodeCost(name, mode) {
  const c = NODE_COSTS[mode]?.[name];
  if (c === undefined) {
    const modeUp = mode.toUpperCase();
    throw new ParseError(`'${name}' not supported in ${modeUp} mode`);
  }
  return c;
}

// ── Tokenizer ──────────────────────────────────────────────────────────────────
function tokenize(src) {
  const tokens = [];
  let i = 0;
  while (i < src.length) {
    if (/\s/.test(src[i])) { i++; continue; }
    if (/\d/.test(src[i]) || (src[i] === "." && /\d/.test(src[i + 1] ?? ""))) {
      let j = i;
      while (j < src.length && /[\d.]/.test(src[j])) j++;
      tokens.push({ t: "num", v: parseFloat(src.slice(i, j)) });
      i = j;
    } else if (/[a-zA-Z_]/.test(src[i])) {
      let j = i;
      while (j < src.length && /[\w]/.test(src[j])) j++;
      tokens.push({ t: "id", v: src.slice(i, j) });
      i = j;
    } else if ("+-*/^(),".includes(src[i])) {
      tokens.push({ t: "op", v: src[i] });
      i++;
    } else {
      throw new ParseError(`Unexpected character: '${src[i]}'`);
    }
  }
  return tokens;
}

// ── Recursive descent parser ───────────────────────────────────────────────────
const ALLOWED_FNS = new Set(["sin","cos","ln","exp","pow","sqrt","abs","tan"]);

function parse(tokens) {
  let pos = 0;

  function peek()    { return tokens[pos]; }
  function at(type, val) { const t = peek(); return t?.t === type && (val === undefined || t.v === val); }
  function eat(type, val) {
    if (!at(type, val)) {
      const t = peek();
      throw new ParseError(`Expected '${val ?? type}', got '${t?.v ?? "end of input"}'`);
    }
    return tokens[pos++];
  }

  function parseExpr() {
    let node = parseTerm();
    while (at("op", "+") || at("op", "-")) {
      const op = tokens[pos++].v;
      node = { type: op === "+" ? "add" : "sub", left: node, right: parseTerm() };
    }
    return node;
  }

  function parseTerm() {
    let node = parseFactor();
    while (at("op", "*") || at("op", "/")) {
      const op = tokens[pos++].v;
      node = { type: op === "*" ? "mul" : "div", left: node, right: parseFactor() };
    }
    return node;
  }

  function parseFactor() {
    const base = parseBase();
    if (at("op", "^")) { pos++; return { type: "pow", left: base, right: parseFactor() }; }
    return base;
  }

  function parseBase() {
    const t = peek();
    if (!t) throw new ParseError("Unexpected end of input");

    if (at("op", "-")) { pos++; return { type: "neg", arg: parseBase() }; }
    if (at("op", "+")) { pos++; return parseBase(); }

    if (at("op", "(")) {
      pos++;
      const e = parseExpr();
      eat("op", ")");
      return e;
    }

    if (t.t === "num") { pos++; return { type: "num", v: t.v }; }

    if (t.t === "id") {
      pos++;
      const name = t.v;
      if (name === "x")  return { type: "var" };
      if (name === "pi") return { type: "num", v: Math.PI };
      if (name === "e" && !at("op", "(")) return { type: "num", v: Math.E };

      if (at("op", "(")) {
        pos++;
        if (!ALLOWED_FNS.has(name)) throw new ParseError(`Unknown function: '${name}'`);
        const arg1 = parseExpr();
        let arg2 = null;
        if (at("op", ",")) { pos++; arg2 = parseExpr(); }
        eat("op", ")");
        if (name === "pow" && !arg2) throw new ParseError("pow() requires two arguments: pow(base, exponent)");
        return { type: "call", fn: name, arg1, arg2 };
      }

      throw new ParseError(`Unknown identifier: '${name}'`);
    }

    throw new ParseError(`Unexpected token: '${t.v}'`);
  }

  const ast = parseExpr();
  if (pos < tokens.length) throw new ParseError(`Unexpected token: '${tokens[pos].v}'`);
  return ast;
}

// ── AST evaluation with node tracking ─────────────────────────────────────────
function evalNode(node, xVal, mode, log) {
  switch (node.type) {
    case "num": return node.v;
    case "var": return xVal;

    case "neg": {
      const v = evalNode(node.arg, xVal, mode, log);
      const n = nodeCost("neg", mode);
      log.push({ fn: "neg", op: getOpLabel("neg", mode), nodes: n });
      return -v;
    }
    case "add": {
      const l = evalNode(node.left, xVal, mode, log);
      const r = evalNode(node.right, xVal, mode, log);
      const n = nodeCost("add", mode);
      log.push({ fn: "+", op: getOpLabel("add", mode), nodes: n });
      return l + r;
    }
    case "sub": {
      const l = evalNode(node.left, xVal, mode, log);
      const r = evalNode(node.right, xVal, mode, log);
      const n = nodeCost("sub", mode);
      log.push({ fn: "−", op: getOpLabel("sub", mode), nodes: n });
      return l - r;
    }
    case "mul": {
      const l = evalNode(node.left, xVal, mode, log);
      const r = evalNode(node.right, xVal, mode, log);
      const n = nodeCost("mul", mode);
      log.push({ fn: "×", op: getOpLabel("mul", mode), nodes: n });
      return l * r;
    }
    case "div": {
      const l = evalNode(node.left, xVal, mode, log);
      const r = evalNode(node.right, xVal, mode, log);
      const n = nodeCost("div", mode);
      log.push({ fn: "÷", op: getOpLabel("div", mode), nodes: n });
      return l / r;
    }
    case "pow": {
      const l = evalNode(node.left, xVal, mode, log);
      const r = evalNode(node.right, xVal, mode, log);
      const n = nodeCost("pow", mode);
      log.push({ fn: "^", op: getOpLabel("pow", mode), nodes: n });
      return Math.pow(l, r);
    }
    case "call": return evalCall(node, xVal, mode, log);
    default: throw new ParseError(`Unknown node type: ${node.type}`);
  }
}

function evalCall(node, xVal, mode, log) {
  const { fn, arg1, arg2 } = node;
  const n = nodeCost(fn, mode);
  const v1 = evalNode(arg1, xVal, mode, log);
  const v2 = arg2 ? evalNode(arg2, xVal, mode, log) : null;

  let result;
  switch (fn) {
    case "sin":
      result = mode === "best" ? sin_best(v1) : mode === "eml" ? sin_eml_taylor(v1) : Math.sin(v1);
      break;
    case "cos":
      result = mode === "best" ? cos_best(v1) : mode === "eml" ? cos_eml_taylor(v1) : Math.cos(v1);
      break;
    case "tan":  result = Math.tan(v1);  break;
    case "exp":  result = Math.exp(v1);  break;
    case "ln":   result = Math.log(v1);  break;
    case "pow":  result = Math.pow(v1, v2); break;
    case "sqrt": result = Math.sqrt(v1); break;
    case "abs":  result = Math.abs(v1);  break;
    default: throw new ParseError(`Unknown function: '${fn}'`);
  }

  log.push({ fn, op: getOpLabel(fn, mode), nodes: n });
  return result;
}

// ── Math.* reference evaluation (no node tracking) ────────────────────────────
function evalMath(node, xVal) {
  switch (node.type) {
    case "num": return node.v;
    case "var": return xVal;
    case "neg": return -evalMath(node.arg, xVal);
    case "add": return evalMath(node.left, xVal) + evalMath(node.right, xVal);
    case "sub": return evalMath(node.left, xVal) - evalMath(node.right, xVal);
    case "mul": return evalMath(node.left, xVal) * evalMath(node.right, xVal);
    case "div": return evalMath(node.left, xVal) / evalMath(node.right, xVal);
    case "pow": return Math.pow(evalMath(node.left, xVal), evalMath(node.right, xVal));
    case "call": {
      const v1 = evalMath(node.arg1, xVal);
      const v2 = node.arg2 ? evalMath(node.arg2, xVal) : null;
      switch (node.fn) {
        case "sin": return Math.sin(v1);
        case "cos": return Math.cos(v1);
        case "tan": return Math.tan(v1);
        case "exp": return Math.exp(v1);
        case "ln":  return Math.log(v1);
        case "pow": return Math.pow(v1, v2);
        case "sqrt":return Math.sqrt(v1);
        case "abs": return Math.abs(v1);
        default: return NaN;
      }
    }
    default: return NaN;
  }
}

// ── Public API ─────────────────────────────────────────────────────────────────
export function buildAST(expr) {
  const trimmed = expr.trim();
  if (!trimmed) return null;
  return parse(tokenize(trimmed));  // throws ParseError on syntax error
}

export function evalExpr(expr, xVal, mode) {
  try {
    const trimmed = expr.trim();
    if (!trimmed) return null;
    const tokens = tokenize(trimmed);
    const ast    = parse(tokens);

    // Mode evaluation
    const nodeLog = [];
    const value   = evalNode(ast, xVal, mode, nodeLog);

    if (!isFinite(value)) return { error: "Domain error — adjust x slider" };

    // Reference (Math.*)
    const mathValue = evalMath(ast, xVal);
    const absError  = isFinite(mathValue) ? Math.abs(value - mathValue) : null;

    const totalNodes = nodeLog.reduce((s, e) => s + e.nodes, 0);

    // EML node count for savings badge
    let emlNodes = totalNodes;
    if (mode !== "eml") {
      try {
        const emlLog = [];
        evalNode(ast, xVal, "eml", emlLog);
        emlNodes = emlLog.reduce((s, e) => s + e.nodes, 0);
      } catch { emlNodes = null; }
    }

    return { value, mathValue, absError, nodeLog, totalNodes, emlNodes };
  } catch (e) {
    if (e instanceof ParseError) return { error: e.message };
    return { error: "Evaluation error" };
  }
}
