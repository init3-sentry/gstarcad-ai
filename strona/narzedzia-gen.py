#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# narzedzia-gen.py — JEDYNY generator katalogu narzedzi GSAI. Zero zaleznosci (stdlib).
#
# JEDYNE ZRODLO PRAWDY (SoT) = ../NARZEDZIA.md.
#   Ten skrypt PARSUJE NARZEDZIA.md (nie zaden osobny JSON) i z jednego parsowania
#   emituje widok dla copywiterki Eryki. Bo jest JEDEN parse, widoki nie moga sie rozjechac.
#
# Zastapil DWA rozjezdzajace sie generatory (drift „9 dni stary", 2026-08-21):
#   - strona/gen-narzedzia-dla-eryki.py  (czytal osobny strona/narzedzia-status.json)  — USUNIETY
#   - skrypty/katalog-gen.py             (czytal bloki @KATALOG z przykladow dydakt.)   — USUNIETY
#
# JAK PARSUJE NARZEDZIA.md:
#   - Naglowek sekcji (## ...) -> status wszystkich wierszy pod nim:
#       ✅ -> gotowe | 🟡 -> w_tescie | 🔧 -> w_budowie | ⛔ -> wycofane | 🧪 -> pomijane (wzorce dydakt.)
#   - Wiersz tabeli: komenda = code-span(y) `GSAI_XXX` w PIERWSZEJ kolumnie
#       (wiersz bez komendy GSAI_ = naglowek/separator/wzorzec -> pomijany automatycznie).
#       Dwie komendy w kolumnie (`GSAI_A` / `GSAI_B`) -> dwa wpisy.
#       Komenda przekreslona (~~...~~) albo wiersz z ⛔ -> nadpisuje status na „wycofane".
#   - Opis = druga kolumna („Co robi"), oczyszczona z markdownu.
#
# CO EMITUJE:
#   - strona/NARZEDZIA-DLA-ERYKI-AKTUALNE.md — regula: na strone idzie TYLKO ✅ gotowe;
#     🟡 = jeszcze nie; w_budowie/wycofane = poza strona. Naglowek + data (dzis albo sys.argv[1]),
#     sekcja „Co sie zmienilo" z diffa, licznik.
#
# CACHE (nie edytowac recznie): strona/.narzedzia.prev.json — snapshot {komenda: status}
#   z POPRZEDNIEGO parsowania, do sekcji „Co sie zmienilo". Kasowanie = reset historii diffa.
#
# KATALOG.md (skrypty/katalog-gen.py, dawny generator #2) jest MARTWY — nielinkowany z zadnego
#   pliku repo, tresc stara/uszkodzona; glownym konsumentem jest Eryka. Nie reanimujemy go.
#   Jesli kiedys bedzie potrzebny widok „po branzy", dolozyc go TU jako kolejny emit z tego parsowania.
import json
import os
import re
import sys
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SOT = os.path.join(HERE, "..", "NARZEDZIA.md")
PREV = os.path.join(HERE, ".narzedzia.prev.json")
OUT = os.path.join(HERE, "NARZEDZIA-DLA-ERYKI-AKTUALNE.md")

# naglowek sekcji -> status. Kolejnosc wg pierwszego trafionego emoji.
SECTION_STATUS = [
    ("✅", "gotowe"),
    ("🟡", "w_tescie"),
    ("🔧", "w_budowie"),
    ("⛔", "wycofane"),
    ("🧪", None),  # biblioteka wzorcow — dydaktyka, poza katalogiem
]

STMAP = {
    "gotowe": "✅ NA STRONE",
    "w_tescie": "🟡 w testach (jeszcze nie)",
    "w_budowie": "🔧 poza strona (w budowie)",
    "wycofane": "⛔ poza strona (wycofane)",
}

CMD_RE = re.compile(r"`\s*(GSAI_[A-Z0-9_]+)\s*`")


def _section_status(header):
    for emoji, status in SECTION_STATUS:
        if emoji in header:
            return status
    return None  # sekcja bez znacznika statusu (np. „Gdzie zglaszac") -> wiersze pomijane


def _clean(text):
    """Zdejmij markdown z opisu, zostaw czysty tekst dla copywiterki."""
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # [tekst](url) -> tekst
    text = text.replace("~~", "").replace("**", "").replace("`", "")
    text = text.replace(r"\|", "|")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _cells(line):
    """Rozbij wiersz tabeli markdown na komorki (bez skrajnych pustych)."""
    parts = line.strip().strip("|").split("|")
    return [p.strip() for p in parts]


def parse(md_path):
    """Zwraca liste wpisow: [{cmd, opis, status, sekcja}]. Jeden parse dla wszystkich widokow."""
    with open(md_path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    entries = []
    seen = set()
    section_name = None
    section_status = None

    for raw in lines:
        line = raw.rstrip()
        # naglowek sekcji tylko na poziomie dokumentu (nie w cytacie „> ###")
        if line.startswith("## "):
            section_name = line[3:].strip()
            section_status = _section_status(section_name)
            continue
        if not line.lstrip().startswith("|"):
            continue
        if section_status is None:
            continue
        cells = _cells(line)
        if len(cells) < 2:
            continue
        first = cells[0]
        cmds = CMD_RE.findall(first)
        if not cmds:
            continue  # naglowek/separator/wiersz bez komendy GSAI_

        # per-wiersz override na wycofane: przekreslenie albo ⛔ w wierszu
        row_status = section_status
        if "~~" in first or "⛔" in line:
            row_status = "wycofane"

        opis = _clean(cells[1])
        for cmd in cmds:
            if cmd in seen:
                continue
            seen.add(cmd)
            entries.append({"cmd": cmd, "opis": opis, "status": row_status, "sekcja": section_name})
    return entries


def load_prev():
    if not os.path.exists(PREV):
        return None
    try:
        with open(PREV, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def diff(cur_map, prev_map):
    if prev_map is None:
        return []
    ch = []
    for cmd, st in cur_map.items():
        if cmd not in prev_map:
            ch.append("+ NOWE: %s (%s)" % (cmd, STMAP.get(st, st)))
        elif prev_map[cmd] != st:
            ch.append("~ %s: %s -> %s" % (cmd, STMAP.get(prev_map[cmd], prev_map[cmd]), STMAP.get(st, st)))
    for cmd in prev_map:
        if cmd not in cur_map:
            ch.append("- USUNIETE: %s" % cmd)
    return ch


def render_eryka(entries, stamp, changes):
    gotowe = [e for e in entries if e["status"] == "gotowe"]
    w_tescie = [e for e in entries if e["status"] == "w_tescie"]
    w_budowie = [e for e in entries if e["status"] == "w_budowie"]
    wycofane = [e for e in entries if e["status"] == "wycofane"]

    L = []
    L.append("# Narzedzia na strone - LISTA AUTOMATYCZNA (dla Eryki)")
    L.append("")
    L.append("> **Aktualizowane automatycznie z NARZEDZIA.md.** Zerkaj tu **raz dziennie**. "
             "Ostatnia aktualizacja: **%s**." % stamp)
    L.append("> Regula: **na strone idzie tylko ✅.** 🟡 = jeszcze nie obiecuj (moze sie zmienic). "
             "**NIE edytuj tego pliku recznie** — zrodlem jest `NARZEDZIA.md`.")
    L.append("")
    if changes:
        L.append("## 🔔 Co sie zmienilo od ostatniego razu")
        for c in changes:
            L.append("- " + c)
        L.append("")
    L.append("Gotowych na strone: **%d** | w testach: **%d** | poza strona (w budowie/wycofane): **%d**"
             % (len(gotowe), len(w_tescie), len(w_budowie) + len(wycofane)))
    L.append("")

    L.append("## ✅ Na strone (gotowe)")
    L.append("")
    for e in sorted(gotowe, key=lambda x: x["cmd"]):
        L.append("- **`%s`** — %s" % (e["cmd"], e["opis"]))
    L.append("")

    L.append("## 🟡 W testach — jeszcze NIE na strone")
    L.append("")
    for e in sorted(w_tescie, key=lambda x: x["cmd"]):
        L.append("- `%s` — %s" % (e["cmd"], e["opis"]))
    L.append("")

    if w_budowie:
        L.append("## 🔧 W budowie — poza strona")
        L.append("")
        for e in sorted(w_budowie, key=lambda x: x["cmd"]):
            L.append("- `%s` — %s" % (e["cmd"], e["opis"]))
        L.append("")

    if wycofane:
        L.append("## ⛔ NIE umieszczac (wycofane / zastapione natywnym GstarCAD)")
        L.append("")
        L.append("- " + ", ".join("`%s`" % e["cmd"] for e in sorted(wycofane, key=lambda x: x["cmd"])))
        L.append("")

    return "\n".join(L).rstrip() + "\n"


def main():
    stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().isoformat()
    entries = parse(SOT)
    cur_map = {e["cmd"]: e["status"] for e in entries}
    changes = diff(cur_map, load_prev())

    md = render_eryka(entries, stamp, changes)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(md)
    with open(PREV, "w", encoding="utf-8") as f:
        json.dump(cur_map, f, ensure_ascii=False, indent=2, sort_keys=True)

    n = {"gotowe": 0, "w_tescie": 0, "w_budowie": 0, "wycofane": 0}
    for e in entries:
        n[e["status"]] += 1
    print("OK: %s" % os.path.basename(OUT))
    print("Sparsowano: %d | gotowe: %d | w_tescie: %d | w_budowie: %d | wycofane: %d"
          % (len(entries), n["gotowe"], n["w_tescie"], n["w_budowie"], n["wycofane"]))
    print("Zmian od ostatniego razu: %d" % len(changes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
