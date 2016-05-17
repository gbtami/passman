# -*- coding: utf-8 -*-

'''
Module for the HeaderBar class
'''

from gi import require_version
require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gio

from .dialogs import AddDialog


class HeaderBar(Gtk.HeaderBar):
    '''
    HeaderBar class
    '''
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.set_title(app.title)
        self.set_show_close_button(True)
        # This is necessary for Windows
        self.set_decoration_layout('menu:close')
        self.connect('unrealize', self.on_unrealize)
        
        button = Gtk.Button()
        button.connect('clicked', self.on_add)
        icon = Gio.ThemedIcon(name='list-add-symbolic')
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        self.pack_start(button)
        
        view_settings = app.settings.get_child('view')
        self.view_mode = view_settings['mode']
        self.view_size = view_settings['size']
        action = Gio.SimpleAction(name='view_mode_switch',
                                  parameter_type=GLib.VariantType('s'),
                                  state=GLib.Variant('s', self.view_mode))
        app.add_action(action)
        action.connect('activate', self.on_view_mode)
        
        button = Gtk.MenuButton()
        builder = app.make_builder(app.gui_custom)
        bar_menu = builder.get_object('bar_menu')
        button.set_popover(bar_menu)
        icon = Gio.ThemedIcon(name='open-menu-symbolic')
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        self.pack_end(button)
        
        self.scale = builder.get_object('scale')
        self.scale.set_value(self.view_size)
        self.scale.connect('value-changed', self.on_value_changed)
        self.show_all()
    
    def on_view_mode(self, action, target):
        '''
        This method handles the view mode changed when
        invoked from the header bar menu.
        '''
        self.view_mode = target.get_string()
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
            button.logo.set_mode(mode)
    
    def on_value_changed(self, scale):
        '''
        This method handles the size change when invoked
        from the header bar menu.
        '''
        size = int(scale.get_value())
        self.view_size = size
        for c in self.app.main_view.flowbox.get_children():
            button = c.get_child()
            button.logo.set_size(size)
    
    def on_add(self, button):
        '''
        This method show the dialog that lets you create a new account.
        '''
        dialog = AddDialog(self.app)
        response = dialog.run()
        while response == Gtk.ResponseType.OK:
            data = dialog.get_data()
            if data['service'] and data['password']:
                item = self.app.main_view.secret.create_item(**data)
                button = self.app.main_view.create_button(item, dialog.logo)
                self.app.main_view.insert_button(button)
                break
            error = Gtk.MessageDialog(transient_for=dialog,
                                      message_type=Gtk.MessageType.ERROR)
            error.add_buttons(_('OK'), Gtk.ResponseType.OK)
            message = _('The {} and {} fields must be filled.')
            message = message.format(_('<b>Service</b>'), _('<b>Password</b>'))
            error.set_markup(message)
            error.run()
            error.destroy()
            response = dialog.run()
        dialog.destroy()
    
    def on_unrealize(self, widget):
        '''
        This method is called when the window is destroyed.
        I could handle it in the window instance instead, but since
        the variables storing the size and mode are on this object by
        the time the window called it's own unrealize, the header bar
        would already be destroyed, and these variables would be gone.
        '''
        view_settings = self.app.settings.get_child('view')
        view_settings.set_value('size', GLib.Variant('q', self.view_size))
        view_settings.set_string('mode', self.view_mode)

