#!/usr/bin/env python
'''
    This file is part of batti, a battery monitor for the system tray.
    Copyright (C) 2010  Arthur Spitzer

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import glob
import os
from distutils.core import setup
from src import Constants

#Create an array with all the images
ICONS = []
current_dir = os.getcwd()
icondir = './data/icons'
os.chdir(icondir)
png_paths = glob.glob("??x??/*")
svg_paths = glob.glob("scalable/*")
os.chdir(current_dir)
for filepath in png_paths:
    targetpath = os.path.join("share/icons/hicolor", filepath)
    sourcepath = "%s/%s/*.png" % (icondir, filepath)
    ICONS.append((targetpath, glob.glob(sourcepath)))
for filepath in svg_paths:
    targetpath = os.path.join("share/icons/hicolor/", filepath)
    sourcepath = "%s/%s/*.svg" % (icondir, filepath)
    ICONS.append((targetpath, glob.glob(sourcepath)))

setup(name = Constants.NAME,
    version = Constants.VERSION, 
    description = Constants.DESCRIPTION,
    author = Constants.AUTHOR,
    author_email = Constants.AUTHOR_EMAIL,
    url = Constants.URL,
    license = 'GNU GPL',
    platforms = 'Linux',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.5',
        'Topic :: System :: Hardware',
        'Topic :: Utilities',
    ],
    package_dir = {Constants.NAME: 'src'},
    packages = [Constants.NAME],
    scripts = [Constants.NAME],
    data_files = [
        ('share/applications/', ['data/%s.desktop' % Constants.NAME])
    ]+ICONS
)

