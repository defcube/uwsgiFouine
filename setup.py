#!/usr/bin/env python
from distutils.core import setup

setup(name='uwsgiFouine',
      version='1.0',
      author_email='gattster@gmail.com',
      author='Philip Gatt',
      py_modules=['uwsgifouinelib'],
      #py_modules=[''],
      scripts=['uwsgiFouine'],
      description = "A uwsgi log parser. Call uwsgiFouine with a uswgi log " \
                    "file, and you will be given reports telling you where " \
                    "uwsgi is spending it's time. Inspired by pgFouine, a " \
                    "postgres log analyser."
      )
