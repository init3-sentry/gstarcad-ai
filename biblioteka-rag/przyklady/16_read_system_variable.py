# Wzorcowa komenda 16 — Odczyt zmiennej systemowej rysunku.
#
# Demonstruje odczyt zmiennych systemowych GstarCAD-a (SETVAR/GETVAR) z poziomu
# Pythona przez gcedGetVar + resbuf. Zmienne systemowe trzymają setki ustawień
# rysunku: aktualną warstwę (CLAYER), wielkość widoku (VIEWSIZE), tryb polilinii
# (PLINETYPE), jednostki, kolory itd. Wzorzec z oficjalnego samples elipsjig.py
# / przewodnika systemowego.
#
# Sposób użycia: APPLOAD, następnie POKAZ_USTAWIENIA. Komenda wypisze w command
# line kilka bieżących zmiennych systemowych.
#
# Konwencje (v2 przewodnika + elipsjig.py):
#   - rb = resbuf(); gcedGetVar("NAZWA", rb); wartość w rb.resval.<typ>
#   - typ wyniku zależy od zmiennej: rreal (liczba), rint (całkowita),
#     rstring (tekst), rpoint (punkt). Trzeba znać typ danej zmiennej.

from pygcad.core.runtime import *
from pygcad.pygrx import *


def _getRealVar(name):
    """Odczyt zmiennej systemowej typu rzeczywistego. Zwraca float albo None."""
    try:
        rb = resbuf()
        gcedGetVar(name, rb)
        return rb.resval.rreal
    except Exception:
        return None


def _getIntVar(name):
    """Odczyt zmiennej systemowej typu całkowitego. Zwraca int albo None."""
    try:
        rb = resbuf()
        gcedGetVar(name, rb)
        return rb.resval.rint
    except Exception:
        return None


def _getStrVar(name):
    """Odczyt zmiennej systemowej typu tekstowego. Zwraca str albo None."""
    try:
        rb = resbuf()
        gcedGetVar(name, rb)
        return rb.resval.rstring
    except Exception:
        return None


@command(local_name='POKAZ_USTAWIENIA')
def showSystemVariables():
    """Odczytuje i wypisuje wybrane zmienne systemowe bieżącego rysunku."""
    try:
        gcutPrintf("\n=== Ustawienia bieżącego rysunku ===")

        viewsize = _getRealVar("VIEWSIZE")
        gcutPrintf(f"\nVIEWSIZE (wysokość widoku):  {viewsize if viewsize is not None else '?'}")

        plinetype = _getIntVar("PLINETYPE")
        gcutPrintf(f"\nPLINETYPE (typ polilinii):   {plinetype if plinetype is not None else '?'}")

        clayer = _getStrVar("CLAYER")
        gcutPrintf(f"\nCLAYER (aktualna warstwa):   {clayer if clayer is not None else '?'}")

        # LTSCALE — skala typu linii (rzeczywista)
        ltscale = _getRealVar("LTSCALE")
        gcutPrintf(f"\nLTSCALE (skala linii):       {ltscale if ltscale is not None else '?'}")

    except Exception as err:
        gcutPrintf(f"\n[BŁĄD] przy odczycie zmiennych: {err}")
