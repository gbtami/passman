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
    width = 256 + 128
    height = 512
    spacing = 8
    app_id = 'com.idlecore.passman'
    app_dir = name.lower()
    data_dir = Path(GLib.get_user_data_dir()) / app_dir
    img_dir = data_dir / 'images'
    config_dir = Path(GLib.get_user_config_dir()) / app_dir
    log_dir = config_dir / 'logs'
    log_file = str(log_dir / (name.lower() + '.log'))
    menus_file = str(data_dir / 'menus.ui')
    
    def __init__(self):
        # Despite many examples showing __init__ being called with the
        # argument flags=Gio.ApplicationFlags.FLAGS_NONE, this is the
        # default behaviour already, so it's not required.
        super().__init__(application_id=self.app_id)
        self.connect('activate', self.on_activate)
        self.connect('startup', self.on_startup)
        logging.basicConfig(filename=self.log_file, level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s: %(message)s')
    
    def on_startup(self, app):
        self.window = Gtk.ApplicationWindow(application=app)
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
        titlebar = self.window.get_titlebar()
        action_methods = {'settings': titlebar.on_settings,
                          'test': titlebar.on_test,
                          'preferences': self.on_preferences,
                          'about': self.on_about,
                          'quit': self.on_quit}
        for name, method in action_methods.items():
            action = Gio.SimpleAction(name=name)
            self.add_action(action)
            action.connect('activate', method)
    
    def on_activate(self, app):
        self.window.show_all()
    
    def on_preferences(self, obj, param):
        print('preferences')
    
    def on_about(self, obj, param):
        print('about')
    
    def on_quit(self, obj, param):
        self.quit()

