#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module adds a menu item to the nautilus right-click menu which allows to Open the Terminal
   on the Selected Folder/Current Directory at predefined Geometry just through the right-clicking"""

#   open-terminal-geometry.py version 1.2
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

import nautilus, urllib, os, subprocess
import locale, gettext

APP_NAME = "nautilus-pyextensions"
LOCALE_PATH = "/usr/share/locale/"
# internationalization
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP_NAME, LOCALE_PATH)
gettext.textdomain(APP_NAME)
_ = gettext.gettext
# post internationalization code starts here
GEOMETRY = "100x25"


class OpenTerminalGeometry(nautilus.MenuProvider):
    """Implements the 'Open Terminal Geometry' extension to the nautilus right-click menu"""

    def __init__(self):
        """Nautilus crashes if a plugin doesn't implement the __init__ method"""
        pass

    def run(self, menu, selected):
        """Runs the Open Terminal Geometry on the given Directory"""
        curr_dir = urllib.unquote(selected.get_uri()[7:])
        if os.path.isfile(curr_dir): curr_dir = os.path.dirname(curr_dir)
        bash_string = "gnome-terminal --geometry=" + GEOMETRY + " --working-directory='" + curr_dir + "' &"
        subprocess.call(bash_string, shell=True)

    def get_file_items(self, window, sel_items):
        """Adds the 'Open Terminal Geometry' menu item to the Nautilus right-click menu,
           connects its 'activate' signal to the 'run' method passing the selected Directory/File"""
        if len(sel_items) != 1 or sel_items[0].get_uri_scheme() != 'file': return
        item = nautilus.MenuItem('NautilusPython::terminal',
                                 _('Open Terminal Here'),
                                 _('Open the Terminal on the Current/Selected Directory') )
        item.set_property('icon', 'terminal')
        item.connect('activate', self.run, sel_items[0])
        return item,

    def get_background_items(self, window, current_directory):
        """Adds the 'Open Terminal Geometry' menu item to the Nautilus right-click menu,
           connects its 'activate' signal to the 'run' method passing the current Directory"""
        item = nautilus.MenuItem('NautilusPython::terminal',
                                 _('Open Terminal Here'),
                                 _('Open the Terminal on the Current Directory') )
        item.set_property('icon', 'terminal')
        item.connect('activate', self.run, current_directory)
        return item,
