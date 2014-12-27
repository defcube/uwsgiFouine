#!/usr/bin/env python
from distutils.core import setup
import os
readme = open('README.rst').read()

setup(
    name='uwsgiFouine',
    version='1.06',
    author_email='gattster@gmail.com',
    author='Philip Gatt',
    py_modules=['uwsgifouinelib'],
    entry_points = {
        'console_scripts': [
            'uwsgiFouine = uwsgifouinelib:main',
        ],
    },
    description="A uwsgi log parser.",
    long_description=readme,
    url='http://github.com/defcube/uwsgiFouine',
    data_files=[('', ['README.rst'])],
    )
