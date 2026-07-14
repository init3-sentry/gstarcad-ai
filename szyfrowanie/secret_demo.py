# Modul do SKOMPILOWANIA przez Cython -> secret_demo.pyd (cp311-win_amd64).
# BRAMKA #2 ochrony: czy Cython .pyd potrafi import pygcad i wywolac GcDb API w GstarCAD.
# Cython przy kompilacji NIE potrzebuje pygcad (importy rozwiazuja sie w runtime w GstarCAD).
# Importy jawne (nie 'import *') — bezpieczniejsze dla Cythona.
from pygcad.core.runtime import gcutPrintf, gcdbWorkingDatabase


def run():
    db = gcdbWorkingDatabase()  # dowod ze skompilowany modul siega API
    gcutPrintf("\n=== secret_demo.pyd DZIALA — logika ze skompilowanego Cython .pyd + pygcad OK ===")
