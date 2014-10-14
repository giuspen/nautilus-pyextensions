# -*- coding: utf-8 -*-
#
#       core.py
#
#       Copyright 2008-2014 Giuseppe Penone <giuspen@gmail.com>
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

from gi.repository import Gtk, GdkPixbuf, GConf
import sys, os, shutil, re, subprocess, webbrowser
import cons


class GladeWidgetsWrapper:
    """Handles the retrieval of glade widgets"""

    def __init__(self, glade_file_path, gui_instance):
        try:
            self.glade_widgets = Gtk.Builder()
            self.glade_widgets.set_translation_domain(cons.APP_NAME)
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


class InfoModel:
    """Holds the information"""

    def __init__(self):
        """Sets up and populates the Gtk.ListStore"""
        self.liststore = Gtk.ListStore('gboolean', str, str)
        self.load_model()
        # Information about the Consistence of the model with the instanced Nautilus
        self.liststore.nautilus_restart_needed = False

    def load_model(self):
        """Load/Reload the model"""
        for dirpath, dirnames, filenames in os.walk(cons.PYEXTENSIONS_DIR):
            for filename in filenames:
                if os.path.splitext(filename)[1] == '.py':
                    active = (dirpath == cons.PYEXTENSIONS_DIR)
                    pyextension_path = os.path.join(dirpath, filename)
                    icon_path = self.get_icon_path(self.get_icon_name(pyextension_path))
                    if icon_path == None:
                        icon_path = self.get_icon_path("dialog-question")
                    self.liststore.append([active, icon_path, filename])
    
    def get_pyextensions_list(self):
        """Returns the list of all pyextensions (active and non)"""
        ret_list = []
        tree_iter = self.liststore.get_iter_first()
        while tree_iter != None:
            ret_list.append(self.liststore[tree_iter][2])
            tree_iter = self.liststore.iter_next(tree_iter)
        return ret_list
    
    def add_pyextension(self, filepath):
        """Add a PyExtension to the model, as Not Active"""
        pyextension_path = os.path.join(cons.PYEXTENSIONS_NOT_ACTIVE_DIR, os.path.basename(filepath))
        shutil.copy(filepath, pyextension_path)
        icon_path = self.get_icon_path(self.get_icon_name(pyextension_path))
        if icon_path == None:
            icon_path = self.get_icon_path("dialog-question")
        self.liststore.append([False, icon_path, os.path.basename(filepath)])

    def remove_pyextension(self, tree_iter):
        """Remove a PyExtension from the model, Not Active directory"""
        os.remove(os.path.join(cons.PYEXTENSIONS_NOT_ACTIVE_DIR, self.liststore[tree_iter][2]))
        self.liststore.remove(tree_iter)

    def pyextension_already_exists(self, pyextension_name):
        """Returns True if a PyExtension with the given Name is already into the model"""
        tree_iter = self.liststore.get_iter_first()
        while tree_iter != None:
            if self.liststore[tree_iter][2] == pyextension_name:
                return True
            tree_iter = self.liststore.iter_next(tree_iter)
        return False

    def get_icon_name(self, pyextension_path):
        """Returns the name of the icon associated to the given pyextension"""
        pyextension_file = open(pyextension_path, 'r')
        pyextension_file_string = pyextension_file.read()
        pyextension_file.close()
        # regular expression: search for a string preceeded by "'NautilusPython::" and followed by "'"
        match = re.search("(?<=icon\=).*?(?=\))", pyextension_file_string)
        if match == None: return None
        else:
            out_str = match.group(0).replace("icon","")
            out_str = out_str.replace("'","").replace("\"","")
            out_str = out_str.replace(",","")
            return out_str.strip()

    def get_icon_path(self, icon_name):
        """Returns the path of the icon from the icon name"""
        if icon_name == None: return None
        for starting_dir in [cons.GLADE_PATH,
                             '/usr/share/icons/gnome', '/usr/share/icons/hicolor', '/usr/share/pixmaps',
                             '/usr/local/share/icons/gnome', '/usr/local/share/icons/hicolor', '/usr/local/share/pixmaps']:
            for dirpath, dirnames, filenames in os.walk(starting_dir):
                for filename in filenames:
                    if os.path.splitext(filename)[0] == icon_name:
                        return os.path.join(dirpath, filename)
        return None

    def get_model(self):
        """Returns the model"""
        return self.liststore

    def get_nautilus_restart_needed(self):
        """Returns True if there is Inconsistence between the model and the instanced Nautilus"""
        return self.liststore.nautilus_restart_needed

    def set_nautilus_restart_needed(self, restart_needed):
        """Sets the Consistence/Inconsistence between the model and the instanced Nautilus"""
        self.liststore.nautilus_restart_needed = restart_needed


class NautilusPyExtensions:
    """The application's main window"""

    def __init__(self, store):
        """Instantiate the Glade Widgets Wrapper, create the view, initialize the statusbar"""
        # add the needed icons to the gtk stock
        factory = Gtk.IconFactory()
        for filename, stock_name in cons.ICONS_FILENAMES:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)
            iconset = Gtk.IconSet.new_from_pixbuf(pixbuf)
            factory.add(stock_name, iconset)
        factory.add_default()
        # system settings
        gtk_settings = Gtk.Settings.get_default()
        gtk_settings.set_property("gtk-button-images", True)
        gtk_settings.set_property("gtk-menu-images", True)
        os.environ['UBUNTU_MENUPROXY'] = '0' # for custom stock icons not visible in appmenu
        # instantiate the Glade Widgets Wrapper
        self.glade = GladeWidgetsWrapper(cons.GLADE_PATH + 'nautilus-pyextensions.glade', self)
        # ui manager
        actions = Gtk.ActionGroup("Actions")
        actions.add_actions(cons.get_entries(self))
        self.ui = Gtk.UIManager()
        self.ui.insert_action_group(actions, 0)
        self.glade.window.add_accel_group(self.ui.get_accel_group())
        self.ui.add_ui_from_string(cons.UI_INFO)
        # menubar add
        self.glade.vbox_main.pack_start(self.ui.get_widget("/MenuBar"), False, False, 0)
        self.glade.vbox_main.reorder_child(self.ui.get_widget("/MenuBar"), 0)
        # toolbar add
        self.glade.vbox_main.pack_start(self.ui.get_widget("/ToolBar"), False, False, 0)
        self.glade.vbox_main.reorder_child(self.ui.get_widget("/ToolBar"), 1)
        self.ui.get_widget("/ToolBar").set_style(Gtk.ToolbarStyle.ICONS)
        # create a variable pointing to the instance of the InfoModel class
        self.store = store
        # create the view
        self.view = Gtk.TreeView.new_with_model(store.get_model())
        self.renderer_checkbox = Gtk.CellRendererToggle()
        self.renderer_checkbox.set_property('activatable', True)
        self.renderer_checkbox.connect('toggled', self.toggle_active, store.get_model())
        self.renderer_pixbuf = Gtk.CellRendererPixbuf()
        self.renderer_text = Gtk.CellRendererText()
        self.columns = [None]*3
        self.columns[0] = Gtk.TreeViewColumn(_("Active"), self.renderer_checkbox, active=0) # active=0 <> read from column 0 of model
        self.columns[1] = Gtk.TreeViewColumn(_("Icon"), self.renderer_pixbuf)
        self.columns[1].set_cell_data_func(self.renderer_pixbuf, self.make_pixbuf)
        self.columns[2] = Gtk.TreeViewColumn(_("PyExtension"), self.renderer_text, text=2) # text=2 <> read from column 2 of model
        for n in range(3):
            self.view.append_column(self.columns[n])
        self.viewselection = self.view.get_selection()
        self.glade.scrolledwindow.add(self.view)
        # initialize the statusbar
        self.statusbar_context_id = self.glade.statusbar.get_context_id('')
        self.glade.statusbar.push(self.statusbar_context_id, _("Version %s") % cons.VERSION)
        self.glade.aboutdialog.set_version(cons.VERSION)
        # retrieve the gconf settings, set them if this is the first run
        self.gconf_client = GConf.Client.get_default()
        self.gconf_client.add_dir("/apps/nautilus-pyextensions", GConf.ClientPreloadType.PRELOAD_NONE)
        if self.gconf_client.get_string("/apps/nautilus-pyextensions/picking_dir") == None:
            self.gconf_client.set_string("/apps/nautilus-pyextensions/picking_dir", os.path.expanduser('~'))
        self.win_size_n_pos = {}
        # window restore size
        self.win_size_n_pos['win_size'] = [self.gconf_client.get_int("/apps/nautilus-pyextensions/win_size_w"),
                                           self.gconf_client.get_int("/apps/nautilus-pyextensions/win_size_h")]
        if 0 not in self.win_size_n_pos['win_size']:
            self.glade.window.resize(self.win_size_n_pos['win_size'][0], self.win_size_n_pos['win_size'][1])
        # have the window and all child widgets visible
        self.glade.window.show_all()
        # window restore position
        self.win_size_n_pos['win_position'] = [self.gconf_client.get_int("/apps/nautilus-pyextensions/win_position_x"),
                                               self.gconf_client.get_int("/apps/nautilus-pyextensions/win_position_y")]
        self.glade.window.move(self.win_size_n_pos['win_position'][0], self.win_size_n_pos['win_position'][1])

    def check_dependency(self, dependency=None):
        """Check and eventually install a Dependency"""
        if dependency == None:
            # {"exe_name":"package_name",...}
            pyextensions_list = self.store.get_pyextensions_list()
            check_list = {}
            if "tortoisehg-here.py" in pyextensions_list: check_list["thg"] = "tortoisehg"
            if "meld-compare.py" in pyextensions_list: check_list["meld"] = "meld"
            if "kdiff3-compare.py" in pyextensions_list: check_list["kdiff3"] = "kdiff3-qt"
            if "add-to-audacious-playlist.py" in pyextensions_list: check_list["audacious"] = "audacious"
        else: check_list = dependency
        for key in check_list:
            if not os.path.isfile(cons.BIN_PATH_1 + key)\
            and not os.path.isfile(cons.BIN_PATH_2 + key):
                if self.dialog_question(_("%s needs to be installed in order to activate the selected pyextension, shall I install it?") % key.upper()):
                    subprocess.call(cons.INSTALL_STRING % check_list[key], shell=True)
                else: return False
        return True

    def toggle_active(self, cell, path, model):
        """Toggles the Active state of the PyExtension"""
        pyextension_path = os.path.join(cons.PYEXTENSIONS_DIR, model[path][2])
        pyextension_not_active_path = os.path.join(cons.PYEXTENSIONS_NOT_ACTIVE_DIR, model[path][2])
        if model[path][0]:
            shutil.move(pyextension_path, pyextension_not_active_path) # move from active to not_active directory
            if os.path.exists(pyextension_path + 'c'): os.remove(pyextension_path + 'c')
            self.glade.statusbar.push(self.statusbar_context_id, _('%s Deactivated') % model[path][2])
        else:
            if "tortoisehg" in model[path][2]:
                if not self.check_dependency({"thg":"tortoisehg"}): return
            if "meld" in model[path][2]:
                if not self.check_dependency({"meld":"meld"}): return
            elif "audacious" in model[path][2]:
                if not self.check_dependency({"audacious":"audacious"}): return
            elif "kdiff3" in model[path][2]:
                if not self.check_dependency({"kdiff3":"kdiff3-qt"}): return
            shutil.move(pyextension_not_active_path, pyextension_path) # move from not_active to active directory
            self.glade.statusbar.push(self.statusbar_context_id, _('%s Activated') % model[path][2])
        model[path][0] = not model[path][0]
        self.store.set_nautilus_restart_needed(True)

    def make_pixbuf(self, treeviewcolumn, cell, model, tree_iter, data):
        """Function to associate the pixbuf to the cell renderer"""
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(model[tree_iter][1], 24, 24)
        cell.set_property('pixbuf', pixbuf)

    def flag_all_rows(self, *args):
        """Flags All Rows"""
        tree_iter = self.store.liststore.get_iter_first()
        while tree_iter != None:
            if self.store.liststore[tree_iter][0] == False:
                self.toggle_active(None, tree_iter, self.store.liststore)
            tree_iter = self.store.liststore.iter_next(tree_iter)
        self.store.set_nautilus_restart_needed(True)

    def unflag_all_rows(self, *args):
        """Unflags All Rows"""
        tree_iter = self.store.liststore.get_iter_first()
        while tree_iter != None:
            if self.store.liststore[tree_iter][0] == True:
                self.toggle_active(None, tree_iter, self.store.liststore)
            tree_iter = self.store.liststore.iter_next(tree_iter)
        self.store.set_nautilus_restart_needed(True)

    def on_window_delete_event(self, widget, event, data=None):
        """Before close the application: check the Consistence of the model with the instanced Nautilus"""
        return self.quit_application()

    def quit_application(self, *args):
        """Quit the gtk main loop"""
        if self.store.get_nautilus_restart_needed() == True:
            if not self.dialog_question(_('You should Restart Nautilus in order to see the changes (Button "Kill").\nDo you want to leave anyway?')):
                return True # stop the delete event
        # save window size and position in case they changed
        actual_win_size = list(self.glade.window.get_size())
        actual_win_pos = list(self.glade.window.get_position())
        if actual_win_size != self.win_size_n_pos['win_size']:
            self.win_size_n_pos['win_size'] = actual_win_size
            self.gconf_client.set_int("/apps/nautilus-pyextensions/win_size_w", self.win_size_n_pos['win_size'][0])
            self.gconf_client.set_int("/apps/nautilus-pyextensions/win_size_h", self.win_size_n_pos['win_size'][1])
        if actual_win_pos != self.win_size_n_pos['win_position']:
            self.win_size_n_pos['win_position'] = actual_win_pos
            self.gconf_client.set_int("/apps/nautilus-pyextensions/win_position_x", self.win_size_n_pos['win_position'][0])
            self.gconf_client.set_int("/apps/nautilus-pyextensions/win_position_y", self.win_size_n_pos['win_position'][1])
        self.glade.window.destroy()
        Gtk.main_quit()
        return False # propogate the delete event

    def restart_nautilus(self, *args):
        """Restarts Nautilus"""
        subprocess.call('killall nautilus', shell=True)
        self.store.set_nautilus_restart_needed(False)
        self.glade.statusbar.push(self.statusbar_context_id, _('Nautilus Restarted'))

    def add_pyextension(self, *args):
        """Opens the File Chooser Dialog, retrieves the filename, Adds the PyExtension as Not Active"""
        filepath = self.dialog_open_file(filter_pattern='*.py',
                                         filter_name=_('Python Source Files'),
                                         set_dir=self.gconf_client.get_string("/apps/nautilus-pyextensions/picking_dir"))
        if filepath != None:
            self.gconf_client.set_string("/apps/nautilus-pyextensions/picking_dir", os.path.dirname(filepath))
            filename = os.path.basename(filepath)
            if self.store.pyextension_already_exists(filename) == False:
                self.store.add_pyextension(filepath)
                self.glade.statusbar.push(self.statusbar_context_id, _('%s Added') % filename)
            else:
                self.dialog_warning(_('The PyExtension %s is Already into the List') % filename)

    def remove_pyextension(self, *args):
        """Opens the Confirmation Dialog, proceeds with the Removal"""
        (model, tree_iter) = self.viewselection.get_selected()
        if tree_iter == None:
            self.dialog_warning(_('No PyExtension is selected'))
        else:
            if model[tree_iter][0] == True:
                self.dialog_warning(_('%s must be Deactivated in order to be Removed') % model[tree_iter][2])
            else:
                filename = model[tree_iter][2]
                if self.dialog_question(_('Do you really want to Delete %s ?') % filename) == True:
                    self.store.remove_pyextension(tree_iter)
                    self.glade.statusbar.push(self.statusbar_context_id, _('%s Removed') % filename)

    def export_pyextension(self, *args):
        """Opens the Export PyExtension Dialog"""
        (model, tree_iter) = self.viewselection.get_selected()
        if tree_iter == None:
            self.dialog_warning(_('No PyExtension is selected'))
        else:
            filepath = self.dialog_save_file_as(filename=model[tree_iter][2], filter_pattern='*.py', filter_name=_('Python Source Files'))
            if filepath != None:
                if model[tree_iter][0] == True:
                    shutil.copy(os.path.join(cons.PYEXTENSIONS_DIR, model[tree_iter][2]), filepath)
                else:
                    shutil.copy(os.path.join(cons.PYEXTENSIONS_NOT_ACTIVE_DIR, model[tree_iter][2]), filepath)
                self.glade.statusbar.push(self.statusbar_context_id, _('%s Exported') % model[tree_iter][2])

    def edit_pyextension(self, *args):
        """Opens the PyExtension through the predefined Text Editor"""
        (model, tree_iter) = self.viewselection.get_selected()
        if tree_iter == None:
            self.dialog_warning(_('No PyExtension is selected'))
        else:
            if model[tree_iter][0] == True:
                self.dialog_warning(_('%s must be Deactivated in order to be Edited') % model[tree_iter][2])
            else:
                shell_command = "xdg-open" + " '" + os.path.join(cons.PYEXTENSIONS_NOT_ACTIVE_DIR, model[tree_iter][2]) + "' &"
                subprocess.call(shell_command, shell=True)
                self.glade.statusbar.push(self.statusbar_context_id, _('%s Opened for Editing') % model[tree_iter][2])

    def show_hide_toolbar(self, menuitem, data=None):
        """Show/Hide the Toolbar"""
        if self.ui.get_widget("/ToolBar").get_property("visible") == True:
            self.ui.get_widget("/ToolBar").hide()
        else: self.ui.get_widget("/ToolBar").show()

    def dialog_about(self, menuitem, data=None):
        """Show the About Dialog and hide it when a button is pressed"""
        self.glade.aboutdialog.run()
        self.glade.aboutdialog.hide()

    def on_help_menu_item_activated(self, menuitem, data=None):
        """Show the application's Instructions"""
        webbrowser.open("http://www.giuspen.com/nautilus-pyextensions/")

    def dialog_save_file_as(self, filename=None, filter_pattern=None, filter_name=None):
        """The application's save file as dialog, returns the retrieved filepath or None"""
        chooser = Gtk.FileChooserDialog( parent=self.glade.window,
                                         action=Gtk.FileChooserAction.SAVE,
                                         buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK) )
        chooser.set_current_folder(os.path.expanduser('~'))
        if filename != None:
            chooser.set_current_name(filename)
        if filter_pattern != None:
            filter = Gtk.FileFilter()
            filter.set_name(filter_name)
            filter.add_pattern(filter_pattern)
            chooser.add_filter(filter)
        if chooser.run() == Gtk.ResponseType.OK:
            filepath = chooser.get_filename()
            chooser.destroy()
            return filepath
        else:
            chooser.destroy()
            return None

    def dialog_open_file(self, filter_pattern=None, filter_name=None, set_dir=None):
        """The application's open file dialog, returns the retrieved filepath or None"""
        chooser = Gtk.FileChooserDialog( parent=self.glade.window,
                                         action=Gtk.FileChooserAction.OPEN,
                                         buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK) )
        chooser.set_current_folder(set_dir)
        if filter_pattern != None:
            filter = Gtk.FileFilter()
            filter.set_name(filter_name)
            filter.add_pattern(filter_pattern)
            chooser.add_filter(filter)
        if chooser.run() == Gtk.ResponseType.OK:
            filepath = chooser.get_filename()
            chooser.destroy()
            return filepath
        else:
            chooser.destroy()
            return None

    def dialog_question(self, message):
        """The application's question dialog, returns True if the user presses OK"""
        dialog = Gtk.MessageDialog(parent=self.glade.window,
                                   flags=Gtk.DialogFlags.MODAL|Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                   type=Gtk.MessageType.QUESTION,
                                   buttons=Gtk.ButtonsType.YES_NO,
                                   message_format=message)
        if dialog.run() == Gtk.ResponseType.YES:
            dialog.destroy()
            return True
        else:
            dialog.destroy()
            return False

    def dialog_warning(self, message):
        """The application's warning dialog"""
        dialog = Gtk.MessageDialog(parent=self.glade.window,
                                   flags=Gtk.DialogFlags.MODAL|Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                   type=Gtk.MessageType.WARNING,
                                   buttons=Gtk.ButtonsType.OK,
                                   message_format=message)
        dialog.run()
        dialog.destroy()
