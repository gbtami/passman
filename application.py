# -*- coding: utf-8 -*-

'''
Module for the Application class
'''

import logging

from gi import require_version
require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GLib

from pathlib import Path
from header_bar import HeaderBar
from main_view import MainView


class Application(Gtk.Application):
    '''
    Main Application
    '''
    
    name = 'PassMan'
    title = name
    version = '0.1.0'
    website = 'http://www.idlecore.com/passman'
    spacing = 8
    app_id = 'com.idlecore.passman'
    app_dir = name.lower()
    data_dir = Path(GLib.get_user_data_dir()) / app_dir
    img_dir = data_dir / 'images'
    config_dir = Path(GLib.get_user_config_dir()) / app_dir
    log_dir = config_dir / 'logs'
    log_file = str(log_dir / (name.lower() + '.log'))
    menus_file = str(data_dir / 'menus.ui')
    preferences_file = str(data_dir / 'preferences.glade')
    schemas_dir = str(data_dir / 'schemas')
    schema_id = app_id
    
    def __init__(self):
        # Despite many examples showing __init__ being called with the
        # argument flags=Gio.ApplicationFlags.FLAGS_NONE, this is the
        # default behaviour already, so it's not required.
        super().__init__(application_id=self.app_id)
        self.connect('activate', self.on_activate)
        self.connect('startup', self.on_startup)
        self.connect('shutdown', self.on_shutdown)
    
    def on_startup(self, app):
        self.settings = Gio.Settings(self.schema_id + '.preferences')
        self.view_mode = self.settings.get_child('view')['mode']
        self.logo_size = self.settings.get_child('logo')['size']
        self.window_settings = Gio.Settings(self.schema_id + '.window')
        self.width = self.window_settings['width']
        self.height = self.window_settings['height']
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
        self.main_view = MainView(self)
        
        self.add_actions()
        builder = Gtk.Builder.new_from_file(self.menus_file)
        app_menu = builder.get_object('app_menu')
        self.set_app_menu(app_menu)

        self.window.add(self.main_view)
    
    def add_actions(self):
        action_methods = {'preferences': self.on_preferences,
                          'help': self.on_help,
                          'about': self.on_about,
                          'quit': self.on_quit}
        for name, method in action_methods.items():
            action = Gio.SimpleAction(name=name)
            self.add_action(action)
            action.connect('activate', method)
    
    def on_activate(self, app):
        self.window.show_all()
    
    def on_size_allocate(self, widget, allocation):
        self.width = allocation.width
        self.height = allocation.height
    
    def on_shutdown(self, app):
        logo = self.settings.get_child('logo')
        view = self.settings.get_child('view')
        window = Gio.Settings(self.schema_id + '.window')
        logo.set_int('size', self.logo_size)
        view.set_string('mode', self.view_mode)
        self.window_settings.set_int('width', self.width)
        self.window_settings.set_int('height', self.height)
    
    def on_preferences(self, obj, param):
        if self.preferences_dialog != None:
            self.preferences_dialog.present()
            return
        builder = Gtk.Builder.new_from_file(self.preferences_file)
        dialog = builder.get_object('preferences_dialog')
        dialog.set_transient_for(self.window)
        self.preferences_dialog = dialog
        dialog.run()
        dialog.destroy()
        self.preferences_dialog = None
    
    def on_help(self, obj, param):
        print('help')
    
    def on_about(self, obj, param):
        if self.about_dialog != None:
            self.about_dialog.present()
            return
        dialog = Gtk.AboutDialog(None, self.window)
        #dialog.props.artists = ['artists']
        dialog.props.authors = ['Pedro \'xor\' Azevedo <passman@idlecore.com>']
        dialog.props.comments = _('Easy to use password manager.')
        copyright = _('Copyright © 2015 - {} authors')
        dialog.props.copyright = copyright.format(self.name)
        #dialog.props.documenters = ['documenters']
        #dialog.props.license = 'license'
        dialog.props.license_type = Gtk.License.GPL_3_0
        #dialog.props.logo = None
        dialog.props.logo_icon_name = 'dialog-password'
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
    
    def on_quit(self, obj, param):
        self.quit()

