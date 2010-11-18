#!/bin/sh

mkdir nautilus-pyextensions_pkg
cd nautilus-pyextensions_pkg
mkdir DEBIAN
mkdir usr
mkdir usr/bin
mkdir usr/share
mkdir usr/share/applications
mkdir -p usr/share/icons/hicolor/scalable/apps
mkdir usr/share/locale
mkdir usr/share/nautilus-pyextensions
mkdir usr/share/nautilus-pyextensions/default-pyextensions
mkdir usr/share/nautilus-pyextensions/glade
mkdir usr/share/nautilus-pyextensions/modules

cp ../deb/control DEBIAN/

cp ../nautilus-pyextensions usr/bin/

cp ../linux/nautilus-pyextensions.desktop usr/share/applications/

cp ../linux/nautilus-pyextensions.svg usr/share/icons/hicolor/scalable/apps/

cd ../locale
python i18n_po_to_mo.py
cd -
for dirname in ../locale/*
do
   if [ -d $dirname ]
   then
      cp -r $dirname usr/share/locale/
   fi
done

for filename in ../default-pyextensions/*.py
do
   cp $filename usr/share/nautilus-pyextensions/default-pyextensions/
done

for filename in ../glade/*.*
do
   cp $filename usr/share/nautilus-pyextensions/glade/
done

for filename in ../modules/*.py
do
   cp $filename usr/share/nautilus-pyextensions/modules/
done

cd ..
dpkg -b nautilus-pyextensions_pkg
rm -r nautilus-pyextensions_pkg
