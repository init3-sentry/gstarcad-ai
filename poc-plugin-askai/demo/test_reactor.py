# TEST LC: czy REAKTORY realnie odpalają w wiązaniu pygcad?
# Rdzeń pytania: czy pybind pozwala NADPISAĆ callback reaktora po stronie Pythona
# (trampoline) — bo od tego zależy cała klasa „program sam reaguje/ostrzega".
#
# Test: subklasa GcDbDatabaseReactor z nadpisanym objectAppended → rejestracja na
# bieżącej bazie → dodanie okręgu → jeśli callback się odpali, REAKTORY DZIAŁAJĄ.
#
# Odpalić przez APPLOAD. Szukać w konsoli: [REAKTOR] objectAppended ODPALIL!
from pygcad.core import *
from pygcad.pygrx import *

_stan = {"fired": 0}


class MojReaktor(GcDbDatabaseReactor):
    def __init__(self):
        GcDbDatabaseReactor.__init__(self)

    def objectAppended(self, dwg, dbObj):
        _stan["fired"] += 1
        try:
            klasa = dbObj.isA().name()
        except Exception:
            klasa = "?"
        try:
            gcutPrintf("\n[REAKTOR] objectAppended ODPALIL! obiekt=%s (licznik=%d)" % (klasa, _stan["fired"]))
        except Exception:
            pass


# GLOBALNA referencja — reaktor NIE może zostać zebrany przez GC (inaczej dangling ptr w C++)
_reaktor = MojReaktor()


def test_reactor():
    try:
        db = gcdbWorkingDatabase()
        st = db.addReactor(_reaktor)
        gcutPrintf("\n[REAKTOR] zarejestrowany na bazie (addReactor=%s). Dodaje okrag..." % str(st))

        status, bt = db.getBlockTable(GcDb.OpenMode.kForRead)
        status, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.OpenMode.kForWrite)
        bt.close()
        circ = GcDbCircle(GcGePoint3d(0, 0, 0), GcGeVector3d(0, 0, 1), 100)
        status, oid = ms.appendGcDbEntity(circ)
        circ.close()
        ms.close()

        if _stan["fired"] > 0:
            gcutPrintf("\n[REAKTOR] WYNIK: DZIALA — callback odpalil %d raz(y). Reaktory zyja w pygcad." % _stan["fired"])
        else:
            gcutPrintf("\n[REAKTOR] WYNIK: NIE odpalil. Reaktor zarejestrowany, ale Python-override nie jest wolany przez C++ (brak trampoline). Rysowanie samo dziala, reaktory - nie.")
        # sprzatanie: wyrejestruj (zeby nie zostawic reaktora na stale w sesji)
        try:
            db.removeReactor(_reaktor)
            gcutPrintf("\n[REAKTOR] wyrejestrowany.")
        except Exception:
            pass
    except Exception as err:
        gcutPrintf("\n[REAKTOR BLAD] %s: %s" % (type(err).__name__, str(err)))


test_reactor()
