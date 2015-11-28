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
    schemas_dir = str(data_dir / 'schemas')
    schema_id = app_id
    
    def __init__(self):
        # Despite many examples showing __init__ being called with the
        # argument flags=Gio.ApplicationFlags.FLAGS_NONE, this is the
        # default behaviour already, so it's not required.
        super().__init__(application_id=self.app_id)
        self.connect('activate', self.on_activate)
        self.connect('startup', self.on_startup)
        self.settings = Gio.Settings(self.schema_id + '.preferences')
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
                          'help': self.on_help,
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
    
    def on_help(self, obj, param):
        print('help')
    
    def on_about(self, obj, param):
        dialog = Gtk.AboutDialog(None, self.window)
        #dialog.props.artists = ['artists']
        dialog.props.authors = ['Pedro \'xor\' Azevedo <passman@idlecore.com>']
        dialog.props.comments = 'Easy to use password manager.'
        dialog.props.copyright = 'Copyright © 2015 - ' + self.name + ' authors'
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
        response = dialog.run()
        dialog.destroy()
    
    def on_quit(self, obj, param):
        self.quit()

