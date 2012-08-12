# -*- coding: utf-8 -*-
#
#       cons.py
#
#       Copyright 2008-2012 Giuseppe Penone <giuspen@gmail.com>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import os


APP_NAME = "nautilus-pyextensions"
VERSION = "3.1"
if os.path.isfile('modules/core.py'):
    GLADE_PATH = 'glade/'
    LOCALE_PATH = 'locale/'
else:
    GLADE_PATH = '/usr/share/nautilus-pyextensions/glade/'
    LOCALE_PATH = '/usr/share/locale/'
NAUTILUS_PYTHON_DIR = os.path.join(os.path.expanduser('~'), '.local/share/nautilus-python')
PYEXTENSIONS_DIR = os.path.join(NAUTILUS_PYTHON_DIR, 'extensions')
PYEXTENSIONS_NOT_ACTIVE_DIR = os.path.join(PYEXTENSIONS_DIR, 'not_active')
BIN_PATH_1 = "/usr/bin/"
BIN_PATH_2 = "/usr/local/bin/"
INSTALL_STRING = "gnome-terminal -x gksu apt-get\ -y\ install\ %s"
CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.config/nautilus-pyextensions')

AVAILABLE_LANGS = ['default', 'en', 'es', 'fr', 'it', 'ja']

ICONS_FILENAMES = [(GLADE_PATH + 'export.svg', 'Export'),
                   (GLADE_PATH + 'restart-nautilus.svg', 'Restart Nautilus'),
                   (GLADE_PATH + 'checkbox_checked.svg', 'Select All'),
                   (GLADE_PATH + 'checkbox_unchecked.svg', 'Deselect All'),
                   (GLADE_PATH + 'help-contents.svg', 'Help Contents'),
                   (GLADE_PATH + 'toolbar.png', 'Toolbar')]

UI_INFO = """
<ui>
    <menubar name='MenuBar'>
        <menu action='FileMenu'>
            <menuitem action='Kill'/>
            <menuitem action='Add'/>
            <menuitem action='Delete'/>
            <menuitem action='Export'/>
            <separator/>
            <menuitem action='QuitApp'/>
        </menu>
    
        <menu action='EditMenu'>
            <menuitem action='SelectAll'/>
            <menuitem action='DeselectAll'/>
            <separator/>
            <menuitem action='Edit'/>
        </menu>
    
        <menu action='ViewMenu'>
            <menuitem action='ShowHideToolbar'/>
        </menu>
    
        <menu action='HelpMenu'>
            <menuitem action='Help'/>
            <separator/>
            <menuitem action='About'/>
        </menu>
    </menubar>
    
    <toolbar name='ToolBar'>
        <toolitem action='Add'/>
        <toolitem action='Delete'/>
        <toolitem action='Export'/>
        <toolitem action='Edit'/>
        <separator/>
        <toolitem action='Kill'/>
        <separator/>
        <toolitem action='SelectAll'/>
        <toolitem action='DeselectAll'/>
        <separator/>
        <toolitem action='QuitApp'/>
    </toolbar>
</ui>
"""

def get_entries(inst):
    """Returns the Menu Entries Given the Class Instance"""
    return [
    # name, stock id, label
    ( "FileMenu", None, _("_File") ),
    ( "EditMenu", None, _("_Edit") ),
    ( "ViewMenu", None, _("_View") ),
    ( "HelpMenu", None, _("_Help") ),
    # name, stock id, label, accelerator, tooltip, callback
    ( "Kill", "Restart Nautilus", _("_Kill"), "<control>K", _("Restart Nautilus"), inst.restart_nautilus),
    ( "Add", "gtk-add", _("_Add"), "<control>N", _("Add A PyExtension"), inst.add_pyextension),
    ( "Delete", "gtk-clear", _("_Delete"), "Delete", _("Delete The Selected PyExtension"), inst.remove_pyextension),
    ( "Export", "Export", _("_Export"), "<control>X", _("Export The Selected PyExtension"), inst.export_pyextension),
    ( "QuitApp", "gtk-quit", _("_Quit"), "<control>Q", _("Quit Nautilus PyExtensions"), inst.quit_application),
    ( "SelectAll", "Select All", _("Select _All"), "<control>A", _("Activate All PyExtensions"), inst.flag_all_rows),
    ( "DeselectAll", "Deselect All", _("Deselect A_ll"), "<control><shift>A", _("Deactivate All PyExtensions"), inst.unflag_all_rows),
    ( "Edit", "gtk-edit", _("_Edit"), "<control>E", _("Edit The Selected PyExtension"), inst.edit_pyextension),
    ( "ShowHideToolbar", "Toolbar", _("Show/Hide _Toolbar"), None, _("Toggle Show/Hide Toolbar"), inst.show_hide_toolbar),
    ( "Help", "Help Contents", _("_Help"), None, _("Application's Home Page"), inst.on_help_menu_item_activated),
    ( "About", "gtk-about", _("_About"), None, _("About Nautilus PyExtensions"), inst.dialog_about),
    ]
