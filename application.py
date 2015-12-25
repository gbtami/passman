# -*- coding: utf-8 -*-

'''
Module for the Application class
'''

import logging
from pathlib import Path

from gi import require_version
require_version('Gtk', '3.0')
require_version('Gdk', '3.0')
require_version('Keybinder', '3.0')
from gi.repository import Gtk, Gdk, Gio, GLib, Keybinder

from header_bar import HeaderBar
from main_view import MainView
import dialogs


class Application(Gtk.Application):
    '''
    Main Application
    '''
    
    name = 'PassMan'
    title = name
    version = '0.1.0'
    icon = 'dialog-password'
    website = 'http://www.idlecore.com/passman'
    spacing = 8
    app_id = 'com.idlecore.passman'
    app_dir = name.lower()
    data_dir = Path(GLib.get_user_data_dir()) / app_dir
    img_dir = data_dir / 'images'
    config_dir = Path(GLib.get_user_config_dir()) / app_dir
    autostart_dir = Path(GLib.get_user_config_dir()) / 'autostart'
    autostart_file = 'passman-autostart.desktop'
    log_dir = config_dir / 'logs'
    log_file = str(log_dir / (name.lower() + '.log'))
    gui_glade = str(data_dir / 'gui.glade')
    gui_ui = str(data_dir / 'gui.ui')
    schemas_dir = str(data_dir / 'schemas')
    schema_id = app_id
    
    def __init__(self):
        # Despite many examples showing __init__ being called with the
        # argument flags=Gio.ApplicationFlags.FLAGS_NONE, this is the
        # default behaviour already, so it's not required.
        super().__init__(application_id=self.app_id)
        description = ('Start the application hidden. '
                       'Useful when you start the application at login.')
        self.add_main_option('hide', 0, GLib.OptionFlags.NONE,
                             GLib.OptionArg.NONE, description, None)
        self.hide_flag = False
        self.started_hidden = False
        self.first_run = True
        self.connect('activate', self.on_activate)
        self.connect('startup', self.on_startup)
        self.connect('shutdown', self.on_shutdown)
        self.connect('handle-local-options', self.on_handle_local_options)
    
    def on_startup(self, app):
        self.settings = Gio.Settings(schema=self.schema_id + '.preferences')
        self.win_settings = Gio.Settings(schema=self.schema_id + '.window')
        self.width = self.win_settings['width']
        self.height = self.win_settings['height']
        self.about_dialog = None
        self.preferences_dialog = None
        logging.basicConfig(filename=self.log_file, level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s: %(message)s')
        
        self.window = Gtk.ApplicationWindow(application=app)
        self.window.connect('size-allocate', self.on_size_allocate)
        self.window.set_title(self.title)
        self.window.set_default_size(self.width, self.height)
        self.window.set_position(Gtk.WindowPosition.MOUSE)
        self.window.set_titlebar(HeaderBar(self))
        # We need to set the icon here as a backup, the gnome system monitor
        # for instance, and for whatever reason, doesn't choose the right icon
        # sometimes, particularly after hiding the window, and showing again.
        self.window.set_icon_name(self.icon)
        self.main_view = MainView(self)
        
        self.add_actions()
        builder = Gtk.Builder.new_from_file(self.gui_ui)
        app_menu = builder.get_object('app_menu')
        self.set_app_menu(app_menu)
        
        Keybinder.init()
        shortcuts = self.settings.get_child('shortcuts')
        Keybinder.bind(shortcuts['app-show'], self.add_show_shortcut)
        
        self.window.add(self.main_view)
    
    def add_show_shortcut(self, keystring):
        self.activate()
    
    def add_show_shortcut_test(self):
        schema = 'org.gnome.settings-daemon.plugins.media-keys'
        key = 'custom-keybindings'
        settings = Gio.Settings(schema=schema)
        bindings = settings.get_strv(key)
        custom = '/{}/{}/passman/'.format(schema.replace('.', '/'), key)
        if custom not in bindings:
            bindings.append(custom)
            settings.set_strv(key, bindings)
            schema = schema + '.' + key[:-1]
            settings = Gio.Settings(schema=schema, path=custom)
            settings.set_string('name', self.name)
            settings.set_string('command', self.name.lower())
            shortcuts = self.settings.get_child('shortcuts')
            settings.set_string('binding', shortcuts['app-show'])
    
    def on_handle_local_options(self, application, options):
        if options.contains('hide'):
            self.hide_flag = True
            self.started_hidden = True
        # All ok, process the rest of the command line
        return -1
    
    def add_actions(self):
        shortcuts = self.settings.get_child('shortcuts')
        action_methods = [('preferences', self.on_preferences, ''),
                          ('help', self.on_help, ''),
                          ('about', self.on_about, ''),
                          ('new', self.on_new, 'account-new'),
                          ('edit', self.on_edit, 'account-edit'),
                          ('delete', self.on_delete, 'account-delete'),
                          ('view_mode', self.on_view_mode, 'view-mode'),
                          ('view_size', self.on_view_size, 'view-size'),
                          ('quit', self.on_quit, 'app-quit')]
        for name, method, accel in action_methods:
            action = Gio.SimpleAction(name=name)
            self.add_action(action)
            action.connect('activate', method)
            if accel and shortcuts[accel]:
                self.set_accels_for_action('app.' + name, [shortcuts[accel]])
    
    def on_activate(self, app):
        if self.hide_flag:
            self.hide_flag = False
            return
        if self.main_view.secret.unlock():
            if self.first_run:
                self.first_run = False
                self.main_view.secret.load_collection()
                self.main_view.init_buttons()
            self.window.show()
            # This seems to be the only way to actually
            # make the window get keyboard focus.
            self.window.get_window().focus(0)
        else:
            if not self.started_hidden:
                self.quit()
    
    def on_size_allocate(self, widget, allocation):
        self.width = allocation.width
        self.height = allocation.height
    
    def on_shutdown(self, app):
        window = Gio.Settings(schema=self.schema_id + '.window')
        self.win_settings.set_value('width', GLib.Variant('q', self.width))
        self.win_settings.set_value('height', GLib.Variant('q', self.height))
        # If the user wants timeouts while the app is running, it makes sense
        # to enforce those on exit as well, even when the timeout isn't over.
        if self.main_view.timeout:
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            clipboard.clear()
        self.main_view.secret.lock()
    
    def on_preferences(self, obj, param):
        if self.preferences_dialog != None:
            self.preferences_dialog.present()
            return
        self.preferences_dialog = dialogs.Preferences(self)
        self.preferences_dialog.run()
        self.preferences_dialog.destroy()
        self.preferences_dialog = None
    
    def on_help(self, obj, param):
        print('help')
    
    def on_about(self, obj, param):
        if self.about_dialog != None:
            self.about_dialog.present()
            return
        dialog = Gtk.AboutDialog(transient_for=self.window)
        #dialog.props.artists = ['artists']
        dialog.props.authors = ['Pedro \'xor\' Azevedo <passman@idlecore.com>']
        dialog.props.comments = _('Easy to use password manager.')
        dialog_copyright = _('Copyright © 2015 - {} authors')
        dialog.props.copyright = dialog_copyright.format(self.name)
        #dialog.props.documenters = ['documenters']
        #dialog.props.license = 'license'
        dialog.props.license_type = Gtk.License.GPL_3_0
        #dialog.props.logo = None
        dialog.props.logo_icon_name = self.icon
        dialog.props.program_name = self.name
        #dialog.props.translator_credits = 'translator_credits'
        dialog.props.version = self.version
        dialog.props.website = self.website
        dialog.props.website_label = 'Website'
        #dialog.props.wrap_license = False
        self.about_dialog = dialog
        response = dialog.run()
        dialog.destroy()
        self.about_dialog = None
    
    def on_new(self, obj, param):
        self.window.get_titlebar().on_add(None)
    
    def on_edit(self, obj, param):
        widget = self.window.get_focus()
        if widget.get_parent() in self.main_view.flowbox:
            self.main_view.on_edit(None, None, widget)
    
    def on_delete(self, obj, param):
        widget = self.window.get_focus()
        if widget.get_parent() in self.main_view.flowbox:
            self.main_view.on_delete(None, None, widget)
    
    def on_view_mode(self, action, param):
        action = self.lookup_action('view_mode_switch')
        if action.get_state() == GLib.Variant('s', 'list'):
            mode = GLib.Variant('s', 'grid')
        else:
            mode = GLib.Variant('s', 'list')
        action.activate(mode)
    
    def on_view_size(self, obj, param):
        scale = self.window.get_titlebar().scale
        adjustment = scale.get_adjustment()
        increment = adjustment.get_step_increment()
        value = scale.get_value() + increment
        upper = adjustment.get_upper()
        if value > upper:
            value = adjustment.get_lower()
        scale.set_value(value)
    
    def on_quit(self, obj, param):
        self.quit()

