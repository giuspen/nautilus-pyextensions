#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""This module adds a menu item to the nautilus right-click menu which allows to add
   all the selected files to the Audacious Playlist just through the right-clicking"""

#   add-to-audacious-playlist.py version 3.2
#
#   Copyright 2008-2013 Giuseppe Penone <giuspen@gmail.com>
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
import urllib, subprocess, re
import locale, gettext

APP_NAME = "nautilus-pyextensions"
LOCALE_PATH = "/usr/share/locale/"
ICONPATH = "/usr/share/icons/hicolor/scalable/apps/audacious.svg"
EXTENSIONS_WHITELIST = [".mp3"]
# internationalization
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP_NAME, LOCALE_PATH)
gettext.textdomain(APP_NAME)
_ = gettext.gettext
# post internationalization code starts here


class AddToAudaciousPlaylist(GObject.GObject, Nautilus.MenuProvider):
    """Implements the 'Add To Audacious Playlist' extension to the nautilus right-click menu"""

    def __init__(self):
        """Nautilus crashes if a plugin doesn't implement the __init__ method"""
        try:
            factory = Gtk.IconFactory()
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(ICONPATH)
            iconset = Gtk.IconSet.new_from_pixbuf(pixbuf)
            factory.add("audacious", iconset)
            factory.add_default()
        except: pass

    def run(self, menu, source_path_list):
        """Runs the Adding of selected Audio file(s) to the Audacious Playlist"""
        subprocess.call("audacious -e " + " ".join(source_path_list) + " &", shell=True)

    def get_file_items(self, window, sel_items):
        """Adds the 'Add To Audacious Playlist' menu item to the Nautilus right-click menu,
           connects its 'activate' signal to the 'run' method passing the list of selected Audio items"""
        if len(sel_items) == 0: return
        if sel_items[0].is_directory() or sel_items[0].get_uri_scheme() != 'file':
            return
        source_path_list = []
        for sel_item in sel_items:
            uri_raw = sel_item.get_uri()
            if len(uri_raw) < 7: continue
            source_path = re.escape(urllib.unquote(uri_raw[7:]))
            for extension in EXTENSIONS_WHITELIST:
                if source_path.endswith(extension):
                    source_path_list.append(source_path)
                    break
            else:
                filetype = subprocess.Popen("file -i %s" % source_path, shell=True, stdout=subprocess.PIPE).communicate()[0]
                if "audio" in filetype\
                or "application/ogg" in filetype:
                    source_path_list.append(source_path)
        if source_path_list:
            item = Nautilus.MenuItem(name='NautilusPython::audacious',
                                     label=_('Add To Audacious Playlist'),
                                     tip=_('Add the selected Audio file(s) to the Audacious Playlist'),
                                     icon='audacious')
            item.connect('activate', self.run, source_path_list)
            return item,
