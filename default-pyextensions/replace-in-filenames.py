#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""This module adds a menu item to the nautilus right-click menu which allows to Replace a String
   with another one in all Current/Selected Directory Filenames just through the right-clicking"""

#   replace-in-filenames.py version 3.1
#
#   Copyright 2011-2013 Giuseppe Penone <giuspen@gmail.com>
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

from gi.repository import Nautilus, GObject, Gtk
import urllib, os
import locale, gettext

APP_NAME = "nautilus-pyextensions"
LOCALE_PATH = "/usr/share/locale/"
# internationalization
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP_NAME, LOCALE_PATH)
gettext.textdomain(APP_NAME)
_ = gettext.gettext
# post internationalization code starts here


class ReplaceInFilenames(GObject.GObject, Nautilus.MenuProvider):
    """Implements the 'Replace in Filenames' extension to the nautilus right-click menu"""

    def __init__(self):
        """Nautilus crashes if a plugin doesn't implement the __init__ method"""
        pass

    def run(self, menu, selected):
        """Runs the Replace in Filenames on the given Directory"""
        uri_raw = selected.get_uri()
        if len(uri_raw) < 7: return
        dialog = Gtk.Dialog(title=_("Replace in Filenames"),
                            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                                     Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
        dialog.set_position(Gtk.WindowPosition.CENTER)
        entry_find = Gtk.Entry()
        entry_replace = Gtk.Entry()
        frame_find = Gtk.Frame(label="<b>"+_("Replace...")+"</b>")
        frame_find.get_label_widget().set_use_markup(True)
        frame_find.add(entry_find)
        frame_replace = Gtk.Frame(label="<b>"+_("...with")+"</b>")
        frame_replace.get_label_widget().set_use_markup(True)
        frame_replace.add(entry_replace)
        content_area = dialog.get_content_area()
        content_area.pack_start(frame_find, True, True, 0)
        content_area.pack_start(frame_replace, True, True, 0)
        content_area.show_all()
        response = dialog.run()
        dialog.hide()
        if response != Gtk.ResponseType.ACCEPT: return
        replace_from = entry_find.get_text()
        replace_to = entry_replace.get_text()
        if uri_raw.startswith("smb"):
            import smbc
            curr_dir = urllib.unquote(uri_raw)
            context = smbc.Context()
            dir_obj = context.opendir(curr_dir)
            dirent_objs = dir_obj.getdents()
            for dirent_obj in dirent_objs:
                if dirent_obj.smbc_type == 8:
                    old_name = dirent_obj.name
                    old_uri = os.path.join(curr_dir, old_name)
                    new_uri = os.path.join(curr_dir, old_name.replace(replace_from, replace_to))
                    if new_uri != old_uri:
                        context.rename(old_uri, new_uri)
        else:
            curr_dir = urllib.unquote(uri_raw[7:])
            if os.path.isfile(curr_dir): curr_dir = os.path.dirname(curr_dir)
            for old_name in os.listdir(curr_dir):
                old_filename = os.path.join(curr_dir, old_name)
                if os.path.isfile(old_filename):
                    new_name = old_name.replace(replace_from, replace_to)
                    if new_name != old_name:
                        os.rename(old_filename, os.path.join(curr_dir, new_name))

    def get_file_items(self, window, sel_items):
        """Adds the 'Replace in Filenames' menu item to the Nautilus right-click menu,
           connects its 'activate' signal to the 'run' method passing the selected Directory/File"""
        if len(sel_items) != 1 or sel_items[0].get_uri_scheme() not in ['file', 'smb']: return
        item = Nautilus.MenuItem(name='NautilusPython::gtk-find-and-replace',
                                 label=_('Replace in Filenames'),
                                 tip=_('Replace in Filenames of the Current/Selected Directory'),
                                 icon='gtk-find-and-replace')
        item.connect('activate', self.run, sel_items[0])
        return item,

    def get_background_items(self, window, current_directory):
        """Adds the 'Replace in Filenames' menu item to the Nautilus right-click menu,
           connects its 'activate' signal to the 'run' method passing the current Directory"""
        item = Nautilus.MenuItem(name='NautilusPython::gtk-find-and-replace',
                                 label=_('Replace in Filenames'),
                                 tip=_('Replace in Filenames of the Current Directory'),
                                 icon='gtk-find-and-replace')
        item.connect('activate', self.run, current_directory)
        return item,
