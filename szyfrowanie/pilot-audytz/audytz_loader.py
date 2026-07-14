# -*- coding: utf-8 -*-
# Otwarty loader GSAI_AUDYTZ: cienki @command + import pygcad; logika w skompilowanym
# audytz_logic.pyd. Loader ma API przez 'import *' i przekazuje CALE globals() do logiki,
# ktora sama pygcada NIE importuje (patrz audytz_logic.py / README-cython.md).
from pygcad.core import *
from pygcad.core.runtime import *
from pygcad.pygrx import *
import sys

_DIR = r"C:\Users\Public\gs-ai\szyfr-test"
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)
import audytz_logic  # skompilowany .pyd


@command(local_name='GSAI_AUDYTZ', global_name='GSAI_AUDITZ', group_name='GSAI')
def audytz():
    audytz_logic.run(globals())
