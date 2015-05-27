'''
Module for the HeaderBar class
'''

from gi.repository import Gtk, Gio
import config as cfg


class HeaderBar(Gtk.HeaderBar):

    '''
    HeaderBar
    '''

    def __init__(self):
        super().__init__()
        self.set_title(cfg.title)
        self.set_show_close_button(True)

        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="list-add-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        self.pack_start(button)

        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="open-menu-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        self.pack_end(button)

        button = Gtk.MenuButton()
        self.pack_end(button)
