# -*- coding: utf-8 -*-

'''
Module for the HeaderBar class
'''

from gi import require_version
require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gio
import dialogs
import logogen


class HeaderBar(Gtk.HeaderBar):
    '''
    HeaderBar
    '''
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.set_title(app.title)
        self.set_show_close_button(True)
        
        button = Gtk.Button()
        button.connect('clicked', self.on_add)
        icon = Gio.ThemedIcon(name='list-add-symbolic')
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        self.pack_start(button)
        
        state = app.view_mode
        action = Gio.SimpleAction(name='view_mode',
                                  parameter_type=GLib.VariantType('s'),
                                  state=GLib.Variant('s', state))
        app.add_action(action)
        action.connect('activate', self.view_mode)
        
        button = Gtk.MenuButton()
        builder = Gtk.Builder.new_from_file(self.app.menus_file)
        bar_menu = builder.get_object('bar_menu')
        button.set_popover(bar_menu)
        icon = Gio.ThemedIcon(name='open-menu-symbolic')
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        self.pack_end(button)
        
        scale = builder.get_object('scale')
        scale.set_value(app.logo_size)
        scale.connect('value-changed', self.on_value_changed)
    
    def view_mode(self, action, target):
        self.app.view_mode = target.get_string()
        action.change_state(target)
        flowbox = self.app.main_view.flowbox
        if target == GLib.Variant('s', 'list'):
            flowbox.set_max_children_per_line(1)
            mode = 'list'
        else:
            flowbox.set_max_children_per_line(256)
            mode = 'grid'
        for c in self.app.main_view.flowbox.get_children():
            button = c.get_child()
            button.logo.set_view(mode)
            button.show_all()
    
    def on_value_changed(self, scale):
        size = int(scale.get_value())
        self.app.logo_size = size
        for c in self.app.main_view.flowbox.get_children():
            button = c.get_child()
            button.logo.set_size(size)
            button.show_all()
    
    def on_add(self, button):
        dialog = dialogs.Add(self.app)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            data = dialog.get_data()
            item = self.app.main_view.secret.create_item(*data)
            button = self.app.main_view.create_button(item)
            self.app.main_view.insert_button(button)
        dialog.destroy()

