# KB frontmatter grammar (restricted YAML)

Records are Markdown files whose first line is `---`, followed by a frontmatter
block, a closing `---`, then the Markdown body. The parser (`kbrecord.py`) is
dependency-free and supports **only** the subset below. Anything outside it is
rejected with a `FrontmatterError` naming the file and line — it is never
silently reinterpreted.

## Supported

```
---
key: scalar value
quoted: "value with: a colon"
single: 'also fine'
empty:                      # -> "" (empty string)
flow_list: [a, b, c]        # -> ["a","b","c"]
empty_list: []              # -> []
block_list:                 # -> ["item one","item two"]
  - item one
  - item two
---
```

- **Top-level keys only.** Keys start at column 0. The only legal indentation is
  a block-list item line (`  - value`) under a key whose value is empty.
- **Scalars** are taken verbatim after `key:`, minus an optional surrounding
  quote pair and an optional trailing ` # comment` (comment detection respects
  quotes).
- **Lists** are either inline flow (`[a, b]`) or a block of `  - ` lines.
- **Comments:** a `#` preceded by whitespace (or at line start) begins a
  comment; `#` inside quotes is literal.
- **Blank lines** and full-line `#` comments inside the block are ignored.

## Rejected (hard errors, by design)

| Input | Why |
|---|---|
| Missing opening/closing `---` | not a record / unterminated block |
| Indented `key: value` (nested map) | nesting unsupported — use flat keys |
| Duplicate key in one block | ambiguous |
| `key: {a: b}` (flow mapping) | flow mappings unsupported |
| `key: \|` or `key: >` (block scalar) | multi-line scalars unsupported |
| `key: &anchor` / `*alias` / `!tag` | anchors/aliases/tags unsupported |

## Rationale

The schema needs only scalars and simple lists of IDs/strings. Forbidding
nesting, flow maps, block scalars, and anchors keeps the parser small enough to
run on a stock Python 3 (no PyYAML) while guaranteeing that an author who
reaches for unsupported YAML gets a clear failure instead of a value that
quietly parses to the wrong thing. If a record needs more structure, add a
flat field — do not nest.
