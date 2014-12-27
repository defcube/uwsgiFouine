#!/usr/bin/env python
from distutils.core import setup
import imp
import os

CWD = os.path.dirname(__file__)
readme = open(
        os.path.join(CWD, 'README.rst')
    ).read()
uwsgifouinelib = imp.load_module(
    'uwsgifouinelib',
    *imp.find_module('uwsgifouinelib', [CWD])
)


setup(
    name='uwsgiFouine',
    version=uwsgifouinelib.__version__,
    author_email='gattster@gmail.com',
    author='Philip Gatt',
    py_modules=['uwsgifouinelib'],
    scripts=['uwsgiFouine'],
    description="A uwsgi log parser.",
    long_description=readme,
    url='http://github.com/defcube/uwsgiFouine',
    data_files=[('', ['README.rst'])],
    )
