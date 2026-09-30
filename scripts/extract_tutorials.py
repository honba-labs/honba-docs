#!/usr/bin/env python3
"""Extract Python code fences from docs/tutorials/*.md into examples/tutorials/.

Layout assumed (all under honba-docs/):
    docs/tutorials/*.md          <- source
    examples/tutorials/<slug>/*.py  <- extracted, parallel to docs/ and book/

Each code fence in the .md is replaced with a pymdownx.snippets include
pointing at the extracted file, so the docs and the runnable file are the
same source of truth.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

DOCS_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = DOCS_ROOT / "docs" / "tutorials"
EXAMPLES_DIR = DOCS_ROOT / "examples" / "tutorials"

SNIPPET_PREFIX = "examples/tutorials"  # relative to honba-docs/ (mkdocs base_path)


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def process(md: Path) -> int:
    text = md.read_text(encoding="utf-8")
    blocks = re.findall(r"```python\n(.*?)```", text, flags=re.DOTALL)
    if not blocks:
        print(f"skip (no python fences): {md.relative_to(DOCS_ROOT)}")
        return 0

    slug = slugify(md.stem)
    out_dir = EXAMPLES_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    for i, block in enumerate(blocks, 1):
        out_file = out_dir / f"{i:02d}.py"
        out_file.write_text(block.strip() + "\n", encoding="utf-8")
        print(f"wrote {out_file.relative_to(DOCS_ROOT)}")

    new_text = text
    for i, block in enumerate(blocks, 1):
        snippet = f'--8<-- "{SNIPPET_PREFIX}/{slug}/{i:02d}.py"'
        new_text = new_text.replace(
            f"```python\n{block}```",
            f"```python\n{snippet}\n```",
            1,
        )
    md.write_text(new_text, encoding="utf-8")
    print(f"rewrote {md.relative_to(DOCS_ROOT)}")
    return len(blocks)


def main() -> int:
    if not DOCS_DIR.exists():
        print(f"no tutorials dir: {DOCS_DIR}", file=sys.stderr)
        return 1

    total = 0
    for md in sorted(DOCS_DIR.glob("*.md")):
        if md.name == "index.md":
            continue
        total += process(md)

    print(f"\nExtracted {total} code block(s) into {EXAMPLES_DIR.relative_to(DOCS_ROOT)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
