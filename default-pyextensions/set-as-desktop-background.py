#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module adds a menu item to the nautilus right-click menu which allows to set
   as desktop background the selected image file just through the right-clicking"""

#   set-as-desktop-background.py version 1.2
#
#   Copyright 2009-2010 Giuseppe Penone <giuspen@gmail.com>
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

import gconf
import nautilus, urllib, subprocess, re
import locale, gettext

APP_NAME = "nautilus-pyextensions"
LOCALE_PATH = "/usr/share/locale/"
# internationalization
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP_NAME, LOCALE_PATH)
gettext.textdomain(APP_NAME)
_ = gettext.gettext
# post internationalization code starts here


class SetAsDesktopBackground(nautilus.MenuProvider):
    """Implements the 'Set As Desktop Background' extension to the nautilus right-click menu"""

    def __init__(self):
        """Nautilus crashes if a plugin doesn't implement the __init__ method"""
        self.gconf_client = gconf.client_get_default()

    def run(self, menu, source_path):
        """Runs the Adding of selected Image file as Desktop Background"""
        self.gconf_client.set_string("/desktop/gnome/background/picture_filename", source_path)

    def get_file_items(self, window, sel_items):
        """Adds the 'Set As Desktop Background' menu item to the Nautilus right-click menu,
           connects its 'activate' signal to the 'run' method passing the list of selected Image item"""
        if len(sel_items) != 1 or sel_items[0].is_directory() or sel_items[0].get_uri_scheme() != 'file':
            return
        source_path = urllib.unquote(sel_items[0].get_uri()[7:])
        filetype = subprocess.Popen("file -i %s" % re.escape(source_path), shell=True, stdout=subprocess.PIPE).communicate()[0]
        if "image" in filetype:
            item = nautilus.MenuItem('NautilusPython::preferences-desktop-wallpaper',
                                     _('Set As Desktop Background'),
                                     _('Set the selected Image file as Desktop Background') )
            item.set_property('icon', 'preferences-desktop-wallpaper')
            item.connect('activate', self.run, source_path)
            return item,
