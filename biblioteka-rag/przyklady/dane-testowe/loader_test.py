# TEST BRAMKI #1 — czy Startup Suite AUTO-ładuje .py (bez APPLOAD za każdym razem).
#
# Procedura na LC:
#   1. APPLOAD -> ikona "Contents" (Startup Suite) -> Add -> wskaz TEN plik -> Close.
#   2. Zamknij i otworz GstarCAD.
#   3a. Przy starcie w linii polecen powinno mrugnac: [TMSys loader_test zaladowany].
#   3b. Wpisz komende TESTSTARTUP -> jesli odpowiada, to Startup Suite zaladowal .py SAM.
#
# Wynik:
#   - komenda dziala bez recznego APPLOAD  -> Startup Suite przyjmuje .py (prosciejszy autoload).
#   - "Nieznane polecenie" / brak mrugniecia -> Startup Suite NIE laduje .py; potrzebny
#     skompilowany loader (.grx/.NET) na kOnGscadStartup.

from pygcad.core.runtime import *
from pygcad.pygrx import *


@command(local_name='TESTSTARTUP')
def testStartup():
    gcutPrintf("\n=== TESTSTARTUP dziala — zaladowany (sprawdz czy BEZ recznego APPLOAD) ===")


# kod na poziomie modulu wykonuje sie przy zaladowaniu (import) -> sygnal auto-loadu przy starcie
gcutPrintf("\n[TMSys loader_test zaladowany]")
