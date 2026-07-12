# Wzorcowa komenda 26 — AUDYT OSI Z: wykryj i ZAZNACZ obiekty „uciekłe" poza Z=0.
#
# Zamyka pozycję #11 z raportu Roberta. Realny ból geodety/projektanta 2D: część
# obiektów ma współrzędną Z różną od zera (import z innego programu, blok wstawiony
# na wysokości, błąd rysowania). W rzucie z góry ich NIE WIDAĆ, ale kursor „łapie" je
# na wysokości Z → pomiary (odległości/pola) wychodzą błędne. GstarCAD sam tego nie
# sygnalizuje i nie da się ich zwyczajnie znaleźć — bo są niewidoczne.
#
# Co robi ta komenda: przechodzi cały model, liczy Z każdej encji i ZAZNACZA
# (pickfirst, z uchwytami) te poza płaszczyzną 2D. Użytkownik od razu WIDZI, które to,
# i ma je w gotowej selekcji — może je obejrzeć, usunąć, albo spłaszczyć.
#
# Podział ról (WAŻNE — native-first, patrz README §REGUŁA #0):
#   - SPŁASZCZANIE Z→0 robi NATYWNY `FLATTEN` (Express Tools) — NIE reimplementujemy go.
#   - Nasza unikalna wartość: FLATTEN wymaga SELEKCJI obiektów, a użytkownik NIE WIE,
#     które uciekły w Z (są niewidoczne). My je ZNAJDUJEMY i ZAZNACZAMY (pickfirst).
#   - ZWERYFIKOWANE END-TO-END na LC 2026-07-12: po AUDYTZ wystarczy wpisać `FLATTEN` —
#     bierze naszą selekcję OD RĘKI (bez pytania „wybierz obiekt") i spłaszcza. Ponowny
#     AUDYTZ pokazuje „Czysto". Cały fix to DWIE komendy: AUDYTZ → FLATTEN.
#
# Jak działa detekcja (uniwersalna): getGeomExtents(ext) daje bounding-box KAŻDEJ encji
# bez znajomości typu; |Zmin|>tol lub |Zmax|>tol → obiekt poza 2D. Zmin≠Zmax = obiekt
# rozciągnięty w Z (prawdziwie 3D, np. linia ze spadkiem) — w raporcie widać to jako
# „Z od..do", żeby użytkownik wiedział, że spłaszczenie takiego to jego świadoma decyzja.
#
# Jak działa zaznaczanie (sprawdzone empirycznie na LC 2026-07-12): iterowana encja nie
# ma bezpośrednio „ename" potrzebnej selection setowi, więc most:
#   GcDbEntity -> getGcDbHandle().getIntoAsciiBuffer() (handle jako string)
#   -> gcdbHandEnt(handle, ename)  -> gcedSSAdd(ename, sset, sset)  [pusty sset = utwórz]
#   -> gcedSSSetFirst(sset, gds_name())  [2. arg MUSI być buforem, nie None] -> pickfirst.
#
# Sposób użycia: APPLOAD → AUDYTZ (zaznacza obiekty poza Z=0 + raport). Aby je spłaszczyć:
# wpisz `FLATTEN` — spłaszczy zaznaczone od ręki. (Albo obejrzyj / usuń; ESC = zdejmij uchwyty.)
#
# Konwencje domu: 3 importy, @command, try/except, Gcad.eOk dla bazy, RTNORM/status dla
# edytora, iteracja modelu jak wzorzec 12, idiom selection setu jak wzorzec 05.

from pygcad.core import *
from pygcad.core.runtime import *
from pygcad.pygrx import *

TOL_Z = 1e-6                 # poniżej tego traktujemy jako Z=0 (szum float)
MAX_LIST = 15               # ile pozycji wypisać szczegółowo w raporcie


@command(local_name='AUDYTZ')
def audytz():
    """Wykryj i zaznacz (uchwyty) obiekty poza płaszczyzną Z=0. Spłaszcza je natywny FLATTEN."""
    try:
        db = gcdbWorkingDatabase()
        status, bt = db.getBlockTable(GcDb.kForRead)
        if status != Gcad.eOk:
            gcutPrintf("\n[AUDYTZ] Nie mozna otworzyc tabeli blokow.")
            return
        status, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForRead)
        bt.close()
        if status != Gcad.eOk:
            gcutPrintf("\n[AUDYTZ] Nie mozna otworzyc modelu.")
            return
        status, it = ms.newIterator()
        if status != Gcad.eOk:
            ms.close()
            gcutPrintf("\n[AUDYTZ] Nie mozna utworzyc iteratora.")
            return

        sset = gds_name()        # pusty bufor selection setu (pusty = utwórz przy 1. SSAdd)
        total = 0
        poza = 0                 # ile obiektów poza Z=0 (wszystkie)
        dodane = 0               # ile realnie trafiło do selekcji
        szczegoly = []           # (klasa, zmin, zmax) do raportu, max MAX_LIST

        it.start()
        while not it.done():
            status, ent = it.getEntity()
            if status == Gcad.eOk and ent is not None:
                total += 1
                ext = GcDbExtents()
                st = ent.getGeomExtents(ext)
                if st == Gcad.eOk:
                    zmin = ext.minPoint().z
                    zmax = ext.maxPoint().z
                    if abs(zmin) > TOL_Z or abs(zmax) > TOL_Z:
                        poza += 1
                        try:
                            klasa = ent.isA().name()
                        except Exception:
                            klasa = "(nieznany)"
                        # most: handle -> ename -> selection set
                        try:
                            ok, hstr = ent.getGcDbHandle().getIntoAsciiBuffer()
                            if ok and hstr:
                                en = gds_name()
                                gcdbHandEnt(hstr, en)
                                gcedSSAdd(en, sset, sset)
                                dodane += 1
                        except Exception:
                            pass
                        if len(szczegoly) < MAX_LIST:
                            szczegoly.append((klasa, zmin, zmax))
                ent.close()
            it.step()
        ms.close()

        # raport + zaznaczenie
        gcutPrintf("\n=== AUDYT OSI Z ===")
        gcutPrintf("\nPrzeskanowano obiektow: %d" % total)
        if poza == 0:
            gcutPrintf("\nWszystko na plaszczyznie 2D (Z=0). Czysto.")
            return

        # ustaw pickfirst — obiekty dostaną uchwyty
        gcedSSSetFirst(sset, gds_name())

        gcutPrintf("\nOBIEKTY POZA Z=0: %d  (ZAZNACZONE — uchwyty w rysunku)" % poza)
        for klasa, zmin, zmax in szczegoly:
            if abs(zmin - zmax) < TOL_Z:
                gcutPrintf("\n  - %-24s Z=%.4f" % (klasa, zmin))
            else:
                gcutPrintf("\n  - %-24s Z od %.4f do %.4f  (3D)" % (klasa, zmin, zmax))
        if poza > MAX_LIST:
            gcutPrintf("\n  ... oraz %d wiecej." % (poza - MAX_LIST))
        gcutPrintf("\nAby SPLASZCZYC do Z=0: wpisz FLATTEN — splaszczy zaznaczone od reki. (Albo obejrzyj/usun.)")
        gcutPrintf("\n(ESC zdejmuje uchwyty. „Z od..do (3D)\" = obiekt celowo rozciagniety w Z — splaszczaj swiadomie.)")

    except Exception as err:
        gcutPrintf("\n[AUDYTZ BLAD] %s: %s" % (type(err).__name__, str(err)))
