# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: source_location(name, lines, digest, node)@L20; block_nodes(root)@L27; python_checks(name, text, project_references)@L49; add(node, code, message, severity)@L56; scope(root, symbols)@L137; references(texts)@L233
# variables: line@L22; prefix@L23; pending@L29; node@L31; findings@L51; digest@L52; lines@L54; tree@L70; table@L72; line@L74; nodes@L94; exports@L95; dynamic_exports@L96; node@L97; t@L99; item@L102; item@L104; dynamic_exports@L106; keyword@L116; value@L124; targets@L125; word@L131; target@L132; children@L139; captures@L140; pending@L141; child@L143; symbol@L146; bindings@L150; definitions@L151; node@L152; alias@L156; symbol@L165; identifier@L166; kind@L174; node@L174; child@L201; node@L202; node@L207; _@L208; value@L208; item@L212; terminated@L215; statement@L216; terminated@L223; node@L226; node@L228; result@L235; text@L236; node@L238; alias@L242
# parameters: digest@L20; lines@L20; name@L20; node@L20; root@L27; name@L49; project_references@L49; text@L49; code@L56; message@L56; node@L56; severity@L56; root@L137; symbols@L137; texts@L233
# </code-map>

"""Non-executing Python checks by Jason Stys; review candidates, never deletion advice.

AST and compiler symbol tables preserve lexical scope and original locations.
Symbols/variables: docs/code-index.md. No target modules or plugins are imported.
"""

import ast
import hashlib
import symtable


def source_location(name: str, lines: list[str], digest: str, node: ast.AST) -> dict:
    """Return one-based Unicode columns from AST's UTF-8 byte offsets and a snapshot digest."""
    line = node.lineno
    prefix = lines[line - 1].encode("utf-8")[: node.col_offset]
    return {"file": name, "line": line, "column": len(prefix.decode("utf-8")) + 1, "source_sha256": digest}


def block_nodes(root: ast.AST):
    """Walk one lexical block; child scope bodies are analyzed independently."""
    pending = list(ast.iter_child_nodes(root))
    while pending:
        node = pending.pop()
        yield node
        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
                ast.Lambda,
                ast.ListComp,
                ast.SetComp,
                ast.DictComp,
                ast.GeneratorExp,
            ),
        ):
            pending.extend(ast.iter_child_nodes(node))


def python_checks(name: str, text: str, project_references: set[str]) -> tuple[list[dict], dict]:
    """Find located syntax/risk/unused/unreachable candidates; expose conservative scope limits."""
    findings = []
    digest = hashlib.sha256(text.encode()).hexdigest()
    # Python physical lines use CR/LF, not Unicode separators embedded inside string literals.
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    def add(node: ast.AST, code: str, message: str, severity: str = "review") -> None:
        """Accumulate at most 1,001 items so the caller can signal the shared 1,000-item limit."""
        if len(findings) < 1001:
            findings.append(
                {
                    **source_location(name, lines, digest, node),
                    "code": code,
                    "message": message,
                    "severity": severity,
                    "origin": "python-static",
                }
            )

    try:
        tree = ast.parse(text, filename=name)
        compile(tree, name, "exec")  # Validate structural syntax, never execute the returned code object.
        table = symtable.symtable(text, name, "exec")
    except (SyntaxError, ValueError, RecursionError) as error:
        line = getattr(error, "lineno", None)
        if line and 0 < line <= len(lines):
            findings.append(
                {
                    "file": name,
                    "line": line,
                    "column": getattr(error, "offset", None),
                    "source_sha256": digest,
                    "code": "PY-SYNTAX",
                    "severity": "error",
                    "message": "Python syntax error: " + str(getattr(error, "msg", error))[:300],
                    "origin": "python-static",
                }
            )
        return findings, {
            "parsed": False,
            "reason": type(error).__name__,
            "location_available": bool(findings),
        }

    nodes = list(ast.walk(tree))
    exports = set()
    dynamic_exports = False
    for node in nodes:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets
        ):
            if isinstance(node.value, (ast.List, ast.Tuple, ast.Set)) and all(
                isinstance(item, ast.Constant) and isinstance(item.value, str) for item in node.value.elts
            ):
                exports.update(item.value for item in node.value.elts)
            else:
                dynamic_exports = True
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec"}:
                add(node, "PY-DYNAMIC", "Dynamic evaluation")
            if (
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and (node.func.value.id == "pickle" and node.func.attr in {"load", "loads"})
            ):
                add(node, "PY-DESERIALIZE", "Unsafe deserialization")
            for keyword in node.keywords:
                if (
                    keyword.arg == "shell"
                    and isinstance(keyword.value, ast.Constant)
                    and keyword.value.value is True
                ):
                    add(keyword, "PY-SHELL", "Shell execution")
        if isinstance(node, (ast.Assign, ast.AnnAssign)) and isinstance(node.value, ast.Constant):
            value = node.value.value
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if (
                isinstance(value, str)
                and len(value) >= 8
                and any(
                    isinstance(target, ast.Name)
                    and any(word in target.id.lower() for word in ("password", "secret", "api_key", "apikey"))
                    for target in targets
                )
            ):
                add(node, "PY-SECRET", "Possible embedded secret (value omitted)")

    def scope(root: ast.AST, symbols) -> None:
        """Use compiler references, closure captures and cross-file uses to avoid naive text counts."""
        children = list(block_nodes(root))
        captures = set()
        pending = list(symbols.get_children())
        while pending:
            child = pending.pop()
            captures.update(
                symbol.get_name()
                for symbol in child.get_symbols()
                if symbol.is_free() or (symbol.is_global() and symbol.is_referenced())
            )
            pending.extend(child.get_children())
        bindings = {}
        definitions = {}
        for node in children:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.ImportFrom) and node.module == "__future__":
                    continue
                for alias in node.names:
                    if alias.name != "*":
                        bindings.setdefault(alias.asname or alias.name.split(".")[0], (alias, "import"))
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                bindings.setdefault(node.id, (node, "local"))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                definitions[(node.name, node.lineno)] = node
                if not isinstance(node, ast.ClassDef) and not node.decorator_list:
                    bindings.setdefault(node.name, (node, "function"))
        for symbol in symbols.get_symbols():
            identifier = symbol.get_name()
            if (
                identifier not in bindings
                or identifier.startswith("_")
                or symbol.is_referenced()
                or identifier in captures
            ):
                continue
            node, kind = bindings[identifier]
            if identifier in exports or (kind in {"import", "function"} and identifier in project_references):
                continue
            if kind == "local" and (
                symbols.get_type() != "function"
                or not symbol.is_local()
                or symbol.is_parameter()
                or symbol.is_nonlocal()
                or symbol.is_global()
            ):
                continue
            if symbols.get_type() == "class" or (symbols.get_type() == "module" and dynamic_exports):
                continue
            if kind == "import":
                add(
                    node,
                    "PY-UNUSED-IMPORT",
                    f"Possibly unused import '{identifier}'; check side effects/re-exports",
                )
            elif kind == "local":
                add(node, "PY-UNUSED-LOCAL", f"Possibly unused local '{identifier}'")
            elif kind == "function":
                add(
                    node,
                    "PY-UNUSED-FUNCTION",
                    f"Possibly unused function '{identifier}'; external/dynamic callers may exist",
                )
        for child in symbols.get_children():
            node = definitions.get((child.get_name(), child.get_lineno()))
            if node is not None:
                scope(node, child)

    scope(tree, table)
    for node in nodes:
        for _, value in ast.iter_fields(node):
            if (
                not isinstance(value, list)
                or not value
                or not all(isinstance(item, ast.stmt) for item in value)
            ):
                continue
            terminated = False
            for statement in value:
                if terminated:
                    add(
                        statement,
                        "PY-UNREACHABLE",
                        "Unreachable statement after unconditional return/raise/break/continue",
                    )
                terminated |= isinstance(statement, (ast.Return, ast.Raise, ast.Break, ast.Continue))
    return findings, {
        "parsed": True,
        "function_count": sum(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) for node in nodes),
        "branch_nodes": sum(
            isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.Match)) for node in nodes
        ),
    }


def references(texts: list[str]) -> set[str]:
    """Preserve cross-file attribute/from-import uses; unrelated lexical name loads are not shared uses."""
    result = set()
    for text in texts:
        try:
            for node in ast.walk(ast.parse(text)):
                if isinstance(node, ast.Attribute):
                    result.add(node.attr)
                elif isinstance(node, ast.ImportFrom):
                    result.update(alias.name for alias in node.names)
        except (SyntaxError, ValueError, RecursionError):
            continue
    return result
