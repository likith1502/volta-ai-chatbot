import React from 'react';

/**
 * Renders the small subset of Markdown that AI replies use:
 *   **bold**, *italic*, `code`, # / ## / ### headings,
 *   "- " / "* " bullets, "1. " numbered lists, paragraphs.
 *
 * Builds React elements directly (never dangerouslySetInnerHTML), so model
 * output can't inject HTML, scripts or links.
 */

const INLINE = /(\*\*[^*\n]+\*\*|__[^_\n]+__|\*[^*\n]+\*|`[^`\n]+`)/g;

function renderInline(text: string, keyPrefix: string): React.ReactNode[] {
  return text.split(INLINE).map((part, i) => {
    const key = `${keyPrefix}-${i}`;
    if ((part.startsWith('**') && part.endsWith('**')) || (part.startsWith('__') && part.endsWith('__'))) {
      if (part.length > 4) return <strong key={key}>{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith('*') && part.endsWith('*') && part.length > 2) {
      return <em key={key}>{part.slice(1, -1)}</em>;
    }
    if (part.startsWith('`') && part.endsWith('`') && part.length > 2) {
      return <code key={key} className="fmt-code">{part.slice(1, -1)}</code>;
    }
    return part;
  });
}

function renderLines(text: string, keyPrefix: string): React.ReactNode[] {
  return text.split('\n').map((ln, i) => (
    <React.Fragment key={`${keyPrefix}-l${i}`}>
      {i > 0 && <br />}
      {renderInline(ln, `${keyPrefix}-l${i}`)}
    </React.Fragment>
  ));
}

type Block =
  | { kind: 'p'; lines: string[] }
  | { kind: 'h'; text: string }
  | { kind: 'ul'; items: string[] }
  | { kind: 'ol'; items: string[]; start: number };

function parseBlocks(src: string): Block[] {
  const blocks: Block[] = [];
  const push = (b: Block) => blocks.push(b);
  for (const raw of src.replace(/\r\n/g, '\n').split('\n')) {
    const line = raw.trimEnd();
    const last = blocks[blocks.length - 1];
    // Indented line under a list item = continuation of that item
    // (e.g. "1. **Mini** ~₹130" followed by "   Compact car ...").
    if (line.trim() && /^\s+/.test(line) && (last?.kind === 'ul' || last?.kind === 'ol')
        && !/^\s*([-*•]|\d+[.)])\s+/.test(line)) {
      last.items[last.items.length - 1] += '\n' + line.trim();
      continue;
    }
    if (!line.trim()) {
      push({ kind: 'p', lines: [] }); // paragraph break marker
      continue;
    }
    const h = line.match(/^\s*#{1,6}\s+(.*)$/);
    if (h) { push({ kind: 'h', text: h[1] }); continue; }
    const ul = line.match(/^\s*[-*•]\s+(.*)$/);
    if (ul) {
      if (last?.kind === 'ul') last.items.push(ul[1]);
      else push({ kind: 'ul', items: [ul[1]] });
      continue;
    }
    const ol = line.match(/^\s*(\d+)[.)]\s+(.*)$/);
    if (ol) {
      if (last?.kind === 'ol') last.items.push(ol[2]);
      // keep the AI's numbering even if blank lines split the list
      else push({ kind: 'ol', items: [ol[2]], start: Number(ol[1]) || 1 });
      continue;
    }
    if (last?.kind === 'p' && last.lines.length) last.lines.push(line);
    else push({ kind: 'p', lines: [line] });
  }
  return blocks.filter(b => b.kind !== 'p' || b.lines.length > 0);
}

export const FormattedText: React.FC<{ text: string }> = ({ text }) => (
  <div className="fmt">
    {parseBlocks(text).map((b, i) => {
      const k = `b${i}`;
      switch (b.kind) {
        case 'h':
          return <p key={k} className="fmt-h">{renderInline(b.text, k)}</p>;
        case 'ul':
          return (
            <ul key={k}>
              {b.items.map((it, j) => <li key={j}>{renderLines(it, `${k}-${j}`)}</li>)}
            </ul>
          );
        case 'ol':
          return (
            <ol key={k} start={b.start}>
              {b.items.map((it, j) => <li key={j}>{renderLines(it, `${k}-${j}`)}</li>)}
            </ol>
          );
        default:
          return (
            <p key={k}>
              {b.lines.map((ln, j) => (
                <React.Fragment key={j}>
                  {j > 0 && <br />}
                  {renderInline(ln, `${k}-${j}`)}
                </React.Fragment>
              ))}
            </p>
          );
      }
    })}
  </div>
);
