#!/usr/bin/env python3
"""Extract Python code fences from docs/tutorials/*.md into examples/tutorials/*.

Each ```python fence is written to examples/tutorials/<slug>/NN.py and the
fence in the .md is replaced with a pymdownx.snippets include, so docs and
runnable code stay in sync.

Layout assumed (all under honba-docs/):
    docs/tutorials/*.md              <- source
    examples/tutorials/<slug>/*.py   <- extracted
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

DOCS_ROOT = Path(__file__).resolve().parent.parent
TUTORIALS_DIR = DOCS_ROOT / "docs" / "tutorials"
EXAMPLES_DIR = DOCS_ROOT / "examples" / "tutorials"
SNIPPET_PREFIX = "examples/tutorials"


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

FENCE_RE = re.compile(
    r"^(?P<open>```(?:python|py|python3)(?:\s+[^\n]*)?)\n"
    r"(?P<code>.*?)"
    r"^(?P<close>```)\s*$",
    flags=re.DOTALL | re.MULTILINE,
)

def process(md: Path) -> int:
    text = md.read_text(encoding="utf-8")
    matches = list(FENCE_RE.finditer(text))
    if not matches:
        print(f"skip (no python fences): {md.relative_to(DOCS_ROOT)}")
        return 0

    slug = slugify(md.stem)
    out_dir = EXAMPLES_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    # write files first
    for i, m in enumerate(matches, 1):
        out_file = out_dir / f"{i:02d}.py"
        out_file.write_text(m.group("code").strip() + "\n", encoding="utf-8")
        print(f"wrote   {out_file.relative_to(DOCS_ROOT)}")

    # rewrite .md by rebuilding it left-to-right
    new_text = []
    cursor = 0
    for i, m in enumerate(matches, 1):
        new_text.append(text[cursor:m.start()])
        snippet = f'--8<-- "{SNIPPET_PREFIX}/{slug}/{i:02d}.py"'
        new_text.append(f"```python\n{snippet}\n```")
        cursor = m.end()
    new_text.append(text[cursor:])

    md.write_text("".join(new_text), encoding="utf-8")
    print(f"rewrote {md.relative_to(DOCS_ROOT)}")
    return len(matches)

def main() -> int:
    if not TUTORIALS_DIR.exists():
        print(f"no tutorials dir: {TUTORIALS_DIR}", file=sys.stderr)
        return 1

    total = 0
    for md in sorted(TUTORIALS_DIR.glob("*.md")):
        if md.name == "index.md":
            continue
        total += process(md)

    print(f"\nExtracted {total} block(s) into {EXAMPLES_DIR.relative_to(DOCS_ROOT)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
