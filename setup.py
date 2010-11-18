#!/usr/bin/env python

# for linux install: "python setup.py install --prefix=/usr --exec-prefix=/usr -f"

from distutils.core import setup

import os, glob, sys, subprocess
import __builtin__
def _(transl_str):
   return transl_str
__builtin__._ = _
sys.path.append(os.path.join(os.getcwd(), "modules"))
import cons

data_files = [
                  ("share/icons/hicolor/scalable/apps", ["linux/nautilus-pyextensions.svg"] ),
                  ("share/applications", ["linux/nautilus-pyextensions.desktop"] ),
                  ("share/nautilus-pyextensions/glade", glob.glob("glade/*.*") ),
                  ("share/nautilus-pyextensions/modules", glob.glob("modules/*.py") ),
               ]

for lang in cons.AVAILABLE_LANGS:
   if lang in ["default", "en"]: continue
   data_files.append( ("share/locale/%s/LC_MESSAGES" % lang, ["locale/%s/LC_MESSAGES/nautilus-pyextensions.mo" % lang] ) )

setup(
   name = "Nautilus PyExtensions",
   description = "Nautilus Python Extensions Handler",
   long_description = "A Graphical Handler of the Nautilus File Manager Python Extensions, Including some Useful PyExtensions",
   version = cons.VERSION,
   author = "Giuseppe Penone",
   author_email = "giuspen@gmail.com",
   url = "http://www.giuspen.com/nautilus-pyextensions/",
   license = "GPL",
   scripts = ["nautilus-pyextensions"],
   data_files = data_files
)
