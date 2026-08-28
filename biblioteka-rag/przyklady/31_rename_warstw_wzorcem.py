# Wzorcowa komenda 31 — Rename warstw WZORCEM (batch find->replace) z dry-run.
#
# ⚠ NAPISANE, NIETESTOWANE — wymaga uruchomienia na prawdziwym rysunku.
#   Powstalo bez pulpitu; przeszla wylacznie kompilacja skladni + walidator.
#   To narzedzie ZMIENIA rysunek (setName na warstwach) — testowac TYLKO na
#   kopii, i najpierw na jednej warstwie (dowod, ze setName dziala z Pythona).
#
# DLACZEGO ISTNIEJE (ADR 08 §6 funkcja nr 4, cytat §B):
#   Natywne -RENAME obsluguje wildcardy (A-* -> B-*), ale NIE: zamiane w SRODKU
#   nazwy, wielu warstw naraz wg wzorca, ani obslugi KOLIZJI. rRename (ARKANCE)
#   ma 40 426 wyswietlen = udokumentowany popyt. QA Manager Autodesku potwierdzil
#   luke na pismie i zaprosil zewnetrznego dewelopera (referencje/warstwy-konkurencja-cytaty §2).
#   ⛔ NIE mowimy "natywne nie umie zmieniac nazw" — umie wildcardy. Nasza nisza:
#   find->replace w dowolnym miejscu nazwy, batch, + (v1.1) merge przy kolizji.
#
# ZAKRES v1 (ten plik): zamiana PODCIAGU w nazwach warstw (find -> replace),
#   wsadowo, z DRY-RUN (podglad co sie zmieni) i POTWIERDZENIEM przed zapisem.
#   Kolizja (nowa nazwa = istniejaca inna warstwa) -> ZGLASZAMY i POMIJAMY te
#   warstwe. NIE merge'ujemy w v1 (merge = przenoszenie encji + kasowanie warstwy
#   = najbardziej crash-ryzykowny zapis w pygcad; idzie jako v1.1 PO potwierdzeniu setName).
#
# BEZPIECZENSTWO (te same reguly co GSAI_WARSTWY / 28_layer_report):
#   - getAt PO NAZWIE (kForWrite), ZERO .cast() (cast truje sesje, BUG-07).
#   - try/finally przy KAZDYM otwarciu tabeli i rekordu.
#   - warstwy 0 / DEFPOINTS / z XREF-a (isDependent) POMIJAMY — nieprzemianowalne.
#     isRenamable() jest niewiarygodne w GS2027 SP1 (True dla "0", BUG-08) -> heurystyka.
#   - checkpoint _ck() przed kazdym setName -> jak natywny crash, wiadomo na ktorej warstwie.
#   - komunikaty ASCII (domyslny font gubi PL, #49).
#   - DRY-RUN najpierw: nic nie zapisujemy, dopoki user nie potwierdzi.
#
# Uzycie: APPLOAD -> GSAI_ZNW. Podajesz co zamienic i na co, widzisz
#   podglad, potwierdzasz. Nic sie nie dzieje bez potwierdzenia.

# @KATALOG
# nazwa: Zmiana nazw warstw wzorcem
# komenda: GSAI_ZNW
# komenda_en: GSAI_RENAMELAYERS
# branza: ogolne
# opis: Zmienia nazwy wielu warstw naraz wedlug wzorca (zamien fragment nazwy na inny), z podgladem przed zapisem. Robi to, czego natywne -RENAME nie ma: zamiane w srodku nazwy i wsadowo. Kolizje nazw wykrywa i zglasza. Nic nie zmienia bez potwierdzenia; dziala tylko na warstwach, ktore wolno przemianowac (pomija 0, DEFPOINTS i warstwy z odnosnikow).
# przyklad: Rysunek po kilku biurach: zamiana przedrostka "P-" na "C-" w 40 warstwach jednym poleceniem, zamiast recznie po jednej.

from pygcad.core import *
from pygcad.core.runtime import *
from pygcad.pygrx import *
import os

DEBUG_PLIKU = "gsai_rename_warstw_debug.txt"


def _ck(msg):
    """Checkpoint: NADPISUJE plik debug ostatnim krokiem + fsync. Natywny crash
    (GCAD abnormal exit) omija try/except Pythona; plik trzyma OSTATNIE setName
    przed faultem = winowajce."""
    try:
        pulpit = os.path.join(os.path.expanduser("~"), "Desktop")
        if not os.path.isdir(pulpit):
            pulpit = os.path.expanduser("~")
        with open(os.path.join(pulpit, DEBUG_PLIKU), "w", encoding="utf-8") as f:
            f.write(msg + "\n")
            f.flush()
            os.fsync(f.fileno())
    except Exception:
        pass


def _nazwy_warstw(db):
    """Same NAZWY warstw + czy przemianowalne (heurystyka, bez cast) -> dict.

    Kolejnosc/idiom jak w 28_layer_report: getName na rekordach z iteratora (nie truje),
    a wlasciwosci przez getAt PO NAZWIE (typowany rekord, bez cast). generateUsageData
    nie jest potrzebne (nie liczymy isInUse) — wystarczy isDependent (xref).
    Zwraca: { nazwa: {"xref": bool, "mozna": bool} } albo None.
    """
    _ck("nazwy: getLayerTable")
    st, lt = db.getLayerTable(GcDb.kForRead)
    if st != Gcad.eOk:
        return None
    nazwy = []
    try:
        st, it = lt.newIterator()
        try:
            it.start()
        except Exception:
            pass
        while not it.done():
            st2, rec = it.getRecord(GcDb.kForRead)
            if rec is not None:
                try:
                    stn, n = rec.getName()
                    if stn == Gcad.eOk and n:
                        nazwy.append(n)
                finally:
                    rec.close()
            it.step()
    finally:
        lt.close()

    out = {}
    st, lt = db.getLayerTable(GcDb.kForRead)
    if st != Gcad.eOk:
        return None
    try:
        for n in nazwy:
            xref = False
            sst, lrec = lt.getAt(n, GcDb.kForRead)   # typowany rekord — BEZ cast
            if sst == Gcad.eOk and lrec is not None:
                try:
                    xref = bool(lrec.isDependent())
                except Exception:
                    xref = False
                finally:
                    lrec.close()
            specjalna = n.upper() in ("0", "DEFPOINTS")
            out[n] = {"xref": xref, "mozna": not (specjalna or xref)}
    finally:
        lt.close()
    _ck("nazwy: %d warstw" % len(out))
    return out


def _plan(warstwy, szukaj, zamien):
    """Buduje plan zmian BEZ dotykania bazy (dry-run).
    Zwraca (rename, kolizje, pominiete):
      rename   = [(stara, nowa)]   — do wykonania
      kolizje  = [(stara, nowa)]   — nowa nazwa juz istnieje jako INNA warstwa
      pominiete= [stara]           — nieprzemianowalne (0/DEFPOINTS/xref) a pasowaly
    """
    istnieje = set(warstwy.keys())
    rename, kolizje, pominiete = [], [], []
    for stara, meta in warstwy.items():
        if szukaj not in stara:
            continue
        nowa = stara.replace(szukaj, zamien)
        if nowa == stara:
            continue
        if not meta["mozna"]:
            pominiete.append(stara)
            continue
        # kolizja: nowa nazwa istnieje i to NIE jest ta sama warstwa
        if nowa in istnieje and nowa != stara:
            kolizje.append((stara, nowa))
        else:
            rename.append((stara, nowa))
    return rename, kolizje, pominiete


@command(local_name='GSAI_ZNW', global_name='GSAI_RENAMELAYERS', group_name='GSAI')
def rename_warstw():
    """Zmiana nazw warstw wzorcem (find->replace), z podgladem i potwierdzeniem."""
    try:
        st, szukaj = gcedGetString(1, "\nZamien w nazwie warstwy - fragment DO ZNALEZIENIA: ")
        if st != RTNORM or not (szukaj or "").strip():
            gcutPrintf("\nAnulowano.")
            return
        szukaj = szukaj.strip()

        # gcedGetString(0,...) -> spacja konczy wpis; (1,...) pozwala spacje. Dla "na co"
        # pozwalamy pusty (usuniecie fragmentu), wiec czytamy z flaga 1 i nie wymagamy tresci.
        st, zamien = gcedGetString(1, "\nZamienic na (moze byc puste = usun fragment): ")
        if st != RTNORM:
            gcutPrintf("\nAnulowano.")
            return
        zamien = (zamien or "").strip()

        db = gcdbWorkingDatabase()
        warstwy = _nazwy_warstw(db)
        if not warstwy:
            gcutPrintf("\n[RENAME] Nie moge odczytac warstw. Nic nie zrobiono.")
            return

        rename, kolizje, pominiete = _plan(warstwy, szukaj, zamien)

        # ── DRY-RUN: pokaz plan, NIC nie zapisano ──────────────────────────────
        gcutPrintf("\n=== PODGLAD (nic jeszcze nie zmieniono) ===")
        gcutPrintf("\nWarstw do przemianowania: %d" % len(rename))
        for stara, nowa in rename[:20]:
            gcutPrintf("\n   %s  ->  %s" % (stara, nowa))
        if len(rename) > 20:
            gcutPrintf("\n   ... i %d dalszych" % (len(rename) - 20))

        if kolizje:
            gcutPrintf("\n! KOLIZJE (nowa nazwa juz istnieje): %d - te POMINIEMY w v1"
                       % len(kolizje))
            for stara, nowa in kolizje[:10]:
                gcutPrintf("\n   %s  ->  %s  (warstwa '%s' juz jest)" % (stara, nowa, nowa))
            gcutPrintf("\n  (Scalanie warstw przy kolizji przyjdzie w kolejnej wersji.)")

        if pominiete:
            gcutPrintf("\n- Pominieto jako nieprzemianowalne (0/DEFPOINTS/xref): %d"
                       % len(pominiete))

        if not rename:
            gcutPrintf("\n[RENAME] Nic do zmiany. Koniec.")
            return

        st, ok = gcedGetString(0, "\nWykonac te zmiany? wpisz TAK aby potwierdzic: ")
        if st != RTNORM or (ok or "").strip().upper() not in ("TAK", "T", "YES", "Y"):
            gcutPrintf("\nAnulowano. Nic nie zmieniono.")
            return

        # ── WYKONANIE: setName po jednej warstwie, checkpoint przed kazda ───────
        zrobione, bledy = 0, []
        st, lt = db.getLayerTable(GcDb.kForWrite)
        if st != Gcad.eOk:
            gcutPrintf("\n[RENAME] Nie moge otworzyc tabeli warstw do zapisu.")
            return
        try:
            for stara, nowa in rename:
                _ck("setName: '%s' -> '%s'" % (stara, nowa))
                sst, lrec = lt.getAt(stara, GcDb.kForWrite)   # typowany rekord — BEZ cast
                if sst != Gcad.eOk or lrec is None:
                    bledy.append("%s: nie otwarto do zapisu" % stara)
                    continue
                try:
                    rst = lrec.setName(nowa)   # <-- JEDYNA niepewna API: setName z Pythona
                    if rst == Gcad.eOk:
                        zrobione += 1
                    else:
                        bledy.append("%s: setName status=%s" % (stara, rst))
                except Exception as e:
                    bledy.append("%s: %s" % (stara, e))
                finally:
                    lrec.close()
        finally:
            lt.close()
        _ck("koniec: zrobione=%d" % zrobione)

        gcutPrintf("\n=== WYNIK ===")
        gcutPrintf("\nPrzemianowano warstw: %d" % zrobione)
        if bledy:
            gcutPrintf("\nNie udalo sie: %d" % len(bledy))
            for b in bledy[:10]:
                gcutPrintf("\n   - %s" % b)
        if kolizje:
            gcutPrintf("\nPominieto z powodu kolizji nazw: %d (scalanie w kolejnej wersji)."
                       % len(kolizje))
        gcutPrintf("\n[RENAME] Gotowe. Sprawdz rysunek; jesli cos nie tak - Cofnij (UNDO).")

    except Exception as err:
        gcutPrintf("\n[RENAME BLAD] %s: %s" % (type(err).__name__, err))
        gcutPrintf("\n[RENAME] Jesli cos zdazylo sie zmienic - uzyj UNDO.")
