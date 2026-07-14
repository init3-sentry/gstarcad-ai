# Modul do SKOMPILOWANIA przez Cython -> secret_demo.pyd (cp311-win_amd64).
# BRAMKA #2 ochrony: czy Cython .pyd potrafi wykonac logike i wywolac API GstarCAD.
#
# NAUCZKA (test Rafala 2026-07-14, LC/Win10): skompilowany/importowany modul NIE
# widzi API pygcad ani przez jawny import (ImportError: cannot import name), ani
# przez 'from ... import *' (import przechodzi, ale w czasie wywolania leci
# NameError: name 'gcdbWorkingDatabase' is not defined). Powod: pygcad wstrzykuje
# swoje nazwy tylko do namespace pliku APPLOAD-owanego, nie do importowanych
# podmodulow.
#
# ROZWIAZANIE: ten modul pygcada NIE importuje wcale. Loader (APPLOAD-owany, ma
# API przez 'import *') PRZEKAZUJE potrzebne funkcje do run(). Dzieki temu .pyd
# jest czysty, przenosny i niezalezny od mechanizmu wstrzykiwania nazw.


def run(gcdbWorkingDatabase, gcutPrintf):
    db = gcdbWorkingDatabase()   # dowod, ze skompilowany modul siega API GstarCAD
    gcutPrintf("\n=== secret_demo.pyd DZIALA: skompilowany Cython .pyd + API GstarCAD OK ===")
