# TEST LC krok 2: reaktor DOKUMENTU — „program sam reaguje na OTWARCIE/przełączenie rysunku".
# To jest mechanizm pełnej wizji #11 Roberta (GstarCAD sam ostrzega przy otwarciu, że coś
# jest w osi Z) — a szerzej cała klasa „coś dzieje się samo przy otwarciu".
#
# Reaktor bazy (objectAppended) już potwierdzony. Teraz reaktor DOKUMENTU:
# gcDocManagerPtr().addReactor(GcApDocManagerReactor z nadpisanym documentActivated).
#
# Użycie: APPLOAD tego pliku → komenda REAKTOR_ON → otwórz nowy rysunek (NEW) albo
# przełącz kartę rysunku → powinien pojawić się [DOC-REAKTOR]. Na koniec REAKTOR_OFF.
from pygcad.core import *
from pygcad.core.runtime import *
from pygcad.pygrx import *

_stan = {"fired": 0, "on": False}


class DocReaktor(GcApDocManagerReactor):
    def __init__(self):
        GcApDocManagerReactor.__init__(self)

    def documentActivated(self, doc):
        _stan["fired"] += 1
        try:
            gcutPrintf("\n[DOC-REAKTOR] documentActivated ODPALIL! (licznik=%d) — to moment otwarcia/przelaczenia rysunku. TU odpalilby sie skan osi Z."
                       % _stan["fired"])
        except Exception:
            pass


# Globalna referencja — reaktor musi zyc po zakonczeniu skryptu (inaczej dangling ptr w C++)
_docreaktor = DocReaktor()


@command(local_name='REAKTOR_ON')
def reaktor_on():
    try:
        dm = gcDocManagerPtr()
        dm.addReactor(_docreaktor)
        _stan["on"] = True
        gcutPrintf("\n[DOC-REAKTOR] zarejestrowany na menedzerze dokumentow.")
        gcutPrintf("\n[DOC-REAKTOR] TERAZ: otworz nowy rysunek (NEW) albo przelacz karte rysunku -> powinien wyskoczyc [DOC-REAKTOR] documentActivated. Na koniec: REAKTOR_OFF.")
    except Exception as err:
        gcutPrintf("\n[DOC-REAKTOR BLAD ON] %s: %s" % (type(err).__name__, str(err)))


@command(local_name='REAKTOR_OFF')
def reaktor_off():
    try:
        dm = gcDocManagerPtr()
        dm.removeReactor(_docreaktor)
        _stan["on"] = False
        gcutPrintf("\n[DOC-REAKTOR] wyrejestrowany. Odpalil sie lacznie %d raz(y)." % _stan["fired"])
    except Exception as err:
        gcutPrintf("\n[DOC-REAKTOR BLAD OFF] %s: %s" % (type(err).__name__, str(err)))
