"""Busca un error típico en los guiones: una función interna (lambda o def) que usa una variable de la
función que la contiene, y esa variable se vuelve a asignar más abajo (al dibujar se leería el valor nuevo).
    python3 tools/cierres.py scenes/cinematica_t2.py
"""
import ast
import sys


def own_assigns(fn):
    """names assigned in fn's own body (not inside nested functions) -> [line numbers]"""
    out = {}

    def visit(node):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, (ast.FunctionDef, ast.Lambda, ast.AsyncFunctionDef)):
                if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    out.setdefault(ch.name, []).append(ch.lineno)
                continue
            if isinstance(ch, ast.Name) and isinstance(ch.ctx, ast.Store):
                out.setdefault(ch.id, []).append(ch.lineno)
            visit(ch)
    visit(fn)
    return out


def local_names(inner):
    names = set(a.arg for a in inner.args.args + inner.args.kwonlyargs)
    if inner.args.vararg:
        names.add(inner.args.vararg.arg)
    body = inner.body if isinstance(inner.body, list) else [inner.body]
    for b in body:
        for n in ast.walk(b):
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
                names.add(n.id)
    return names


def check(path):
    tree = ast.parse(open(path).read())
    found = 0
    for fn in [n for n in tree.body if isinstance(n, ast.FunctionDef)]:
        assigns = own_assigns(fn)
        multi = {k: sorted(v) for k, v in assigns.items() if len(v) > 1}
        for inner in ast.walk(fn):
            if inner is fn or not isinstance(inner, (ast.FunctionDef, ast.Lambda)):
                continue
            loc = local_names(inner)
            seen = set()
            for node in ast.walk(inner):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and node.id in multi \
                        and node.id not in loc and node.id not in seen:
                    later = [ln for ln in multi[node.id] if ln > inner.lineno]
                    if later:
                        seen.add(node.id)
                        found += 1
                        print(f"{path}:{inner.lineno}: '{node.id}' se reasigna después (líneas {later})")
    return found


if __name__ == "__main__":
    n = sum(check(p) for p in sys.argv[1:])
    print("sin problemas" if n == 0 else f"{n} posibles problemas")
    sys.exit(1 if n else 0)
