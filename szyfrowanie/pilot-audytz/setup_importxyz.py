# python setup_importxyz.py build_ext --inplace  -> importxyz_logic.cp311-win_amd64.pyd
from setuptools import setup
from Cython.Build import cythonize

setup(ext_modules=cythonize("importxyz_logic.py", language_level=3))
