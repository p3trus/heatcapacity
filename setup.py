#  -*- coding: utf-8 -*-
from setuptools import setup, find_packages

requires = ['future', 'slave']

try:
    import numpy
except ImportError:
    requires.append('numpy')

try:
    import scipy
except ImportError:
    requires.append('scipy')

desc = 'A small python package for heat capacity measurements and analysis.'

setup(
    name='heatcapacity',
    version=__import__('heatcapacity').__version__,
    author='Marco Halder',
    author_email='marco.halder@frm2.tum.de',
    license = 'BSD',
    url='https://github.com/p3trus/heatcapacity',
    description=desc,
    long_description=open('README.rst').read(),
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
)
