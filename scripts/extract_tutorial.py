#!/usr/bin/env python3
"""Extract Python code fences from docs/tutorials/*.md into examples/tutorials/."""
from pathlib import Path
import re
import sys

DOCS = Path("docs/tutorials")
OUT = Path("examples/tutorials")


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def main() -> int:
    if not DOCS.exists():
        print("No docs/tutorials directory", file=sys.stderr)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)

    for md in sorted(DOCS.glob("*.md")):
        if md.name == "index.md":
            continue

        text = md.read_text(encoding="utf-8")
        blocks = re.findall(r"```python\n(.*?)```", text, flags=re.DOTALL)

        if not blocks:
            continue

        tutorial_dir = OUT / slugify(md.stem)
        tutorial_dir.mkdir(parents=True, exist_ok=True)

        for i, block in enumerate(blocks, 1):
            out_file = tutorial_dir / f"{i:02d}.py"
            out_file.write_text(block.strip() + "\n", encoding="utf-8")
            print(f"Wrote {out_file}")

        new_text = text
        for i, block in enumerate(blocks, 1):
            snippet = f'--8<-- "examples/tutorials/{tutorial_dir.name}/{i:02d}.py"'
            new_text = new_text.replace(
                f"```python\n{block}```",
                f"```python\n{snippet}\n```",
                1,
            )

        md.write_text(new_text, encoding="utf-8")
        print(f"Updated {md}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
