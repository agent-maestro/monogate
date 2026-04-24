import type { APIRoute } from 'astro';
import { files, aggregates, leanRepo } from '../data/proofs';

// Plain-text companion to /proofs — curl-friendly, no HTML.
// One "-- file:line — name" header per theorem. Verbatim Lean source blocks.

export const GET: APIRoute = () => {
  const header =
    `-- monogate.org/proofs.lean.txt\n` +
    `-- ${aggregates.verifiedOriginal} original EML theorems · ${aggregates.totalStatements} total Lean statements · ${aggregates.cleanFiles} zero-sorry files (+ ${aggregates.partialFiles} partial, ${aggregates.sorriesTotal} sorries documented)\n` +
    `-- Repo: ${leanRepo}\n` +
    `-- Verify: git clone ${leanRepo} && cd monogate-lean && lake build\n` +
    `-- This file: ${aggregates.flagshipCount} flagship theorems extracted verbatim from the source.\n` +
    `-- Every block below is a literal copy; the line numbers point at the first line of each theorem in monogate-lean/MonogateEML/<file>.\n\n`;

  const body = files
    .map(f => {
      const fileHeader =
        `-- ========================================================================\n` +
        `-- ${f.file}  (${f.original} original / ${f.total} total · ${f.sorries === 0 ? '0 sorries' : `${f.sorries} sorries — documented, see below`})\n` +
        `-- ${f.thm}: ${f.what}\n` +
        `-- ========================================================================\n`;

      const theorems = f.flagships
        .map(
          th =>
            `\n-- ${f.file}:L${th.line} — ${th.name}${th.hasSorry ? '  [contains sorry — documented gap]' : ''}\n` +
            `-- ${th.hook}\n` +
            `${th.source}\n`
        )
        .join('');

      return fileHeader + theorems;
    })
    .join('\n');

  return new Response(header + body, {
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
      'Cache-Control': 'public, max-age=300, s-maxage=3600',
    },
  });
};
