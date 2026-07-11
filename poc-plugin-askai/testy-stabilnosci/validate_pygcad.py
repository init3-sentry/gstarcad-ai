#!/usr/bin/env python3
"""
Lokalny walidator wygenerowanego kodu pygcad względem stubów pygrx.pyi.
0 tokenów API — czysta analiza AST.

Łapie klasy błędów, które wychodziły dopiero na żywo:
  - pusty konstruktor gdy klasa go nie ma (przypadek GcDbText())
  - wywołanie konstruktora z liczbą argumentów spoza wszystkich przeciążeń
  - metoda/atrybut-wywołanie których NIE MA w żadnej klasie stubów
    (słaby sygnał halucynacji, np. dawne .handle() na GcDbBlockReference)

Użycie:
  validate_pygcad.py <stub.pyi> <snippet_dir_or_file> [...]
"""
import ast
import sys
from pathlib import Path


def build_stub_index(pyi_path):
    """Zwraca:
      class_arities: {simple_name: set(dozwolone liczby pozycyjnych argów w __init__)}
      class_has_zeroarg: {simple_name: bool}
      class_defined: set(nazwy klas)
      all_methods: set(nazwy wszystkich metod/funkcji zdef. w stubach)
    """
    src = Path(pyi_path).read_text(encoding="utf-8")
    tree = ast.parse(src)
    class_arities = {}
    class_has_zero = {}
    class_defined = set()
    all_methods = set()

    def init_arity(fn):
        # liczba pozycyjnych po self: min (bez domyślnych) .. max
        args = fn.args
        pos = args.args[1:]  # pomiń self
        n_max = len(pos)
        n_defaults = len(args.defaults)
        n_min = n_max - n_defaults
        # *args => akceptuje dowolną >= n_min
        star = args.vararg is not None
        return n_min, n_max, star

    def visit_class(node):
        name = node.name
        class_defined.add(name)
        arities = class_arities.setdefault(name, set())
        has_zero = class_has_zero.get(name, False)
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                all_methods.add(item.name)
                if item.name == "__init__":
                    n_min, n_max, star = init_arity(item)
                    if star:
                        for k in range(n_min, n_min + 12):
                            arities.add(k)
                    else:
                        for k in range(n_min, n_max + 1):
                            arities.add(k)
                    if n_min == 0:
                        has_zero = True
            elif isinstance(item, ast.ClassDef):
                visit_class(item)  # zagnieżdżone (enumy, podklasy)
        class_has_zero[name] = has_zero

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            visit_class(node)
    return class_arities, class_has_zero, class_defined, all_methods


def call_name(func):
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def n_positional(call):
    # licz pozycyjne (bez *args rozpakowania); starred liczymy jako 1+ ~ pomijamy strict
    return sum(1 for a in call.args if not isinstance(a, ast.Starred))


def validate_snippet(code, idx):
    """Zwraca listę (severity, msg)."""
    flags = []
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return [("BŁĄD", f"SyntaxError: {e}")]
    class_arities, class_has_zero, class_defined, all_methods = idx
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = call_name(fn)
        if name is None:
            continue
        # Konstruktor klasy Gc* wywołany jako Name(...)
        if isinstance(fn, ast.Name) and name.startswith("Gc") and name in class_defined:
            nargs = n_positional(node)
            arities = class_arities.get(name, set())
            has_kw = any(k.arg for k in node.keywords)
            if not arities:
                continue  # brak jawnego __init__ w stubie (dziedziczony) — nie ryzykuj FP
            if nargs == 0 and not class_has_zero.get(name, False) and not has_kw:
                flags.append(("BŁĄD", f"{name}() — pusty konstruktor, a stub wymaga argumentów (arności: {sorted(arities)})"))
            elif nargs not in arities and not has_kw:
                flags.append(("UWAGA", f"{name}(...) wołany z {nargs} arg pozycyjnymi, stub zna arności {sorted(arities)}"))
        # Wywołanie metody .foo(...) — słaby sygnał halucynacji
        elif isinstance(fn, ast.Attribute) and name.startswith(("get", "set", "append", "add", "handle", "color", "textString", "contents")):
            if name not in all_methods:
                flags.append(("UWAGA", f".{name}() — brak takiej metody w stubach (możliwa halucynacja lub metoda modułowa)"))
    return flags


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    stub = sys.argv[1]
    idx = build_stub_index(stub)
    _, _, class_defined, all_methods = idx
    print(f"[stub] {len(class_defined)} klas, {len(all_methods)} unikalnych nazw metod\n")
    targets = []
    for p in sys.argv[2:]:
        pp = Path(p)
        if pp.is_dir():
            targets += sorted(pp.glob("*.py"))
        else:
            targets.append(pp)
    total_bad = 0
    for t in targets:
        code = Path(t).read_text(encoding="utf-8")
        flags = validate_snippet(code, idx)
        bad = [f for f in flags if f[0] == "BŁĄD"]
        total_bad += len(bad)
        status = "🔴 BŁĄD" if bad else ("🟡 UWAGA" if flags else "🟢 OK")
        print(f"{status}  {t.name}")
        for sev, msg in flags:
            print(f"      [{sev}] {msg}")
    print(f"\n=== PODSUMOWANIE: {total_bad} twardych błędów w {len(targets)} snippetach ===")
    sys.exit(1 if total_bad else 0)


if __name__ == "__main__":
    main()
