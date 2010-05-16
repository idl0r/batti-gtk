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
import sys
from distutils.core import setup
from distutils.command.install_data import install_data
from distutils.command.build import build
from distutils.dep_util import newer
from distutils.log import info
from subprocess import call
from src import Constants

PO_DIR = 'po'
MO_DIR = os.path.join('build', 'mo')
ICON_DIR = os.path.join("data", "icons")

#Create an array with all the images
ICONS = []
current_dir = os.getcwd()
os.chdir(ICON_DIR)
png_paths = glob.glob("??x??/*")
svg_paths = glob.glob("scalable/*")
os.chdir(current_dir)
for filepath in png_paths:
    targetpath = os.path.join("share/icons/hicolor", filepath)
    sourcepath = "%s/%s/*.png" % (ICON_DIR, filepath)
    ICONS.append((targetpath, glob.glob(sourcepath)))
for filepath in svg_paths:
    targetpath = os.path.join("share/icons/hicolor/", filepath)
    sourcepath = "%s/%s/*.svg" % (ICON_DIR, filepath)
    ICONS.append((targetpath, glob.glob(sourcepath)))
    
    
class BuildLocales(build):
  def run(self):
    build.run(self)

    for po in glob.glob(os.path.join(PO_DIR, '*.po')):
      lang = os.path.basename(po[:-3])
      mo = os.path.join(MO_DIR, lang, Constants.NAME + '.mo')

      directory = os.path.dirname(mo)
      if not os.path.exists(directory):
        os.makedirs(directory)

      if newer(po, mo):
        info('compiling %s -> %s' % (po, mo))
        try:
          rc = call(['msgfmt', po, '-o', mo])
          if rc != 0:
            raise Warning, "msgfmt returned %d" % rc
        except Exception, e:
          print "Building gettext files failed."
          print "%s: %s" % (type(e), str(e))
          sys.exit(1)


class InstallLocales(install_data):
  def run(self):
    self.data_files.extend(self._find_mo_files())
    install_data.run(self)

  def _find_mo_files(self):
    data_files = []
    for mo in glob.glob(os.path.join(MO_DIR, '*', Constants.NAME + '.mo')):
        lang = os.path.basename(os.path.dirname(mo))
        dest = os.path.join('share', 'locale', lang, 'LC_MESSAGES')
        data_files.append((dest, [mo]))
    return data_files



setup(name = Constants.NAME,
    version = Constants.VERSION, 
    description = Constants.DESCRIPTION,
    author = Constants.AUTHOR,
    author_email = Constants.AUTHOR_EMAIL,
    url = Constants.URL,
    license = 'GNU GPLv2',
    platforms = ['Linux'],
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
    cmdclass = {'build': BuildLocales, 'install_data': InstallLocales},
    data_files = [
        ('share/applications/', ['data/%s.desktop' % Constants.NAME])
    ]+ICONS
)

