#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module adds menu items to the Nemo right-click menu which allows to compare
   the selected files/folder using Kdiff3 (Diff and merge tool) just through the right-clicking"""

#   kdiff3-compare.py version 4.2
#
#   Copyright 2009-2019 Giuseppe Penone <giuspen@gmail.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#   MA 02110-1301, USA.

import gi
gi.require_version('Nemo', '3.0')
from gi.repository import Nemo, GObject, Gtk, GdkPixbuf
import urllib.parse, os, subprocess, re
import locale, gettext

APP_NAME = "nemo-pyextensions"
LOCALE_PATH = "/usr/share/locale/"
NAUPYEXT_KDIFF3 = 'NAUPYEXT_KDIFF3'
ICONPATH = "/usr/share/icons/hicolor/32x32/apps/kdiff3.png"
# internationalization
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP_NAME, LOCALE_PATH)
gettext.textdomain(APP_NAME)
_ = gettext.gettext
# post internationalization code starts here


class Kdiff3Actions(GObject.GObject, Nemo.MenuProvider):
    """Implements the 'Kdiff3 Compare' extension to the Nemo right-click menu"""

    def __init__(self):
        """Nemo crashes if a plugin doesn't implement the __init__ method"""
        try:
            factory = Gtk.IconFactory()
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(ICONPATH)
            iconset = Gtk.IconSet.new_from_pixbuf(pixbuf)
            factory.add("kdiff3", iconset)
            factory.add_default()
        except: pass

    def _run(self, menu, element_1, element_2):
        """Runs the Kdiff3 Comparison of selected files/folders"""
        subprocess.call("kdiff3 %s %s &" % (re.escape(element_1), re.escape(element_2)), shell=True)

    def _kdiff3_save(self, menu, element):
        """Save the File/Folder Path for Future Use"""
        os.environ[NAUPYEXT_KDIFF3] = element

    def _is_text_document(self, filepath):
        """The given filepath is a text document"""
        filetype = subprocess.Popen("file -i %s" % re.escape(filepath), shell=True, stdout=subprocess.PIPE).communicate()[0]
        return (b"text" in filetype or b"xml" in filetype)

    def get_file_items(self, window, sel_items):
        """Adds the 'Add To Audacious Playlist' menu item to the Nemo right-click menu,
           connects its 'activate' signal to the '_run' method passing the list of selected Audio items"""
        num_paths = len(sel_items)
        if num_paths == 0 or num_paths > 2: return
        uri_raw = sel_items[0].get_uri()
        if len(uri_raw) < 7: return
        element_1 = urllib.parse.unquote(uri_raw[7:])
        if num_paths == 2:
            uri_raw = sel_items[1].get_uri()
            if len(uri_raw) < 7: return
            element_2 = urllib.parse.unquote(uri_raw[7:])
            if os.path.isfile(element_1):
                if not os.path.isfile(element_2): return
                if not self._is_text_document(element_1): return
                if not self._is_text_document(element_2): return
            elif os.path.isdir(element_1):
                if not os.path.isdir(element_2): return
            else: return
            item = Nemo.MenuItem(name='Kdiff3::kdiff3',
                                     label=_('Kdiff3 Compare'),
                                     tip=_('Compare the selected Files/Folders using Kdiff3 (Diff and merge tool)'),
                                     icon='kdiff3')
            item.connect('activate', self._run, element_1, element_2)
            return item,
        # only one item selected
        if os.path.isfile(element_1) and not self._is_text_document(element_1):
            return
        # top menuitem
        top_menuitem = Nemo.MenuItem(name='Kdiff3::actions',
                                         label=_('Kdiff3 Actions'),
                                         tip=_('Kdiff3 (Diff and merge tool) Actions'),
                                         icon='kdiff3')
        # creation of submenus
        submenu = Nemo.Menu()
        top_menuitem.set_submenu(submenu)
        # submenu items save
        sub_menuitem_save = Nemo.MenuItem(name='Kdiff3::save',
                                              label=_('Save Path for Future Use'),
                                              tip=_('Save the Selected File/Dir Path for Future Use'),
                                              icon='gtk-save')
        sub_menuitem_save.connect('activate', self._kdiff3_save, element_1)
        submenu.append_item(sub_menuitem_save)
        # submenu items compare with saved
        stored_path = os.environ[NAUPYEXT_KDIFF3] if NAUPYEXT_KDIFF3 in os.environ else ""
        if stored_path and stored_path != element_1 and ( (os.path.isfile(stored_path) and os.path.isfile(element_1) ) or (os.path.isdir(stored_path) and os.path.isdir(element_1) ) ):
            sub_menuitem_compare_saved = Nemo.MenuItem(name='Kdiff3::compare_saved',
                                                           label=_('Compare with %s' % stored_path.replace("_", " ") ),
                                                           tip=_('Compare the Selected File/Dir with %s' % stored_path),
                                                           icon='gtk-execute')
            sub_menuitem_compare_saved.connect('activate', self._run, element_1, stored_path)
            submenu.append_item(sub_menuitem_compare_saved)
        return top_menuitem,
