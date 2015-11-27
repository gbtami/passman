'''
Module for the MainView class
'''

import bisect

from gi import require_version
require_version('Gtk', '3.0')
require_version('Gdk', '3.0')
require_version('Secret', '1')
from gi.repository import Gtk, Gdk, Gio, Secret
import dialogs
import libsecret
import logogen

class MainView(Gtk.ScrolledWindow):
    '''
    MainView class
    '''
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.secret = libsecret.LibSecret(app.name.lower(), app.app_id)
        self.load_widgets()
    
    def load_widgets(self):
        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_valign(Gtk.Align.START)
        self.flowbox.set_max_children_per_line(1)
        self.flowbox.set_sort_func(self.sort_function)
        self.flowbox.set_border_width(self.app.spacing)
        self.flowbox.set_column_spacing(self.app.spacing)
        self.flowbox.set_row_spacing(self.app.spacing)
        for item in self.secret.collection.get_items():
            button = self.create_button(item)
            self.insert_button(button)
        self.add(self.flowbox)
        self.show_all()
    
    def sort_function(self, child1, child2):
        
        label1 = child1.get_child().get_child().get_children()[1]
        label1 = label1.get_text().lower()
        label2 = child2.get_child().get_child().get_children()[1]
        label2 = label2.get_text().lower()
        if label1 > label2:
            return 1
        elif label1 < label2:
            return -1
        else:
            return 0
    
    def create_button(self, item):
        button = Gtk.Button()
        button.item = item
        button.connect('button-press-event', self.on_button_press)
        button.connect('clicked', self.on_button_click)
        button.connect('popup-menu', self.on_popup_menu)
        service = item.get_attributes()['service']
        username = item.get_attributes()['username']
        button.add(logogen.LogoGen(self.app, service, username).box)
        return button
    
    def insert_button(self, button):
        self.flowbox.add(button)
        # The next code is required because the flowbox children, that contain
        # the actual widgets, can get focus by default. So when the widgets
        # can get focus themselves, navigating with the keyboard becomes very
        # cumbersome, forcing us to tab twice to move between them.
        # Also the spacing added by the 'grid-child' style is inconsistent.
        # The space between the items is twice that of the border, so it was
        # removed and is instead configured manually through the flowbox.
        child = button.get_parent()
        child.set_can_focus(False)
        style = child.get_style_context()
        style.remove_class('grid-child')
        button.show_all()
    
    def edit_button(self, button):
        service = button.item.get_attributes()['service']
        username = button.item.get_attributes()['username']
        button.remove(button.get_child())
        button.add(logogen.LogoGen(app, service, username).box)
        self.flowbox.invalidate_sort()
    
    def delete_button(self, button):
        self.flowbox.remove(button.get_parent())
        button.destroy()
    
    def show_context_menu(self, widget):
        action_methods = {'delete': self.on_delete,
                          'edit': self.on_edit}
        for action_name, method in action_methods.items():
            action = Gio.SimpleAction(name=action_name)
            self.app.remove_action(action_name)
            self.app.add_action(action)
            action.connect('activate', method, widget)
        builder = Gtk.Builder.new_from_file(self.app.menus_file)
        self.context_menu = builder.get_object('context_menu')
        self.context_menu.set_relative_to(widget)
        self.context_menu.show()
    
    def on_popup_menu(self, widget):
        self.show_context_menu(widget)
        return True
    
    def on_button_click(self, button):
        button.item.load_secret_sync()
        text = button.item.get_secret().get_text()
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(text, len(text))
    
    def on_button_press(self, widget, event):
        # Right mouse button click
        if event.button == Gdk.BUTTON_SECONDARY:
            self.show_context_menu(widget)
        # We just want right clicks here, left clicks will
        # be handled elsewhere. So we return False.
        return False
    
    def on_delete(self, obj, param, button):
        item = button.item.get_label()
        message = 'Are you sure you want to delete account {}?'.format(item)
        dialog = Gtk.MessageDialog(self.app.window, 0,
                                   Gtk.MessageType.QUESTION,
                                   Gtk.ButtonsType.YES_NO, message)
        message2 = 'This operation will be permanent and irreversible.'
        dialog.format_secondary_text(message2)
        response = dialog.run()
        if response == Gtk.ResponseType.YES:
            self.secret.delete_item(button.item)
            self.delete_button(button)
        dialog.destroy()
    
    def on_edit(self, obj, param, button):
        dialog = dialogs.Edit(self.app, button.item)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            data = dialog.get_data()
            self.secret.edit_item(button.item, *data)
            self.edit_button(button)
        dialog.destroy()

