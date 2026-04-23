import type { APIRoute } from "astro";

const SITE = "https://monogate.org";

// Static top-level pages
const STATIC_PAGES: Array<{ url: string; lastmod?: string; changefreq?: string; priority?: number }> = [
  { url: "/",            priority: 1.0, changefreq: "weekly" },
  { url: "/one-operator", priority: 0.9, changefreq: "monthly" },
  { url: "/superbest",   priority: 0.9, changefreq: "monthly" },
  { url: "/framework",   priority: 0.8, changefreq: "monthly" },
  { url: "/atlas",       priority: 0.8, changefreq: "monthly" },
  { url: "/theorems",    priority: 0.8, changefreq: "monthly" },
  { url: "/proofs",      priority: 0.9, changefreq: "monthly" },
  { url: "/paper",       priority: 0.8, changefreq: "monthly" },
  { url: "/blog",        priority: 0.9, changefreq: "weekly" },
];

function xmlEscape(s: string): string {
  return s.replace(/[<>&'"]/g, (ch) => ({
    "<": "&lt;", ">": "&gt;", "&": "&amp;", "'": "&apos;", '"': "&quot;",
  }[ch] as string));
}

export const GET: APIRoute = async () => {
  // Discover blog posts: .md files under src/pages/blog/ and .astro (excluding index)
  const mdPosts = import.meta.glob("./blog/*.md", { eager: true, query: "?raw", import: "default" });
  const astroPosts = import.meta.glob("./blog/*.astro", { eager: true, query: "?raw", import: "default" });

  const posts: Array<{ slug: string; lastmod?: string }> = [];
  for (const path of Object.keys(mdPosts)) {
    const slug = path.replace(/^\.\/blog\//, "").replace(/\.md$/, "");
    if (slug === "index") continue;
    posts.push({ slug });
  }
  for (const path of Object.keys(astroPosts)) {
    const slug = path.replace(/^\.\/blog\//, "").replace(/\.astro$/, "");
    if (slug === "index") continue;
    posts.push({ slug });
  }
  posts.sort((a, b) => a.slug.localeCompare(b.slug));

  const now = new Date().toISOString().slice(0, 10);

  const urls = [
    ...STATIC_PAGES.map((p) => ({
      loc: `${SITE}${p.url}`,
      lastmod: p.lastmod ?? now,
      changefreq: p.changefreq ?? "monthly",
      priority: p.priority ?? 0.7,
    })),
    ...posts.map((p) => ({
      loc: `${SITE}/blog/${p.slug}`,
      lastmod: now,
      changefreq: "yearly",
      priority: 0.6,
    })),
  ];

  const body =
    '<?xml version="1.0" encoding="UTF-8"?>\n' +
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    urls
      .map(
        (u) =>
          `  <url>\n` +
          `    <loc>${xmlEscape(u.loc)}</loc>\n` +
          `    <lastmod>${u.lastmod}</lastmod>\n` +
          `    <changefreq>${u.changefreq}</changefreq>\n` +
          `    <priority>${u.priority.toFixed(1)}</priority>\n` +
          `  </url>`
      )
      .join("\n") +
    "\n</urlset>\n";

  return new Response(body, {
    headers: { "Content-Type": "application/xml; charset=utf-8" },
  });
};
