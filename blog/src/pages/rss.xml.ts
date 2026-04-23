import type { APIRoute } from "astro";

const SITE = "https://monogate.org";
const TITLE = "Monogate — Research Blog";
const DESCRIPTION =
  "Monogate Research: one operator for all elementary functions. Blog posts on SuperBEST routing, ELC characterisation, Lean-verified theorems, and the EML framework.";

function xmlEscape(s: string): string {
  return s.replace(/[<>&'"]/g, (ch) => ({
    "<": "&lt;", ">": "&gt;", "&": "&amp;", "'": "&apos;", '"': "&quot;",
  }[ch] as string));
}

function stripMdFrontmatter(raw: string): { title?: string; description?: string; pubDate?: string; body: string } {
  const m = raw.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
  if (!m) return { body: raw };
  const fm = m[1];
  const body = m[2];
  const title = /^title:\s*(.+?)\s*$/m.exec(fm)?.[1]?.replace(/^['"]|['"]$/g, "");
  const description = /^description:\s*(.+?)\s*$/m.exec(fm)?.[1]?.replace(/^['"]|['"]$/g, "");
  const pubDate = /^(date|pubDate):\s*['"]?(.+?)['"]?\s*$/m.exec(fm)?.[2];
  return { title, description, pubDate, body };
}

export const GET: APIRoute = async () => {
  const md = import.meta.glob("./blog/*.md", { eager: true, query: "?raw", import: "default" });

  const items: Array<{ slug: string; title: string; description: string; pubDate: string }> = [];
  for (const [path, raw] of Object.entries(md)) {
    const slug = path.replace(/^\.\/blog\//, "").replace(/\.md$/, "");
    if (slug === "index") continue;
    const parsed = stripMdFrontmatter(raw as string);
    // Pull a short description from the first paragraph if frontmatter omits it
    let desc = parsed.description;
    if (!desc) {
      const firstPara = parsed.body
        .split(/\n\n+/)
        .find((p) => p.trim() && !p.startsWith("#"));
      desc = firstPara ? firstPara.replace(/\n/g, " ").slice(0, 300) : "";
    }
    items.push({
      slug,
      title: parsed.title || slug.replace(/-/g, " "),
      description: desc || "",
      pubDate: parsed.pubDate || new Date().toISOString(),
    });
  }
  // Newest first by pubDate; fall back to slug
  items.sort((a, b) => (b.pubDate || "").localeCompare(a.pubDate || "") || b.slug.localeCompare(a.slug));

  const now = new Date().toUTCString();

  const body =
    '<?xml version="1.0" encoding="UTF-8"?>\n' +
    '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n' +
    "  <channel>\n" +
    `    <title>${xmlEscape(TITLE)}</title>\n` +
    `    <link>${SITE}</link>\n` +
    `    <description>${xmlEscape(DESCRIPTION)}</description>\n` +
    `    <language>en-us</language>\n` +
    `    <lastBuildDate>${now}</lastBuildDate>\n` +
    `    <atom:link href="${SITE}/rss.xml" rel="self" type="application/rss+xml" />\n` +
    items
      .map((it) => {
        const pub = (() => {
          try {
            return new Date(it.pubDate).toUTCString();
          } catch {
            return now;
          }
        })();
        return (
          "    <item>\n" +
          `      <title>${xmlEscape(it.title)}</title>\n` +
          `      <link>${SITE}/blog/${it.slug}</link>\n` +
          `      <guid>${SITE}/blog/${it.slug}</guid>\n` +
          `      <pubDate>${pub}</pubDate>\n` +
          `      <description>${xmlEscape(it.description)}</description>\n` +
          "    </item>"
        );
      })
      .join("\n") +
    "\n  </channel>\n</rss>\n";

  return new Response(body, {
    headers: { "Content-Type": "application/rss+xml; charset=utf-8" },
  });
};
