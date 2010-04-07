#!/usr/bin/env python
from DistUtilsExtra.command import *
import glob
from distutils.core import setup

setup(name='batti',
      version="0.3",
      description='A battery monitor for the system tray',
      author='Arthur Spitzer',
      author_email='arthapex@gmail.com',
      url='http://code.google.com/p/batti-gtk',
      package_dir={'batti': 'src'},
      packages = ['batti'],
      scripts=['batti'],
      )
