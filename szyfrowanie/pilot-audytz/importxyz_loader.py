# -*- coding: utf-8 -*-
# Otwarty loader GSAI_XYZ: @command + import pygcad; logika w importxyz_logic.pyd.
from pygcad.core import *
from pygcad.core.runtime import *
from pygcad.pygrx import *
import sys

_DIR = r"C:\Users\Public\gs-ai\szyfr-test"
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)
import importxyz_logic  # skompilowany .pyd


@command(local_name='GSAI_XYZ', global_name='GSAI_XYZ', group_name='GSAI')
def importxyz():
    importxyz_logic.run(globals())
