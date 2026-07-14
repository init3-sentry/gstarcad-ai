# Stub APPLOAD-owany: cienki OTWARTY wrapper @command; logika w skompilowanym secret_demo.pyd.
# Wzorzec ochrony (jak przy .pyc, ale .pyd = natywny, niedekompilowalny).
from pygcad.core.runtime import *
from pygcad.pygrx import *
import sys
_DIR = r"C:\Users\Public\gs-ai\szyfr-test"
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)
import secret_demo  # skompilowany .pyd


@command(local_name='TESTPYD')
def testPyd():
    secret_demo.run()
