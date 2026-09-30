# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: strip_map(text)@L25; symbols(text, python)@L32; header(rows, python)@L68; render(path)@L87; main()@L101
# variables: ROOT@L21; DIRECTORIES@L22; rows@L34; tree@L36; node@L37; kind@L39; name@L40; name@L42; argument@L46; line@L56; value@L56; match@L59; match@L61; match@L63; grouped@L70; kind@L70; kind@L71; line@L71; name@L71; descriptions@L73; descriptions@L77; kind@L79; values@L79; value@L83; value@L84; original@L89; python@L90; revised@L91; _@L92; rows@L93; candidate@L94; revised@L97; parser@L103; args@L105; paths@L106; directory@L109; path@L110; index@L116; stale@L122; path@L123; rows@L124; updated@L124; index@L129; index@L135; kind@L136; line@L136; name@L136; expected@L139; output@L140
# parameters: text@L25; python@L32; text@L32; row@L65; python@L68; rows@L68; path@L87; path@L114
# </code-map>

"""Mechanically refresh exact source function/class/variable locations and docs index.

This is a bulk mechanical source-header rewrite, not semantic source editing.
Python maps are AST-derived; TypeScript/JavaScript declaration locations use a
small explicit regex and are labeled accordingly. Generated headers are CI checked.
"""

import argparse
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECTORIES = ("studio", "runner", "training", "scripts", "examples", "tests", "ui", "desktop")


def strip_map(text: str) -> str:
    """Remove only the generated marker block, preserving authored comments/docstrings."""
    return re.sub(
        r"(?ms)^# <code-map>\n.*?^# </code-map>\n\n|^/\* <code-map>\n.*?^ \* </code-map> \*/\n\n", "", text
    )


def symbols(text: str, python: bool) -> list[tuple[str, str, int]]:
    """Extract definition sites; parameters are listed alongside their declaration locations."""
    rows = set()
    if python:
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                kind = "class" if isinstance(node, ast.ClassDef) else "function"
                name = node.name
                if hasattr(node, "args"):
                    name += (
                        "("
                        + ", ".join(
                            argument.arg
                            for argument in node.args.posonlyargs + node.args.args + node.args.kwonlyargs
                        )
                        + ")"
                    )
                rows.add((kind, name, node.lineno))
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                rows.add(("variable", node.id, node.lineno))
            elif isinstance(node, ast.arg):
                rows.add(("parameter", node.arg, node.lineno))
    else:
        for line, value in enumerate(text.splitlines(), 1):
            if value.lstrip().startswith(("//", "/*", "*")):
                continue
            for match in re.finditer(r"\b(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)", value):
                rows.add(("function", match[1] + "(" + match[2] + ")", line))
            for match in re.finditer(r"\b(?:const|let|var)\s+(\w+|\[[^]]+\]|\{[^}]+\})", value):
                rows.add(("variable", match[1], line))
            for match in re.finditer(r"\b(?:interface|type|class)\s+(\w+)", value):
                rows.add(("type", match[1], line))
    return sorted(rows, key=lambda row: (row[2], row[0], row[1]))


def header(rows: list[tuple[str, str, int]], python: bool) -> str:
    """Make compact accurate definitions; source docstrings describe semantic use."""
    grouped = {kind: [] for kind in ("class", "type", "function", "variable", "parameter")}
    for kind, name, line in rows:
        grouped[kind].append(f"{name}@L{line}")
    descriptions = [
        "Generated definition map; @L is the exact declaration line.",
        "Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.",
    ]
    descriptions += [
        ("classes" if kind == "class" else kind + "s") + ": " + "; ".join(values)
        for kind, values in grouped.items()
        if values
    ]
    if python:
        return "# <code-map>\n" + "\n".join("# " + value for value in descriptions) + "\n# </code-map>\n\n"
    return "/* <code-map>\n" + "\n".join(" * " + value for value in descriptions) + "\n * </code-map> */\n\n"


def render(path: Path) -> tuple[str, list[tuple[str, str, int]]]:
    """Resolve self-shifting header line offsets to a stable map."""
    original = strip_map(path.read_text(encoding="utf-8"))
    python = path.suffix == ".py"
    revised = original
    for _ in range(8):
        rows = symbols(revised, python)
        candidate = header(rows, python) + original
        if candidate == revised:
            return revised, rows
        revised = candidate
    raise ValueError(f"Could not stabilize source header: {path.name}")


def main() -> None:
    """Write or verify mechanically derived source headers and the exact documentation index."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    paths = sorted(
        [
            path
            for directory in DIRECTORIES
            for path in (ROOT / directory).glob("*")
            if path.suffix in {".py", ".ts", ".tsx", ".cjs"}
        ]
        + list(ROOT.glob("*config.ts")),
        key=lambda path: path.relative_to(ROOT).as_posix(),
    )
    index = [
        "# Code symbol index",
        "",
        "Generated declaration locations. Python uses AST; JS/TS uses declaration-line matching. Inline docstrings/comments describe behavior and variable use. Headers include exact positions and are checked mechanically in CI.",
        "",
    ]
    stale = []
    for path in paths:
        updated, rows = render(path)
        if path.read_text(encoding="utf-8") != updated:
            stale.append(str(path.relative_to(ROOT)))
            if not args.check:
                path.write_text(updated, encoding="utf-8", newline="\n")
        index += [
            "## " + path.relative_to(ROOT).as_posix(),
            "",
            "| Kind | Declaration | Line |",
            "|---|---|---|",
        ]
        index += [
            f"| {kind} | `{name.replace('|', '/').replace('`', '')}` | {line} |" for kind, name, line in rows
        ]
        index.append("")
    expected = "\n".join(index)
    output = ROOT / "docs/code-index.md"
    if not output.exists() or output.read_text(encoding="utf-8") != expected:
        stale.append("docs/code-index.md")
        if not args.check:
            output.write_text(expected, encoding="utf-8", newline="\n")
    if args.check and stale:
        raise SystemExit("Stale code maps: " + ", ".join(stale))
    print(f"Checked {len(paths)} source maps")


if __name__ == "__main__":
    main()
