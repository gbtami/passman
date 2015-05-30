'''
Module for the Application class
'''

from gi.repository import Gtk, Gio, GLib
from pathlib import Path
import config as cfg
from header_bar import HeaderBar
from main_view import MainView


class Application(Gtk.Application):

    '''
    Gtk Application
    '''

    def __init__(self):
        # Despite many examples showing __init__ being called with the
        # argument flags=Gio.ApplicationFlags.FLAGS_NONE, this is the
        # default behaviour already, so not required.
        super().__init__(application_id=cfg.app_id)
        self.connect('activate', self.on_activate)
        self.connect('startup', self.on_startup)

    def on_startup(self, app):
        # Here I choose the last path on the list because by XDG specification
        # (http://www.freedesktop.org/Standards/basedir-spec)
        # the default values are ['/usr/local/share', '/usr/share'],
        # and I don't want to install this app locally only.
        temp = Path(GLib.get_system_data_dirs()[-1])
        self.system_data_dir = temp / cfg.app_dir
        self.window = Gtk.ApplicationWindow(application=app)
        self.window.set_title(cfg.title)
        self.window.set_default_size(cfg.width, cfg.height)
        self.window.set_position(Gtk.WindowPosition.MOUSE)
        self.window.set_titlebar(HeaderBar())
        self.add_actions()
        builder_path = str(self.system_data_dir / 'app_menu.ui')
        builder = Gtk.Builder.new_from_file(builder_path)
        app_menu = builder.get_object('app_menu')
        self.set_app_menu(app_menu)
        self.window.add(MainView())

    def add_actions(self):
        preferences = Gio.SimpleAction(name='preferences')
        self.add_action(preferences)
        preferences.connect('activate', self.on_preferences)

        about = Gio.SimpleAction(name='about')
        self.add_action(about)
        about.connect('activate', self.on_about)

        quit = Gio.SimpleAction(name='quit')
        self.add_action(quit)
        quit.connect('activate', self.on_quit)

    def on_activate(self, app):
        self.window.show_all()

    def on_preferences(self, obj, param):
        print('preferences')

    def on_about(self, obj, param):
        print('about')

    def on_quit(self, obj, param):
        self.quit()

