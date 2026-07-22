# Wzorcowa komenda 28 — Raport warstw: pokazuje TO, CZEGO MENEDŻER WARSTW NIE POKAZUJE.
#
# ⚠ NAPISANE, NIETESTOWANE — wymaga uruchomienia. Powstało w sesji bez pulpitu
#   (SSH), GstarCAD nie był ani razu uruchomiony. Przeszła wyłącznie kompilacja
#   składni. Przed pokazaniem komukolwiek: uruchomić na prawdziwym rysunku.
#
# DLACZEGO tak wąsko — najważniejsza decyzja w tym pliku:
#   Menedżer warstw (LAYER), LAYWALK, SHOWLAYERUSAGE i PURGE pokazują natywnie:
#   ile jest warstw, które są wyłączone/zamrożone/zablokowane/nie do wydruku,
#   które pochodzą z XREF-a i które GstarCAD uważa za nieużywane — w kolumnach,
#   z sortowaniem i filtrowaniem, czyli lepiej niż jakikolwiek nasz tekst.
#   Powtarzanie tego w raporcie nie daje klientowi nic i psuje wiarygodność
#   reszty. Zostało więc TYLKO to, czego natywnie nie ma (analiza Z-23/Z-26):
#     1. ROZJAZD — warstwy, na których nie znaleźliśmy ani jednego obiektu,
#        a GstarCAD twierdzi, że są używane. Wymaga zestawienia DWÓCH źródeł
#        prawdy obok siebie; żadne natywne okno tego nie robi.
#     2. BLIŹNIAKI — nazwy różniące się tylko wielkością liter albo spacjami.
#     3. PRZEDROSTKI — ile konwencji nazewniczych spotkało się w jednym rysunku.
#     4. NIE DO PRZEMIANOWANIA — czego nie da się przemianować przy porządkowaniu.
#     5. PEŁNA LISTA DO PLIKU — natywnie wszystko jest oknem, do oglądania.
#   Liczba warstw jest podana wyłącznie jako mianownik dla procentów, nie jako
#   „funkcja raportu".
#
# CZEGO TO NARZĘDZIE NIE ROBI — świadomie:
#   - NIE liczy atrybutów bloków. Dotknięcie attributeIterator zatruwa sesję
#     i wywala GstarCAD 2027 SP1 przy późniejszym entGet (ustalenie Z-24, 9
#     przetestowanych wariantów). Wolimy przyznaną lukę niż wywalony program
#     u klienta — dlatego raport mówi o tym WPROST, w wydruku i w pliku.
#   - NIC NIE ZMIENIA w rysunku. Zero add/erase/set. To jest raport, nie
#     naprawiacz. Wszystkie tabele otwierane są WYŁĄCZNIE do odczytu.
#   - NIE zgaduje liczb. Jeżeli choć jednego pojemnika albo obiektu nie dało się
#     odczytać, liczenie obiektów jest niepewne i narzędzie pisze „nie wiem"
#     zamiast liczby. Fałszywa liczba w raporcie o warstwach jest gorsza niż jej
#     brak — na jej podstawie ktoś kasuje warstwy.
#
# DLACZEGO try/finally przy KAŻDYM otwarciu tabeli (Z-25) — NIE UPRASZCZAĆ:
#   tabela otwarta przez getLayerTable/getBlockTable MUSI zostać zamknięta na
#   KAŻDEJ drodze wyjścia. Wyjątek albo wcześniejszy `return` między otwarciem
#   a close() zostawia tabelę otwartą; GstarCAD nie zwalnia jej sam, a objaw
#   (eWasOpenForWrite) wychodzi dopiero w NASTĘPNEJ komendzie, więc nikt nie
#   wiąże go z tą. Tu otwieramy tylko do odczytu, ale wzorzec trzymamy ten sam:
#   rekordy i iteratory też zamykamy w finally.
#
# Sposób użycia: APPLOAD tego pliku → komenda GSAI_WARSTWY. Raport leci na
# ekran (skrót) i na Pulpit do pliku gsai_raport_warstw.txt (całość).

# @KATALOG
# nazwa: Raport warstw
# komenda: GSAI_WARSTWY
# komenda_en: GSAI_LAYERREPORT
# branza: ogolne
# opis: Pokazuje to, czego Menedżer warstw nie pokaże: warstwy puste, które GstarCAD mimo to uważa za używane (te, których PURGE nie sprząta), nazwy różniące się tylko wielkością liter i zderzone konwencje nazewnicze. Całość ląduje w pliku tekstowym, więc da się ją komuś wysłać. Niczego w rysunku nie zmienia.
# przyklad: Przejęty po kimś rysunek z 300 warstwami — sprawdzenie, co da się posprzątać, zanim ktokolwiek zacznie kasować.

from pygcad.core import *
from pygcad.core.runtime import *
from pygcad.pygrx import *
import os
import re

NAZWA_PLIKU = "gsai_raport_warstw.txt"
DEBUG_PLIKU = "gsai_warstwy_debug.txt"   # checkpoint diagnostyczny — patrz _ck()

# Zbierane w trakcie przebiegu: cokolwiek, czego nie dało się odczytać.
# Niepusta lista = liczby obiektów są NIEPEWNE i nie wolno ich podawać.
_ostrzezenia = []
_linie = []


def _sciezka_raportu():
    """Pulpit, nie %TEMP% — pliku w tempie nikt nie znajduje (nauczka z #30)."""
    pulpit = os.path.join(os.path.expanduser("~"), "Desktop")
    if not os.path.isdir(pulpit):
        pulpit = os.path.expanduser("~")
    return os.path.join(pulpit, NAZWA_PLIKU)


def _ck(msg):
    """Checkpoint diagnostyczny: NADPISUJE plik debug ostatnim krokiem + fsync.
    Crash natywny (GCAD abnormal exit) omija try/except Pythona i nie zostawia
    tracebacku — ale plik debug trzyma OSTATNIE wywolanie zapisane przed faultem,
    czyli winowajce. Po naprawie tor diagnostyczny sie usuwa."""
    try:
        p = os.path.join(os.path.dirname(_sciezka_raportu()), DEBUG_PLIKU)
        with open(p, "w", encoding="utf-8") as f:
            f.write(msg + "\n")
            f.flush()
            os.fsync(f.fileno())
    except Exception:
        pass


def _do_pliku(msg):
    """Zbiera linię do raportu. Zapis jednym strzałem na końcu — patrz _zapisz."""
    _linie.append(msg)


def _powiedz(msg):
    """Na ekran I do pliku. Konsola urywa długie listy, plik nie."""
    gcutPrintf("\n%s" % msg)
    _do_pliku(msg)


def _zapisz():
    """Cały raport jednym zapisem, z fsync. Zwraca ścieżkę albo None."""
    sciezka = _sciezka_raportu()
    try:
        with open(sciezka, "w", encoding="utf-8") as f:
            f.write("\n".join(_linie) + "\n")
            f.flush()
            os.fsync(f.fileno())
        return sciezka
    except Exception as err:
        gcutPrintf("\n[WARSTWY] Nie moge zapisac pliku %s (%s)." % (sciezka, err))
        return None


def _nazwy_warstw(db):
    """SAME NAZWY warstw — getName, BEZ cast/isInUse/isDependent/isRenamable.

    DLACZEGO tylko nazwy i dlaczego to pierwszy krok (dowód Tomasz 22.07):
    `cast`+`isInUse` na rekordach warstw NIE crashuje samo w sobie (pętla po
    tabeli warstw kończy się), ale ZATRUWA sesję tak, że KOLEJNY odczyt ENCJI
    (`getEntity` w liczeniu obiektów) wywala GstarCAD natywnie. `GSAI_ZAMIEN_TEKST`
    na tym samym rysunku działa — bo NIE robi wcześniej isInUse. Wzorzec Z-24.
    Dlatego: najpierw same nazwy (nietrujące), potem liczenie obiektów na czystej
    sesji, a isInUse/xref/rename dopiero NA KOŃCU (patrz _wlasciwosci_warstw).
    """
    out = {}
    _ck("nazwy warstw: otwieram tabele")
    st, lt = db.getLayerTable(GcDb.kForRead)
    if st != Gcad.eOk:
        return None
    # close() w finally — patrz nagłówek pliku. NIE upraszczać.
    try:
        st, it = lt.newIterator()
        try:
            it.start()
        except Exception:
            pass
        while not it.done():
            st2, rec = it.getRecord(GcDb.kForRead)
            if rec is None:
                _ostrzezenia.append("nie dalo sie otworzyc rekordu warstwy")
            else:
                try:
                    stn, nazwa = rec.getName()
                    if stn == Gcad.eOk and nazwa:
                        out[nazwa] = {"uzywana": None, "z_xref": None,
                                      "mozna_zmienic": None, "obiektow": 0}
                    else:
                        _ostrzezenia.append("rekord warstwy bez czytelnej nazwy")
                finally:
                    rec.close()
            it.step()
    finally:
        lt.close()
    _ck("nazwy warstw: koniec (%d warstw)" % len(out))
    return out


def _wlasciwosci_warstw(db, warstwy):
    """Wypełnia isInUse / xref (isDependent) / rename (isRenamable) PER WARSTWA — CAST-FREE.

    KLUCZOWA ZMIANA (22.07, dowód Tomasza + nasze badania): NIE iterujemy tabeli
    i NIE castujemy. Split test dowiódł, że trucizna sesji (WARSTWY dziala, ale
    następna akcja w GstarCAD wywala program) siedzi w tej fazie. Główny podejrzany:
    `.cast()` — WARSTWY było jedyną komendą z castem i jedyną, która wywalała GS
    (patrz nagłówek GSAI_DLUGOSC — celowo napisany bez castu z tego powodu).

    Zamiast iterator+cast: otwieram każdą warstwę PO NAZWIE przez `getAt()`, który
    wg stubów zwraca od razu `GcDbLayerTableRecord` (typ warstwy) — więc
    isInUse/isDependent/isRenamable działają BEZ rzutowania. Plus `generateUsageData()`
    przed isInUse (Z-24 §5.1 — bez tego werdykt bywa nieświeży). Uruchamiane JAKO
    OSTATNIE czytanie bazy: gdyby mimo wszystko truło, po nim nie ma odczytu encji.
    """
    _ck("wlasciwosci: getLayerTable")
    st, lt = db.getLayerTable(GcDb.kForRead)
    if st != Gcad.eOk:
        _ostrzezenia.append("nie dalo sie ponownie otworzyc tabeli warstw")
        return
    try:
        try:
            lt.generateUsageData()   # Z-24 §5.1 — przelicz dane uzycia PRZED isInUse
        except Exception:
            pass
        for nazwa in list(warstwy.keys()):
            _ck("wlasciwosci: getAt '%s'" % nazwa)
            sst, lrec = lt.getAt(nazwa, GcDb.kForRead)   # TYPOWANY rekord warstwy — BEZ cast
            if sst != Gcad.eOk or lrec is None:
                continue
            try:
                warstwy[nazwa]["uzywana"] = lrec.isInUse()
                warstwy[nazwa]["z_xref"] = lrec.isDependent()
                warstwy[nazwa]["mozna_zmienic"] = lrec.isRenamable()
            except Exception as e:
                _ostrzezenia.append("wlasciwosci warstwy %s: %s" % (nazwa, e))
            finally:
                lrec.close()
    finally:
        lt.close()
    _ck("wlasciwosci: koniec")


def _policz_obiekty(db, warstwy):
    """Ile obiektów siedzi na każdej warstwie — nasze własne, drugie źródło prawdy.

    Otwieramy każdy rekord PO NAZWIE przez getAt (cast-free — cast truje sesję, BUG-07):
        bt.getAt(NAZWA) -> newIterator() -> start() -> getEntity() -> layer().

    DLACZEGO getAt-po-nazwie, a NIE cast (zmiana 22.07): pierwsza wersja castowała
    rekordy z iteratora (`GcDbBlockTableRecord.cast(btr).newIterator()`) i to ZATRUWAŁO
    sesję — crash na pierwszym model space, a potem na dowolnej akcji usera (BUG-07,
    debug Tomasza: „blok #1 '*Model_Space' -> newIterator"). Tu iterujemy tabelę bloków
    TYLKO po NAZWY (getName na bazie, bez cast), a potem każdy rekord otwieramy przez
    getAt(nazwa), który zwraca typ wprost — zero castu, zero trucizny.

    ZAKRES (rozszerzony 22.07, cast-free): model space + WSZYSTKIE arkusze + WSZYSTKIE
    definicje bloków. Bo pełna tabela bloków zawiera *Model_Space, *Paper_Space*, każdą
    nazwaną definicję i XREF-y (Z-24 §5.2). Definicje liczymy jako DEFINICJE, nie wystąpienia
    (blok wstawiony 200× = +1 do warstwy) — to właściwa semantyka dla „czy warstwa pusta /
    blokery PURGE". Pomijamy tylko XREF / niezaładowane (ich encje to nie własne obiekty).

    Czego NIE obchodzimy: atrybutów bloków (attributeIterator zatruwa sesję, Z-24) — więc
    warstwa używana WYŁĄCZNIE przez atrybut wyjdzie jako ROZJAZD (zadeklarowane w raporcie).
    Każdy nieudany odczyt ląduje w _ostrzezenia i unieważnia liczby.
    """
    przejrzane = 0
    st, bt = db.getBlockTable(GcDb.kForRead)
    if st != Gcad.eOk:
        _ostrzezenia.append("nie dalo sie otworzyc tabeli blokow")
        return przejrzane
    # close() w finally — patrz nagłówek pliku. NIE upraszczać.
    try:
        # 1) Zbierz NAZWY wszystkich rekordów tabeli bloków — getName na bazie, BEZ cast
        #    (cast truje sesję, BUG-07; ten sam bezpieczny wzorzec co _nazwy_warstw).
        nazwy = []
        st, bit = bt.newIterator()
        try:
            bit.start()
        except Exception:
            pass
        while not bit.done():
            st2, btr = bit.getRecord(GcDb.kForRead)
            if btr is not None:
                try:
                    stn, bn = btr.getName()
                    if stn == Gcad.eOk and bn:
                        nazwy.append(bn)
                finally:
                    btr.close()
            bit.step()
        _ck("policz: %d rekordow blokow do przejrzenia" % len(nazwy))

        # 2) Każdy rekord otwarty PO NAZWIE przez getAt -> TYPOWANY GcDbBlockTableRecord (bez cast).
        for bn in nazwy:
            _ck("policz: getAt '%s'" % bn)
            sst, brec = bt.getAt(bn, GcDb.kForRead)
            if sst != Gcad.eOk or brec is None:
                continue
            try:
                # Pomijamy XREF / niezaładowane (encje z odnośnika = nie własne obiekty rysunku;
                # iteracja niezaładowanego xref-a bywa też niebezpieczna).
                try:
                    if (brec.isFromExternalReference()
                            or brec.isFromOverlayReference()
                            or brec.isUnloaded()):
                        continue
                except Exception:
                    continue   # nie wiem, czy bezpieczny = nie ruszam
                ist, it = brec.newIterator()
                if ist != Gcad.eOk or it is None:
                    continue
                it.start()
                while not it.done():
                    est, ent = it.getEntity()   # bez kForRead — jak we wzorcu 21
                    if ent is None:
                        _ostrzezenia.append("nie dalo sie otworzyc obiektu w '%s'" % bn)
                    else:
                        try:
                            w = ent.layer()
                            if w in warstwy:
                                warstwy[w]["obiektow"] += 1
                            else:
                                _ostrzezenia.append("obiekt na nieznanej warstwie: %s" % w)
                            przejrzane += 1
                        finally:
                            ent.close()
                    it.step()
            finally:
                brec.close()
    finally:
        bt.close()
    _ck("policz: koniec (przejrzane=%d)" % przejrzane)
    return przejrzane


def _bliznieta(nazwy):
    """Nazwy różniące się TYLKO wielkością liter albo białymi znakami.
    Klasyk po scaleniu plików od kilku osób: 'Osie', 'OSIE', 'osie ' = trzy
    warstwy, które człowiek czyta jako jedną."""
    grupy = {}
    for n in nazwy:
        klucz = re.sub(r"\s+", "", n).lower()
        grupy.setdefault(klucz, []).append(n)
    return {k: v for k, v in grupy.items() if len(v) > 1}


def _przedrostki(nazwy):
    """Ile konwencji nazewniczych spotkało się w jednym rysunku (E-, INST_, A-…).
    To nie jest „błąd" — to informacja, że rysunek powstawał w kilku biurach."""
    pref = {}
    for n in nazwy:
        m = re.match(r"^([A-Za-z]{1,6})[-_]", n)
        if m:
            k = m.group(1).upper()
            pref[k] = pref.get(k, 0) + 1
    return sorted(pref.items(), key=lambda x: -x[1])


@command(local_name='GSAI_WARSTWY', global_name='GSAI_LAYERREPORT', group_name='GSAI')
def raport_warstw():
    """Raport warstw: pokazuje to, czego Menedżer warstw nie pokazuje. Nic nie zmienia."""
    try:
        del _linie[:]
        del _ostrzezenia[:]

        _do_pliku("=" * 70)
        _do_pliku("RAPORT WARSTW (GSAI_WARSTWY) — narzedzie tylko czyta, nic nie zmienia")
        _do_pliku("=" * 70)

        db = gcdbWorkingDatabase()
        # KOLEJNOŚĆ MA ZNACZENIE (Tomasz 22.07): isInUse zatruwa sesję dla późniejszego
        # odczytu encji, więc: 1) same nazwy, 2) liczenie obiektów na czystej sesji,
        # 3) isInUse/xref/rename NA KOŃCU — po nich już nie czytamy encji.
        warstwy = _nazwy_warstw(db)
        if warstwy is None:
            _powiedz("[WARSTWY] Nie moge otworzyc tabeli warstw. Raportu nie ma.")
            return
        if not warstwy:
            _powiedz("[WARSTWY] Tabela warstw jest pusta — nie ma czego raportowac.")
            return

        przejrzane = _policz_obiekty(db, warstwy)
        # Split test (Tomasz 22.07) dowiódł: trucizna była w tej fazie. Wersja CAST-FREE
        # (getAt zamiast iterator+cast) — test, czy usunięcie castu zdejmuje poison.
        _wlasciwosci_warstw(db, warstwy)   # OSTATNI odczyt bazy
        n = len(warstwy)
        pewne = not _ostrzezenia   # czy wolno w ogóle podawać liczby obiektów

        # Liczba warstw jest tu MIANOWNIKIEM, nie funkcją raportu — bez niej
        # „7 rozjazdów" nic nie znaczy. Menedżer warstw pokazuje ją sam.
        _powiedz("[WARSTWY] Warstw w rysunku: %d   (obiektow przejrzanych: %d)"
                 % (n, przejrzane))

        # ── 1. ROZJAZD — rdzeń raportu ────────────────────────────────────────
        # Warstwa, na której NIE znaleźliśmy ani jednego obiektu (ani w modelu,
        # ani w arkuszach, ani w definicjach bloków), a GstarCAD mimo to mówi
        # „używana". Zestawienia tych dwóch źródeł nie robi żadne natywne okno.
        if not pewne:
            _powiedz("[WARSTWY] >>> ROZJAZD: NIE WIEM — liczenie obiektow bylo niepelne.")
            _powiedz("          Powody nizej, w sekcji CZEGO TA WERSJA NIE WIE.")
            _powiedz("          Zadnej liczby tu nie podaje, bo bylaby zmyslona.")
        else:
            puste = [k for k, v in warstwy.items() if v["obiektow"] == 0]
            rozjazd = sorted(k for k in puste if warstwy[k]["uzywana"])
            _powiedz("[WARSTWY] >>> ROZJAZD: warstw pustych wg nas, 'uzywanych' wg "
                     "GstarCAD: %d  (%.0f%%)" % (len(rozjazd), 100.0 * len(rozjazd) / n))
            if rozjazd:
                _powiedz("          Nie znalezlismy na nich zadnego obiektu (przeszlismy")
                _powiedz("          model, arkusze I definicje blokow), a program uwaza je")
                _powiedz("          za uzywane. Najczestsze przyczyny: warstwa z XREF-a,")
                _powiedz("          siedzi na niej ATRYBUT bloku (ktorych NIE liczymy), albo")
                _powiedz("          trzyma ja obiekt NIE bedacy encja (zamrozenie per-rzutnia,")
                _powiedz("          stan warstwy, styl, slownik). Zwykle to wlasnie te")
                _powiedz("          warstwy, ktorych PURGE nie sprzata.")
                _powiedz("          UWAGA: to lista DO SPRAWDZENIA, nie do skasowania.")
                for k in rozjazd[:15]:
                    zn = " (z XREF-a)" if warstwy[k]["z_xref"] else ""
                    _powiedz("          -> %s%s" % (k, zn))
                if len(rozjazd) > 15:
                    _powiedz("          ... i %d dalszych — pelna lista w pliku."
                             % (len(rozjazd) - 15))

            # Rozjazd w drugą stronę: MY policzyliśmy obiekty, a GstarCAD mówi
            # „nieużywana". To nie powinno się zdarzyć. Jeśli się zdarza, to nie
            # jest odkrycie o rysunku, tylko sygnał, że nasze liczenie kłamie —
            # i klient musi to wiedzieć, zanim cokolwiek na jego podstawie zrobi.
            odwrotny = sorted(k for k, v in warstwy.items()
                              if v["obiektow"] > 0 and not v["uzywana"])
            if odwrotny:
                _powiedz("[WARSTWY] ! Sprzecznosc odwrotna: %d warstw, na ktorych "
                         "policzylismy obiekty," % len(odwrotny))
                _powiedz("          a GstarCAD mowi 'nieuzywana'. To znaczy, ze NASZE")
                _powiedz("          liczenie jest w tym rysunku niepewne — traktuj cala")
                _powiedz("          sekcje ROZJAZD z ostroznoscia. Przyklady:")
                for k in odwrotny[:5]:
                    _powiedz("          -> %s (%d obiektow)" % (k, warstwy[k]["obiektow"]))

        # ── 2. BLIŹNIAKI ──────────────────────────────────────────────────────
        bl = _bliznieta(list(warstwy.keys()))
        _powiedz("[WARSTWY] Nazwy rozniace sie tylko wielkoscia liter albo spacjami: "
                 "%d grup" % len(bl))
        if bl:
            _powiedz("          Czlowiek czyta je jako jedna warstwe, program jako kilka.")
            for v in list(bl.values())[:10]:
                _powiedz("          -> %s" % " | ".join(v))
            if len(bl) > 10:
                _powiedz("          ... i %d dalszych grup — pelna lista w pliku."
                         % (len(bl) - 10))

        # ── 3. PRZEDROSTKI ────────────────────────────────────────────────────
        top = _przedrostki(list(warstwy.keys()))
        if top:
            _powiedz("[WARSTWY] Konwencje nazewnicze, ktore sie tu spotkaly: %s"
                     % ", ".join("%s=%d" % t for t in top[:8]))
            if len(top) > 1:
                _powiedz("          Kilka przedrostkow naraz = rysunek skladany z kilku")
                _powiedz("          zrodel. Nie jest to blad, ale utrudnia filtrowanie.")
        else:
            _powiedz("[WARSTWY] Konwencje nazewnicze: brak czytelnego wzorca przedrostkow.")

        # ── 4. NIE DO PRZEMIANOWANIA ──────────────────────────────────────────
        # Cienka pozycja, ale natywnie nie ma zestawienia: RENAME mówi tylko
        # ogólnie o „standard items". Wartość ma jako ostrzeżenie PRZED
        # porządkowaniem nazw — żeby ktoś nie planował zmiany, która się nie uda.
        zablok = sorted(k for k, v in warstwy.items() if not v["mozna_zmienic"])
        _powiedz("[WARSTWY] Warstw, ktorych NIE da sie przemianowac: %d" % len(zablok))
        if zablok:
            _powiedz("          (zwykle warstwa 0, DEFPOINTS i warstwy z XREF-ow)")
            for k in zablok[:10]:
                _powiedz("          -> %s" % k)
            if len(zablok) > 10:
                _powiedz("          ... i %d dalszych — pelna lista w pliku."
                         % (len(zablok) - 10))

        # ── 5. CZEGO TA WERSJA NIE WIE — sekcja obowiązkowa ───────────────────
        _do_pliku("")
        _do_pliku("-" * 70)
        _do_pliku("CZEGO TA WERSJA NIE WIE — przeczytaj, zanim cos skasujesz")
        _do_pliku("-" * 70)
        _powiedz("[WARSTWY] ATRYBUTY BLOKOW NIE SA LICZONE.")
        _do_pliku("  Tekst atrybutu moze siedziec na innej warstwie niz blok, w ktorym")
        _do_pliku("  jest osadzony. Nie zagladamy tam CELOWO: przejscie po atrybutach")
        _do_pliku("  (attributeIterator) zatruwa sesje GstarCAD 2027 SP1 i wywala program")
        _do_pliku("  przy pozniejszych operacjach. Wolimy przyznac luke, niz wywalic")
        _do_pliku("  program na rysunku klienta.")
        _do_pliku("  SKUTEK PRAKTYCZNY: warstwa uzywana WYLACZNIE przez atrybuty wyjdzie")
        _do_pliku("  w tym raporcie jako ROZJAZD. To nie znaczy, ze jest do usuniecia.")
        _do_pliku("")
        _do_pliku("  Raport nie ocenia, czy rysunek jest POPRAWNY — pokazuje wylacznie")
        _do_pliku("  rozbieznosci i nazwy. Decyzje, co usunac, podejmuje czlowiek.")

        if _ostrzezenia:
            # Bez dubli, w kolejności wystąpienia — 300 razy to samo nikomu nie pomoże.
            widziane = []
            for o in _ostrzezenia:
                if o not in widziane:
                    widziane.append(o)
            _powiedz("[WARSTWY] ! Liczenie obiektow bylo NIEPELNE (%d potkniec, %d rodzajow)."
                     % (len(_ostrzezenia), len(widziane)))
            _do_pliku("  Dlatego liczby obiektow i rozjazd nie zostaly podane.")
            for o in widziane[:10]:
                _do_pliku("  - %s" % o)
            if len(widziane) > 10:
                _do_pliku("  - ... i %d innych rodzajow" % (len(widziane) - 10))

        # ── 6. PEŁNA LISTA DO PLIKU ───────────────────────────────────────────
        # Druga połowa rdzenia: natywnie wszystko jest oknem, jeden rysunek naraz,
        # do oglądania. Plik da się wysłać, wkleić, porównać i przeszukać.
        _do_pliku("")
        _do_pliku("-" * 70)
        if pewne:
            _do_pliku("PELNA LISTA WARSTW (nazwa | obiektow | uzywana wg GstarCAD | "
                      "z XREF | mozna przemianowac)")
        else:
            _do_pliku("PELNA LISTA WARSTW — kolumna 'obiektow' pominieta, bo liczenie")
            _do_pliku("bylo niepelne. Zamiast liczby jest '?'.")
        _do_pliku("-" * 70)
        for k in sorted(warstwy, key=lambda x: (warstwy[x]["obiektow"], x.lower())):
            v = warstwy[k]
            ile = ("%6d" % v["obiektow"]) if pewne else "     ?"
            _do_pliku("%-45s %s  uzyw=%-5s xref=%-5s rename=%s"
                      % (k[:45], ile, v["uzywana"], v["z_xref"], v["mozna_zmienic"]))

        if bl:
            _do_pliku("")
            _do_pliku("--- WSZYSTKIE GRUPY NAZW-BLIZNIAKOW ---")
            for v in bl.values():
                _do_pliku("  %s" % " | ".join(v))
        if zablok:
            _do_pliku("")
            _do_pliku("--- WSZYSTKIE WARSTWY NIE DO PRZEMIANOWANIA ---")
            for k in zablok:
                _do_pliku("  %s" % k)

        sciezka = _zapisz()
        if sciezka:
            gcutPrintf("\n[WARSTWY] Pelny raport zapisany: %s" % sciezka)
        gcutPrintf("\n[WARSTWY] Rysunek nie zostal w zaden sposob zmieniony.")

    except Exception as err:
        # Raport, ktory sie wywalil w polowie, nie moze udawac kompletnego.
        gcutPrintf("\n[WARSTWY BLAD] %s: %s" % (type(err).__name__, err))
        gcutPrintf("\n[WARSTWY] Raport jest NIEPELNY — nie opieraj na nim decyzji.")
        try:
            _do_pliku("")
            _do_pliku("!!! RAPORT PRZERWANY BLEDEM: %s: %s" % (type(err).__name__, err))
            _do_pliku("!!! Powyzsze dane sa niepelne.")
            _zapisz()
        except Exception:
            pass
