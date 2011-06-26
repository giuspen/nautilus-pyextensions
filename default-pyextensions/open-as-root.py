#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module adds a menu item to the nautilus right-click menu which allows to
   open the selected file/folder as root user, so having administrator rights"""

#   open-as-root.py version 1.2
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

from gi.repository import Gtk
import nautilus, gconf, urllib, os, sys, subprocess, re
import locale, gettext

APP_NAME = "nautilus-pyextensions"
LOCALE_PATH = "/usr/share/locale/"
# internationalization
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP_NAME, LOCALE_PATH)
gettext.textdomain(APP_NAME)
_ = gettext.gettext
# post internationalization code starts here


def dialog_info(message):
    """Debug dialog"""
    dialog = Gtk.MessageDialog(type=Gtk.MessageType.INFO,
                               buttons=Gtk.ButtonsType.OK,
                               message_format=message)
    dialog.run()
    dialog.destroy()


class OpenAsRoot(nautilus.MenuProvider):
    """Implements the 'Open as Root' extension to the nautilus right-click menu"""

    def __init__(self):
        """Nautilus crashes if a plugin doesn't implement the __init__ method"""
        pass

    def run(self, menu, source_path):
        """Runs the Opening of the selected File/Folder as Root User"""
        subprocess.call("gksu gnome-open %s &" % source_path, shell=True)

    def get_file_items(self, window, sel_items):
        """Adds the 'Open as Root' menu item to the Nautilus right-click menu,
           connects its 'activate' signal to the 'run' method passing the selected File/Folder"""
        if len(sel_items) != 1 or sel_items[0].get_uri_scheme() != 'file': return
        source_path = urllib.unquote(sel_items[0].get_uri()[7:])
        item = nautilus.MenuItem('NautilusPython::gksu',
                                 _('Open as Root'),
                                 _('Open the selected File/Folder as Root User') )
        item.set_property('icon', 'gksu')
        item.connect('activate', self.run, re.escape(source_path))
        return item,
