#!/bin/sh

cd ..

intltool-extract --type=gettext/glade glade/caja-pyextensions.glade

xgettext --language=Python --from-code=utf-8 --keyword=_ --keyword=N_ --output=locale/caja-pyextensions.pot modules/core.py modules/cons.py glade/caja-pyextensions.glade.h default-pyextensions/add-to-audacious-playlist.py default-pyextensions/meld-compare.py default-pyextensions/kdiff3-compare.py default-pyextensions/open-as-root.py default-pyextensions/open-terminal-here.py default-pyextensions/replace-in-filenames.py
