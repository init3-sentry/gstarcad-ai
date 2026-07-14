# Build .pyd: python setup.py build_ext --inplace  -> secret_demo.cp311-win_amd64.pyd
from setuptools import setup
from Cython.Build import cythonize

setup(ext_modules=cythonize("secret_demo.py", language_level=3))
