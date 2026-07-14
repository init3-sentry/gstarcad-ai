# Modul do SKOMPILOWANIA przez Cython -> secret_demo.pyd (cp311-win_amd64).
# BRAMKA #2 ochrony: czy Cython .pyd potrafi import pygcad i wywolac GcDb API w GstarCAD.
# Cython przy kompilacji NIE potrzebuje pygcad (importy rozwiazuja sie w runtime w GstarCAD).
#
# WAZNE: pygcad dziala TYLKO z 'from ... import *'. Jawny import po nazwie
# (from pygcad.core.runtime import gcutPrintf) wywala ImportError: cannot import
# name gcutPrintf w GstarCAD — potwierdzone Rafal, GstarCAD2027 PL, 2026-07-14
# (loader_secret.py z 'import *' przeszedl, ten plik z jawnym importem sie wywalil
# w tej samej sesji). Cala nasza biblioteka narzedzi tez uzywa 'import *'.
# Cython kompiluje 'import *' jako import runtime — build przechodzi bez problemu.
from pygcad.core.runtime import *


def run():
    db = gcdbWorkingDatabase()  # dowod ze skompilowany modul siega API
    gcutPrintf("\n=== secret_demo.pyd DZIALA — logika ze skompilowanego Cython .pyd + pygcad OK ===")
