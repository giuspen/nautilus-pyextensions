#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module adds a menu item to the nautilus right-click menu which allows to Replace a String
   with another one in all Current/Selected Directory Filenames just through the right-clicking"""

#   replace-in-filenames.py version 2.0
#
#   Copyright 2011 Giuseppe Penone <giuspen@gmail.com>
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

import gtk
import nautilus, urllib, os
import locale, gettext

APP_NAME = "nautilus-pyextensions"
LOCALE_PATH = "/usr/share/locale/"
# internationalization
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP_NAME, LOCALE_PATH)
gettext.textdomain(APP_NAME)
_ = gettext.gettext
# post internationalization code starts here
GLADE_PATH = "/usr/share/nautilus-pyextensions/glade/nautilus-pyextensions_replace.glade"


class GladeWidgetsWrapper:
    """Handles the retrieval of glade widgets"""

    def __init__(self, glade_file_path, gui_instance):
        try:
            self.glade_widgets = gtk.Builder()
            self.glade_widgets.set_translation_domain(APP_NAME)
            self.glade_widgets.add_from_file(glade_file_path)
            self.glade_widgets.connect_signals(gui_instance)
        except: print "Failed to load the glade file"

    def __getitem__(self, key):
        """Gives us the ability to do: wrapper['widget_name'].action()"""
        return self.glade_widgets.get_object(key)

    def __getattr__(self, attr):
        """Gives us the ability to do: wrapper.widget_name.action()"""
        new_widget = self.glade_widgets.get_object(attr)
        if new_widget is None: raise AttributeError, 'Widget %r not found' % attr
        setattr(self, attr, new_widget)
        return new_widget


class ReplaceInFilenames(nautilus.MenuProvider):
    """Implements the 'Replace in Filenames' extension to the nautilus right-click menu"""

    def __init__(self):
        """Nautilus crashes if a plugin doesn't implement the __init__ method"""
        pass

    def run(self, menu, selected):
        """Runs the Replace in Filenames on the given Directory"""
        uri_raw = selected.get_uri()
        if len(uri_raw) < 7: return
        curr_dir = urllib.unquote(uri_raw[7:])
        if os.path.isfile(curr_dir): curr_dir = os.path.dirname(curr_dir)
        self.glade = GladeWidgetsWrapper(GLADE_PATH, self)
        self.glade.replacedialog.connect('key_press_event', self.on_key_press)
        response = self.glade.replacedialog.run()
        self.glade.replacedialog.hide()
        if response != 1: return
        replace_from = self.glade.entry_replace_from.get_text()
        replace_to = self.glade.entry_replace_to.get_text()
        for old_name in os.listdir(curr_dir):
            old_filename = os.path.join(curr_dir, old_name)
            if os.path.isfile(old_filename):
                new_name = old_name.replace(replace_from, replace_to)
                if new_name != old_name:
                    os.rename(old_filename, os.path.join(curr_dir, new_name))

    def on_key_press(self, widget, event):
        """Catches AnchorHandle Dialog key presses"""
        keyname = gtk.gdk.keyval_name(event.keyval)
        if keyname == "Return": self.glade.replace_button_ok.clicked()

    def get_file_items(self, window, sel_items):
        """Adds the 'Replace in Filenames' menu item to the Nautilus right-click menu,
           connects its 'activate' signal to the 'run' method passing the selected Directory/File"""
        if len(sel_items) != 1 or sel_items[0].get_uri_scheme() != 'file': return
        item = nautilus.MenuItem('NautilusPython::gtk-find-and-replace',
                                 _('Replace in Filenames'),
                                 _('Replace in Filenames of the Current/Selected Directory') )
        item.set_property('icon', 'gtk-find-and-replace')
        item.connect('activate', self.run, sel_items[0])
        return item,

    def get_background_items(self, window, current_directory):
        """Adds the 'Replace in Filenames' menu item to the Nautilus right-click menu,
           connects its 'activate' signal to the 'run' method passing the current Directory"""
        item = nautilus.MenuItem('NautilusPython::gtk-find-and-replace',
                                 _('Replace in Filenames'),
                                 _('Replace in Filenames of the Current Directory') )
        item.set_property('icon', 'gtk-find-and-replace')
        item.connect('activate', self.run, current_directory)
        return item,
