#!/usr/bin/env python3
"""katalog-gen.py — autonomiczny generator katalogu narzędzi GstarCAD.

Skanuje biblioteka-rag/przyklady/*.py, wyciąga blok metadanych `# @KATALOG`
i składa KATALOG.md (tabela pogrupowana po branży). Skrypt bez bloku @KATALOG
jest pomijany (dydaktyczne wzorce 01-20 nie zaśmiecają katalogu klienckiego).

Blok w skrypcie (w nagłówku, linie komentarza):
  # @KATALOG
  # nazwa: Renumeracja elementów
  # komenda: RENUMERUJ
  # branza: ogólne
  # opis: Automatyczne przenumerowanie... (2-3 zdania).
  # przyklad: Ponumerowanie 200 pomieszczeń na rzucie w kilka sekund.

Autonomia: uruchamiany cyklicznie (cron na Oracle) — pull repo -> ten skrypt ->
commit/push KATALOG.md. Nowy skrypt z blokiem = automatycznie w katalogu.
Bez zależności zewnętrznych (tylko stdlib) — działa na Oracle bez venv.
"""
import os
import re
import sys
from datetime import datetime, timezone

FIELDS = ("nazwa", "komenda", "branza", "opis", "przyklad")


def parse_katalog_blocks(path):
    """Zwraca listę dict metadanych (wiele bloków @KATALOG w jednym pliku, np. EKSPORT+IMPORT)."""
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return []
    blocks = []
    cur = None
    for ln in lines:
        s = ln.strip()
        if re.match(r"#\s*@KATALOG\b", s):
            if cur and "komenda" in cur:
                blocks.append(cur)
            cur = {}
            continue
        if cur is not None:
            if not s.startswith("#"):
                if "komenda" in cur:
                    blocks.append(cur)
                cur = None
                continue
            m = re.match(r"#\s*([a-ząćęłńóśźż]+)\s*:\s*(.+)$", s, re.IGNORECASE)
            if m and m.group(1).lower() in FIELDS:
                cur[m.group(1).lower()] = m.group(2).strip()
    if cur and "komenda" in cur:
        blocks.append(cur)
    for b in blocks:
        b.setdefault("nazwa", b.get("komenda", "?"))
        b.setdefault("branza", "ogólne")
        b.setdefault("opis", "")
        b.setdefault("przyklad", "")
        b["_plik"] = os.path.basename(path)
    return blocks


def build_markdown(entries):
    now = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
    out = []
    out.append("# Katalog narzędzi GstarCAD (TMSys)\n")
    out.append(f"> ⚙️ **Plik generowany automatycznie** przez `skrypty/katalog-gen.py` "
               f"(cron na Oracle). Nie edytuj ręcznie — opis pochodzi z bloku `# @KATALOG` "
               f"w każdym skrypcie. Ostatnia aktualizacja: **{now}**. Narzędzi: **{len(entries)}**.\n")
    # grupowanie po branży
    by_branch = {}
    for e in entries:
        by_branch.setdefault(e["branza"], []).append(e)
    for branch in sorted(by_branch):
        items = sorted(by_branch[branch], key=lambda x: x["nazwa"].lower())
        out.append(f"\n## {branch.capitalize()}\n")
        out.append("| Komenda | Narzędzie | Co robi | Przykład |")
        out.append("|---|---|---|---|")
        for e in items:
            kom = f"`{e['komenda']}`"
            opis = e["opis"].replace("|", "\\|")
            przyk = e["przyklad"].replace("|", "\\|")
            out.append(f"| {kom} | {e['nazwa']} | {opis} | {przyk} |")
    out.append("")
    return "\n".join(out)


def main():
    root = os.environ.get("KATALOG_REPO") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = os.path.join(root, "biblioteka-rag", "przyklady")
    out_path = os.path.join(root, "KATALOG.md")
    entries = []
    skipped = 0
    for name in sorted(os.listdir(src)):
        if not name.endswith(".py"):
            continue
        blocks = parse_katalog_blocks(os.path.join(src, name))
        if blocks:
            entries.extend(blocks)
        else:
            skipped += 1
    md = build_markdown(entries)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"[katalog-gen] {len(entries)} narzędzi w katalogu, {skipped} plików bez @KATALOG (pominięte).")
    print(f"[katalog-gen] zapisano: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
