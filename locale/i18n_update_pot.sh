#!/bin/sh

cd ..

intltool-extract --type=gettext/glade glade/nautilus-pyextensions.glade
intltool-extract --type=gettext/glade glade/nautilus-pyextensions_replace.glade

xgettext --language=Python --keyword=_ --keyword=N_ --output=locale/nautilus-pyextensions.pot modules/core.py modules/cons.py glade/nautilus-pyextensions.glade.h glade/nautilus-pyextensions_replace.glade.h default-pyextensions/add-to-audacious2-playlist.py default-pyextensions/meld-compare.py default-pyextensions/kdiff3-compare.py default-pyextensions/open-as-root.py default-pyextensions/open-terminal-geometry.py default-pyextensions/replace-in-filenames.py default-pyextensions/set-as-desktop-background.py
