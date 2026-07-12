# Wzorcowa komenda 25 — Import współrzędnych z pliku (CSV / Notatnik) → punkty w rysunku.
#
# Zamyka pozycję #8 z raportu Roberta („jest eksport współrzędnych, brakuje importu").
# Klasyka geodezyjna: masz plik z numerami i współrzędnymi punktów (z tachimetru,
# z Excela, z Notatnika) i chcesz je wrzucić do rysunku jako PUNKTY (GcDbPoint —
# łapią się osnapem WĘZeł/NODe), każdy z opisem numeru.
#
# REALIA PL (świadomie obsłużone):
#   - Excel PL eksportuje CSV separatorem ŚREDNIK, a przecinek to znak dziesiętny
#     (np. "1;5600123,45;7400987,10"). Notatnik zwykle spacja/tab. Obsługujemy oba:
#     separator = średnik/tab jeśli obecny, inaczej białe znaki; przecinek dziesiętny
#     zamieniany na kropkę PRZY parsowaniu liczby.
#   - Współrzędne geodezyjne PL (PUWG2000) są rzędu milionów → wysokość opisu i
#     odsunięcie liczone są DYNAMICZNIE z rozpiętości punktów (2% przekątnej), a nie
#     stałą wartością — inaczej tekst byłby niewidoczny albo gigantyczny.
#   - Punkty w CAD są domyślnie niewidoczne (PDMODE=0 = kropka 1px). Best-effort
#     ustawiamy PDMODE=3 (krzyżyk X — klasyczny punkt geodezyjny, czysto) i
#     PDSIZE=-2 (2% ekranu), żeby było je widać.
#
# Format pliku wybierany słowem kluczowym (komenda pyta):
#   XY     : "X Y"            (bez numeru, bez Z; numer nadawany automatycznie 1,2,3…)
#   XYZ    : "X Y Z"
#   NrXY   : "Nr X Y"         (pierwsza kolumna = numer/nazwa punktu)  ← DOMYŚLNY
#   NrXYZ  : "Nr X Y Z"
#
# Sposób użycia: APPLOAD tego pliku → komenda IMPORTXYZ → wybierz plik w oknie
# (przeglądasz katalogi, klikasz plik) → wybierz format → punkty i opisy pojawią się
# w rysunku → wpisz ZOOM, potem A (Wszystko) albo E (Zakres), żeby je zobaczyć.
# UWAGA: opcji „Granice/G" ZOOM nie ma.
#
# Konwencje domu: 3 importy, @command, całość w try/except, Gcad.eOk dla bazy /
# RTNORM dla wejścia edytora, model space open→append→close, GcDbText(pt, str).

from pygcad.core import *
from pygcad.core.runtime import *
from pygcad.pygrx import *
import re


def _openModelSpace():
    """Zwraca (ms, db) z modelem otwartym do zapisu, albo (None, None)."""
    db = gcdbWorkingDatabase()
    status, bt = db.getBlockTable(GcDb.kForRead)
    if status != Gcad.eOk:
        return None, None
    status, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForWrite)
    bt.close()
    if status != Gcad.eOk:
        return None, None
    return ms, db


def _setPointDisplayVars():
    """Best-effort: zrób punkty widocznymi (PDMODE/PDSIZE). Niekrytyczne."""
    try:
        rb = resbuf()
        rb.restype = RTSHORT
        rb.resval.rint = 3             # krzyżyk X — klasyczny marker punktu geodezyjnego (czysto)
        gcedSetVar("PDMODE", rb)
        rb2 = resbuf()
        rb2.restype = RTREAL
        rb2.resval.rreal = -2.0        # ujemne = % rozmiaru ekranu (skaluje się z zoomem)
        gcedSetVar("PDSIZE", rb2)
    except Exception:
        pass                            # brak widoczności punktów nie psuje importu


def _parseLine(raw, fmt):
    """Zamień linię pliku na (label, x, y, z) wg wybranego formatu. None = pomiń."""
    line = raw.strip()
    if not line or line.startswith("#") or line.startswith("//"):
        return None
    # separator: średnik/tab (Excel PL) jeśli obecny, inaczej białe znaki (Notatnik)
    if ";" in line or "\t" in line:
        toks = [t.strip() for t in re.split(r"[;\t]+", line) if t.strip()]
    else:
        toks = [t.strip() for t in re.split(r"\s+", line) if t.strip()]
    if not toks:
        return None

    def num(tok):
        return float(tok.replace(",", "."))   # przecinek dziesiętny PL → kropka

    try:
        if fmt == "XY":
            return (None, num(toks[0]), num(toks[1]), 0.0)
        if fmt == "XYZ":
            return (None, num(toks[0]), num(toks[1]), num(toks[2]))
        if fmt == "NrXY":
            return (toks[0], num(toks[1]), num(toks[2]), 0.0)
        if fmt == "NrXYZ":
            return (toks[0], num(toks[1]), num(toks[2]), num(toks[3]))
    except (ValueError, IndexError):
        return None                            # linia niepełna / nagłówek tekstowy → pomiń
    return None


def _readRows(path, fmt):
    """Czyta plik (utf-8 z fallbackiem cp1250) i zwraca (rows, skipped_count)."""
    data = None
    for enc in ("utf-8-sig", "cp1250", "latin-1"):
        try:
            with open(path, "r", encoding=enc) as fp:
                data = fp.readlines()
            break
        except (UnicodeDecodeError, OSError):
            continue
    if data is None:
        return None, 0

    rows, skipped = [], 0
    auto = 0
    for raw in data:
        parsed = _parseLine(raw, fmt)
        if parsed is None:
            if raw.strip() and not raw.strip().startswith(("#", "//")):
                skipped += 1
            continue
        label, x, y, z = parsed
        if label is None:
            auto += 1
            label = str(auto)
        rows.append((label, x, y, z))
    return rows, skipped


@command(local_name='IMPORTXYZ')
def importxyz():
    """Wczytaj plik ze współrzędnymi i wstaw punkty + opisy numerów."""
    try:
        # 1) wybór pliku — NATYWNE okno „przeglądaj katalogi i kliknij plik"
        #    (gcedGetFileD) — intuicyjne, nie trzeba wpisywać całej ścieżki.
        #    Fallback: gdyby okno nie zadziałało (wyjątek), pytamy o ścieżkę tekstem,
        #    żeby nie zepsuć już zweryfikowanej drogi.
        path = None
        okno_ok = True
        try:
            rbf = resbuf()
            # (tytul, domyslna nazwa, filtr rozszerzenia, flagi, wynik w resbuf)
            rc = gcedGetFileD("Wybierz plik ze wspolrzednymi (CSV / TXT)", "", "csv;txt", 0, rbf)
        except Exception:
            okno_ok = False
            rc = None
        if okno_ok:
            if rc == RTNORM:
                try:
                    path = rbf.resval.rstring
                except Exception:
                    path = None
            else:
                gcutPrintf("\nAnulowano (nie wybrano pliku).")   # klik Anuluj w oknie
                return
        if not path:                                              # okno niedostępne → wpisanie ścieżki
            status, path = gcedGetString(1, "\nPodaj sciezke do pliku ze wspolrzednymi: ")
            if status != RTNORM or not path or not path.strip():
                gcutPrintf("\nAnulowano.")
                return
        path = path.strip().strip('"')

        # 2) format pliku (słowo kluczowe; Enter = domyślny NrXY)
        #    gcedInitGet MUSI poprzedzać gcedGetKword — inaczej KAŻDE wpisane słowo
        #    jest odrzucane jako „Nieprawidłowe opcje słów kluczowych" (wzorzec 15).
        gcedInitGet(0, "XY XYZ NrXY NrXYZ")
        rc, kw = gcedGetKword("\nFormat pliku [XY/XYZ/NrXY/NrXYZ] <NrXY>: ")
        if rc == RTNONE:
            fmt = "NrXY"                                   # Enter bez wpisania = domyślny
        elif rc == RTNORM and kw in ("XY", "XYZ", "NrXY", "NrXYZ"):
            fmt = kw
        else:
            gcutPrintf("\nAnulowano.")
            return

        rows, skipped = _readRows(path, fmt)
        if rows is None:
            gcutPrintf("\n[BLAD] Nie mozna otworzyc pliku: %s" % path)
            return
        if not rows:
            gcutPrintf("\n[IMPORTXYZ] Zero poprawnych wierszy w formacie %s (pominieto %d). Sprawdz format." % (fmt, skipped))
            return

        # 3) auto-skalowanie opisu z rozpiętości punktów
        xs = [r[1] for r in rows]
        ys = [r[2] for r in rows]
        span = max(max(xs) - min(xs), max(ys) - min(ys))
        txtH = (span * 0.02) if span > 1e-6 else 2.5   # 2% rozpiętości; fallback dla 1 pkt
        off = txtH * 0.6

        ms, _ = _openModelSpace()
        if ms is None:
            gcutPrintf("\n[BLAD] Nie mozna otworzyc przestrzeni modelu.")
            return

        placed = 0
        for label, x, y, z in rows:
            pt = GcGePoint3d(x, y, z)
            point = GcDbPoint(pt)
            ms.appendGcDbEntity(point)
            point.close()

            txt = GcDbText(GcGePoint3d(x + off, y + off, z), str(label))
            txt.setHeight(txtH)
            ms.appendGcDbEntity(txt)
            txt.close()
            placed += 1

        ms.close()
        _setPointDisplayVars()

        gcutPrintf("\n[IMPORTXYZ] Wstawiono %d punktow (format %s, pominieto %d wierszy)." % (placed, fmt, skipped))
        gcutPrintf("\n[IMPORTXYZ] Wpisz ZOOM, potem A (Wszystko), zeby zobaczyc wszystkie punkty.")

    except Exception as err:
        gcutPrintf("\n[IMPORTXYZ BLAD] %s: %s" % (type(err).__name__, str(err)))
