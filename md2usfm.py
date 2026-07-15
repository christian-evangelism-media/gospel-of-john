#!/usr/bin/env python3
"""Convert the Teksto ti Biblia markdown format to USFM.

The source (github.com/nasantuan-a-biblia/teksto-ti-biblia) stores each book as
a directory of NN.md chapter files in a simple markdown convention:

  - an H1 setext title (the book name) at the top of chapter 1
  - a "Kapitulo N" setext H2 marking each chapter
  - "### ..." section headings
  - one verse per line: "N text..."  (a lone "N" starts a poetry verse)
  - blank lines are paragraph breaks
  - lines indented with spaces are second-level poetry

It emits a single USFM file for the whole book, compatible with the texish
`usfm` package used by the gospel-of-john editions.

Usage:
    python3 md2usfm.py --src ~/teksto-ti-biblia/juan --id JHN \
        --name Juan --abbr Jn --out ilo.usfm
"""

import argparse
import glob
import os
import re
import sys

# A verse line is a number, optionally followed by text on the same line.
VERSE_RE = re.compile(r'^(\d+)(?:\s+(.*))?$')

# Poetry uses indentation for its second level; the source indents those lines.
POETRY_INDENT = 2


def is_rule(line, ch):
    """True if `line` is a setext underline made only of `ch` (=== or ---)."""
    s = line.strip()
    return len(s) >= 3 and set(s) == {ch}


def indent_of(line):
    return len(line) - len(line.lstrip(' '))


def emit_prose(block):
    """A paragraph of prose: one `\\p`, then a `\\v` per numbered line.

    A line with no leading number continues the verse already open (a verse
    whose text runs past a section heading or paragraph break), so it is
    emitted without a new `\\v`.
    """
    out = ['\\p']
    for line in block:
        text = line.strip()
        m = VERSE_RE.match(text)
        if m:
            num, rest = m.group(1), (m.group(2) or '')
            out.append(f'\\v {num} {rest}'.rstrip())
        else:
            out.append(text)
    return out


def emit_poetry(block):
    """A poetic stanza: `\\q1` for flush lines, `\\q2` for indented ones.

    A lone verse number on its own line attaches to the next poetic line.
    """
    out = []
    pending = None
    for line in block:
        level = 2 if indent_of(line) >= POETRY_INDENT else 1
        text = line.strip()
        m = VERSE_RE.match(text)
        if m and m.group(2) is None:
            pending = m.group(1)
            continue
        if m:
            num, rest = m.group(1), (m.group(2) or '')
            out.append(f'\\q{level} \\v {num} {rest}'.rstrip())
            pending = None
        elif pending is not None:
            out.append(f'\\q{level} \\v {pending} {text}'.rstrip())
            pending = None
        else:
            out.append(f'\\q{level} {text}')
    return out


def emit_block(block):
    """A blank-line-delimited text block is poetry if any line is indented."""
    if any(indent_of(l) >= POETRY_INDENT for l in block):
        return emit_poetry(block)
    return emit_prose(block)


def build_header(book_id, full_title, name, abbr):
    """The USFM identification and title headers.

    `full_title` (the source H1, e.g. "Ebanghelio ni Juan") becomes `\\toc1`
    and splits across two main-title lines: all-but-last word over the last.
    """
    words = full_title.split()
    mt2 = ' '.join(words[:-1]) if len(words) > 1 else ''
    mt1 = words[-1] if words else name
    header = [
        f'\\id {book_id}',
        '',
        '\\usfm 3.1',
        f'\\h {name}',
        f'\\toc1 {full_title}',
        f'\\toc2 {name}',
        f'\\toc3 {abbr}',
    ]
    if mt2:
        header.append(f'\\mt2 {mt2}')
    header.append(f'\\mt1 {mt1}')
    return header


def convert(src_dir, book_id, name, abbr, figures=False):
    files = sorted(glob.glob(os.path.join(src_dir, '[0-9][0-9].md')))
    if not files:
        sys.exit(f'no NN.md chapter files found in {src_dir}')

    out = []
    header_done = False
    full_title = None
    block = []

    def flush():
        if block:
            out.extend(emit_block(block))
            block.clear()

    def ensure_header():
        nonlocal header_done
        if not header_done:
            out.extend(build_header(book_id, full_title or name, name, abbr))
            header_done = True

    for path in files:
        with open(path, encoding='utf-8') as f:
            lines = f.read().split('\n')
        i = 0
        while i < len(lines):
            line = lines[i]
            nxt = lines[i + 1] if i + 1 < len(lines) else ''

            if line.strip() and is_rule(nxt, '='):
                flush()
                full_title = line.strip()
                i += 2
                continue

            m = re.match(r'^Kapitulo\s+(\d+)\s*$', line)
            if m and is_rule(nxt, '-'):
                flush()
                ensure_header()
                num = int(m.group(1))
                out.append(f'\\c {num}')
                if figures:
                    out.append(f'\\fig |src="ch{num:02d}.png" size="col"\\fig*')
                i += 2
                continue

            if line.startswith('### '):
                flush()
                out.append(f'\\s1 {line[4:].strip()}')
                i += 1
                continue

            if not line.strip():
                flush()
                i += 1
                continue

            block.append(line)
            i += 1
        flush()

    return '\n'.join(out) + '\n'


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--src', required=True, help='directory of NN.md chapter files')
    ap.add_argument('--id', default='JHN', help='USFM book id (default: JHN)')
    ap.add_argument('--name', default='Juan', help='short book name (default: Juan)')
    ap.add_argument('--abbr', default='Jn', help='book abbreviation (default: Jn)')
    ap.add_argument('--out', required=True, help='output .usfm path')
    ap.add_argument('--figures', action='store_true',
                    help='insert a \\fig chNN.png chapter image after each \\c')
    args = ap.parse_args()

    usfm = convert(os.path.expanduser(args.src), args.id, args.name,
                   args.abbr, figures=args.figures)
    with open(os.path.expanduser(args.out), 'w', encoding='utf-8') as f:
        f.write(usfm)
    print(f'wrote {args.out}')


if __name__ == '__main__':
    main()
