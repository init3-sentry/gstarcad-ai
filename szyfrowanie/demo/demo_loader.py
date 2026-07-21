# demo_loader - otwarty loader (APPLOAD). import * daje API pygcad, przekazuje globals() do .pyd.
from pygcad.core import *
from pygcad.core.runtime import *
from pygcad.pygrx import *
import sys
import os

_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)
import demo_logic


@command(local_name="GSAI_DEMO", global_name="GSAI_DEMO", group_name="GSAI")
def demo():
    demo_logic.run(globals())
