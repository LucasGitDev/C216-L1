from __future__ import annotations

from html import escape
from pathlib import Path
import math
import sys


ROOT = Path(__file__).resolve().parents[1]
IMG_DIR = ROOT / "img"


def render_svg(*, title: str, lines: list[str], output_path: Path) -> None:
    IMG_DIR.mkdir(parents=True, exist_ok=True)

    font_size = 18
    line_height = 28
    padding_x = 24
    padding_top = 68
    padding_bottom = 24
    width = 1400
    height = max(220, padding_top + padding_bottom + line_height * len(lines))

    text_nodes = []
    for index, line in enumerate(lines):
        y = padding_top + index * line_height
        text_nodes.append(
            f'<text x="{padding_x}" y="{y}" fill="#e5e7eb">{escape(line)}</text>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#0f172a" />
  <rect x="12" y="12" width="{width - 24}" height="{height - 24}" rx="16" fill="#111827" stroke="#334155" />
  <text x="{padding_x}" y="42" fill="#93c5fd" font-size="24" font-weight="700">{escape(title)}</text>
  <g font-family="Menlo, Monaco, Consolas, monospace" font-size="{font_size}">
    {''.join(text_nodes)}
  </g>
</svg>
"""
    output_path.write_text(svg, encoding="utf-8")


def normalize_lines(content: str, *, max_lines: int = 24, max_columns: int = 130) -> list[str]:
    lines: list[str] = []
    for raw_line in content.splitlines():
        line = raw_line.rstrip()
        if not line:
            lines.append("")
            continue
        chunks = max(1, math.ceil(len(line) / max_columns))
        for index in range(chunks):
            start = index * max_columns
            end = start + max_columns
            lines.append(line[start:end])
    return lines[:max_lines]


def main() -> int:
    if len(sys.argv) < 4 or len(sys.argv[1:]) % 3 != 0:
        raise SystemExit(
            "usage: python scripts/generate_result_images.py <title> <input-file> <output-file> ..."
        )

    args = sys.argv[1:]
    for index in range(0, len(args), 3):
        title = args[index]
        input_path = Path(args[index + 1])
        output_path = ROOT / args[index + 2]
        content = input_path.read_text(encoding="utf-8")
        render_svg(title=title, lines=normalize_lines(content), output_path=output_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
