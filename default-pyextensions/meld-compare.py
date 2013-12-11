#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""This module adds menu items to the nautilus right-click menu which allows to compare
   the selected files/folder using Meld (Diff and merge tool) just through the right-clicking"""

#   meld-compare.py version 3.1
#
#   Copyright 2009-2013 Giuseppe Penone <giuspen@gmail.com>
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

from gi.repository import Nautilus, GObject, Gtk, GdkPixbuf
import urllib, os, subprocess, re
import locale, gettext

APP_NAME = "nautilus-pyextensions"
LOCALE_PATH = "/usr/share/locale/"
NAUPYEXT_MELD = 'NAUPYEXT_MELD'
ICONPATH = "/usr/share/icons/hicolor/scalable/apps/meld.svg"
# internationalization
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP_NAME, LOCALE_PATH)
gettext.textdomain(APP_NAME)
_ = gettext.gettext
# post internationalization code starts here


class MeldActions(GObject.GObject, Nautilus.MenuProvider):
    """Implements the 'Meld Compare' extension to the nautilus right-click menu"""

    def __init__(self):
        """Nautilus crashes if a plugin doesn't implement the __init__ method"""
        try:
            factory = Gtk.IconFactory()
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(ICONPATH)
            iconset = Gtk.IconSet.new_from_pixbuf(pixbuf)
            factory.add("meld", iconset)
            factory.add_default()
        except: pass

    def run(self, menu, element_1, element_2):
        """Runs the Meld Comparison of selected files/folders"""
        subprocess.call("meld %s %s &" % (element_1, element_2), shell=True)

    def meld_save(self, menu, element):
        """Save the File/Folder Path for Future Use"""
        os.environ[NAUPYEXT_MELD] = element

    def get_file_items(self, window, sel_items):
        """Adds the 'Add To Audacious Playlist' menu item to the Nautilus right-click menu,
           connects its 'activate' signal to the 'run' method passing the list of selected Audio items"""
        num_paths = len(sel_items)
        if num_paths == 0 or num_paths > 2: return
        uri_raw = sel_items[0].get_uri()
        if len(uri_raw) < 7: return
        element_1 = urllib.unquote(uri_raw[7:])
        if num_paths == 2:
            uri_raw = sel_items[1].get_uri()
            if len(uri_raw) < 7: return
            element_2 = urllib.unquote(uri_raw[7:])
            if os.path.isfile(element_1):
                if not os.path.isfile(element_2): return
                element_1 = re.escape(element_1)
                filetype = subprocess.Popen("file -i %s" % element_1, shell=True, stdout=subprocess.PIPE).communicate()[0]
                if "text" not in filetype and "xml" not in filetype: return
                element_2 = re.escape(element_2)
                filetype = subprocess.Popen("file -i %s" % element_2, shell=True, stdout=subprocess.PIPE).communicate()[0]
                if "text" not in filetype and "xml" not in filetype: return
            elif os.path.isdir(element_1):
                if not os.path.isdir(element_2): return
                element_1 = re.escape(element_1)
                element_2 = re.escape(element_2)
            else: return
            item = Nautilus.MenuItem(name='Meld::meld',
                                     label=_('Meld Compare'),
                                     tip=_('Compare the selected Files/Folders using Meld (Diff and merge tool)'),
                                     icon='meld')
            item.connect('activate', self.run, element_1, element_2)
            return item,
        # only one item selected
        if os.path.isfile(element_1):
            filetype = subprocess.Popen("file -i %s" % re.escape(element_1), shell=True, stdout=subprocess.PIPE).communicate()[0]
            if "text" not in filetype and "xml" not in filetype: return
        # top menuitem
        top_menuitem = Nautilus.MenuItem(name='Meld::actions',
                                         label=_('Meld Actions'),
                                         tip=_('Meld (Diff and merge tool) Actions'),
                                         icon='meld')
        # creation of submenus
        submenu = Nautilus.Menu()
        top_menuitem.set_submenu(submenu)
        # submenu items save
        sub_menuitem_save = Nautilus.MenuItem(name='Meld::save',
                                              label=_('Save Path for Future Use'),
                                              tip=_('Save the Selected File/Dir Path for Future Use'),
                                              icon='gtk-save')
        sub_menuitem_save.connect('activate', self.meld_save, element_1)
        submenu.append_item(sub_menuitem_save)
        # submenu items compare with saved
        stored_path = os.environ[NAUPYEXT_MELD] if NAUPYEXT_MELD in os.environ else ""
        if stored_path and stored_path != element_1 and ( (os.path.isfile(stored_path) and os.path.isfile(element_1) ) or (os.path.isdir(stored_path) and os.path.isdir(element_1) ) ):
            sub_menuitem_compare_saved = Nautilus.MenuItem(name='Meld::compare_saved',
                                                           label=_('Compare with %s' % stored_path.replace("_", " ") ),
                                                           tip=_('Compare the Selected File/Dir with %s' % stored_path),
                                                           icon='gtk-execute')
            sub_menuitem_compare_saved.connect('activate', self.run, re.escape(element_1), re.escape(stored_path))
            submenu.append_item(sub_menuitem_compare_saved)
        return top_menuitem,
