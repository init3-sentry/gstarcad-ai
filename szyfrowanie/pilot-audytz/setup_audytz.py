# Build: python setup_audytz.py build_ext --inplace  -> audytz_logic.cp311-win_amd64.pyd
from setuptools import setup
from Cython.Build import cythonize

setup(ext_modules=cythonize("audytz_logic.py", language_level=3))
