#!/usr/bin/env python

#from DistUtilsExtra.command import *
import glob
import os
from distutils.core import setup
from src import BatteryMonitor

#Create an array with all the images
ICONS = []
current_dir = os.getcwd()
icondir = './data/icons'
os.chdir(icondir)
png_paths = glob.glob("??x??/*")
svg_paths = glob.glob("scalable/*")
os.chdir(current_dir)
print png_paths
for filepath in png_paths:
    targetpath = os.path.join("share/icons/hicolor", filepath)
    sourcepath = "%s/%s/*.png" % (icondir, filepath)
    ICONS.append((targetpath, glob.glob(sourcepath)))
for filepath in svg_paths:
    targetpath = os.path.join("share/icons/hicolor/", filepath)
    sourcepath = "%s/%s/*.svg" % (icondir, filepath)
    ICONS.append((targetpath, glob.glob(sourcepath)))
print ICONS

setup(name = BatteryMonitor.NAME,
    version = BatteryMonitor.VERSION, 
    description = BatteryMonitor.DESCRIPTION,
    author = BatteryMonitor.AUTHOR,
    author_email = BatteryMonitor.AUTHOR_EMAIL,
    url = BatteryMonitor.URL,
    license = 'GNU GPL',
    platforms = 'linux',
    package_dir = {BatteryMonitor.NAME: 'src'},
    packages = [BatteryMonitor.NAME],
    scripts = [BatteryMonitor.NAME],
    data_files = [
        ('share/applications/', ['data/batti.desktop'])
    ]+ICONS
)

