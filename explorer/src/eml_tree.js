/**
 * eml_tree.js — Tree-building layer for the EML operator.
 *
 * Every function here mirrors eml.js but returns a tree node (AST)
 * instead of a computed number. Used by the Visual Tree Explorer tab.
 *
 * Node shapes:
 *   { tag: 'eml', left: node, right: node }  — internal operator node
 *   { tag: 'lit', label: string }             — leaf (terminal or numeric literal)
 */

// ─── Primitives ───────────────────────────────────────────────────────────────

export const mkLit = (v) => ({ tag: "lit", label: String(v) });
export const mkVar = (name = "x") => ({ tag: "lit", label: name });

// Auto-wrap: numbers and strings become lit nodes; objects pass through unchanged.
const _wrap = (v) =>
  v !== null && typeof v === "object" && v.tag ? v : mkLit(v);

const eml = (x, y) => ({ tag: "eml", left: _wrap(x), right: _wrap(y) });
const ONE = { tag: "lit", label: "1" };
const TWO = { tag: "lit", label: "2" };

// ─── Constants ────────────────────────────────────────────────────────────────

/** e = eml(1,1).  Nodes:1  Depth:1 */
export const E_t = eml(ONE, ONE);

/** 0 = eml(1, eml(eml(1,1), 1)).  Nodes:3  Depth:3 */
export const ZERO_t = eml(ONE, eml(eml(ONE, ONE), ONE));

/** −1 = eml(ZERO, eml(2, 1)).  Nodes:5  Depth:4  (uses terminal 2) */
export const NEG_ONE_t = eml(ZERO_t, eml(TWO, ONE));

// ─── Functions ────────────────────────────────────────────────────────────────

/** eˣ = eml(x, 1).  Nodes:1  Depth:1 */
export const exp_t = (x) => eml(x, ONE);

/** ln x = eml(1, eml(eml(1, x), 1)).  Nodes:3  Depth:3 */
export const ln_t = (x) => eml(ONE, eml(eml(ONE, x), ONE));

/** x − y = eml(ln(x), exp(y)).  Nodes:5  Depth:4 */
export const sub_t = (x, y) => eml(ln_t(x), exp_t(y));

/**
 * −y  (shift formula only — matches complex_eml convention)
 * = eml(ZERO, eml(y − NEG_ONE, 1))  Nodes:9  Depth:5
 */
export const neg_t = (y) => eml(ZERO_t, eml(sub_t(y, NEG_ONE_t), ONE));

/** x + y = eml(ln(x), eml(neg(y), 1)).  Nodes:11  Depth:6 */
export const add_t = (x, y) => eml(ln_t(x), eml(neg_t(y), ONE));

/** x × y = eml(add(ln(x), ln(y)), 1).  Nodes:13  Depth:7 */
export const mul_t = (x, y) => eml(add_t(ln_t(x), ln_t(y)), ONE);

/** x / y = eml(add(ln(x), neg(ln(y))), 1).  Nodes:15  Depth:8 */
export const div_t = (x, y) => eml(add_t(ln_t(x), neg_t(ln_t(y))), ONE);

/** xⁿ = eml(mul(n, ln(x)), 1).  Nodes:15  Depth:8 */
export const pow_t = (x, n) => eml(mul_t(n, ln_t(x)), ONE);

/** 1/x = eml(neg(ln(x)), 1).  Nodes:5  Depth:4 */
export const recip_t = (x) => eml(neg_t(ln_t(x)), ONE);

/** √x = pow(x, 0.5) — convenience alias */
export const sqrt_t = (x) => pow_t(x, mkLit("0.5"));

// ─── Tree utilities ───────────────────────────────────────────────────────────

/** Total number of nodes (internal + leaves). */
export const countNodes = (node) => {
  if (!node) return 0;
  if (node.tag === "lit") return 1;
  return 1 + countNodes(node.left) + countNodes(node.right);
};

/** Maximum depth (root = depth 1). */
export const countDepth = (node) => {
  if (!node) return 0;
  if (node.tag === "lit") return 1;
  return 1 + Math.max(countDepth(node.left), countDepth(node.right));
};

/**
 * BFS traversal order — returns array of nodes root-first.
 * Used to determine animation reveal order.
 */
export const bfsOrder = (root) => {
  const result = [];
  const queue = [root];
  while (queue.length > 0) {
    const node = queue.shift();
    result.push(node);
    if (node.tag === "eml") {
      if (node.left) queue.push(node.left);
      if (node.right) queue.push(node.right);
    }
  }
  return result;
};

/**
 * Compute (x, y, id) layout coordinates for every node.
 * Returns a Map from node object → { x, y, id } where id is BFS index.
 *
 * Layout strategy: leaves are assigned horizontal slots 0,1,2,…
 * Internal nodes are centered over their subtree's leaf range.
 * HSPACE and VSPACE are in SVG user units.
 */
export const layoutTree = (root, HSPACE = 54, VSPACE = 80) => {
  const coords = new Map();
  let slotCounter = 0;

  const bfsNodes = bfsOrder(root);
  const idMap = new Map(bfsNodes.map((n, i) => [n, i]));

  const recurse = (node, depth) => {
    if (node.tag === "lit") {
      const x = slotCounter * HSPACE;
      slotCounter++;
      coords.set(node, { x, y: depth * VSPACE, id: idMap.get(node) });
      return { minX: x, maxX: x };
    }
    const left = recurse(node.left, depth + 1);
    const right = recurse(node.right, depth + 1);
    const x = (left.minX + right.maxX) / 2;
    coords.set(node, { x, y: depth * VSPACE, id: idMap.get(node) });
    return { minX: left.minX, maxX: right.maxX };
  };

  recurse(root, 0);
  return coords;
};

// ─── Open-challenge keywords ──────────────────────────────────────────────────

/** Functions with no known EML construction under strict principal-branch grammar. */
export const OPEN_CHALLENGES = ["sin", "cos", "tan", "pi", "i"];
