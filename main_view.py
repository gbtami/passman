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

class MainView(Gtk.ScrolledWindow):
    '''
    MainView class
    '''
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.action_methods = {'delete': self.on_delete,
                               'edit': self.on_edit}
        self.secret = libsecret.LibSecret(app.name.lower(), app.app_id)
        self.make_context_menu()
        self.load_widgets()
    
    def make_context_menu(self):
        builder = Gtk.Builder.new_from_file(self.app.menus_file)
        context_menu_model = builder.get_object('context_menu')
        self.context_menu = Gtk.Menu.new_from_model(context_menu_model)
    
    def load_widgets(self):
        self.button_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.button_list.set_spacing(self.app.spacing)
        self.button_list.set_border_width(self.app.spacing)
        items = self.secret.collection.get_items()
        sorted_items = sorted(items, key=lambda x: x.get_label())
        self.sorted_labels = [i.get_label() for i in sorted_items]
        for item in sorted_items:
            button = self.create_button(item)
            self.button_list.pack_start(button, False, False, 0)
        self.add(self.button_list)
        self.show_all()
    
    def create_button(self, item):
        button = Gtk.Button()
        button.item = item
        button.connect('button-press-event', self.on_button_press)
        button.connect('clicked', self.on_button_click)
        button.connect('popup-menu', self.on_popup_menu)
        box = Gtk.Box(Gtk.Orientation.HORIZONTAL)
        label_text = ('<b>' + item.get_attributes()['service'] +
                      ':</b> ' + item.get_attributes()['username'])
        label = Gtk.Label(label_text, **{'use-markup': True})
        button.label = label
        image_dir = str(self.app.img_dir / 'test')
        image = Gtk.Image.new_from_file(image_dir)
        button.add(box)
        box.pack_start(image, False, False, 0)
        box.pack_start(label, True, False, 0)
        return button
    
    def insert_button(self, button):
        self.button_list.pack_start(button, False, False, 0)
        self.order_button(button)
        button.show_all()
    
    def order_button(self, button):
        index = bisect.bisect(self.sorted_labels, button.item.get_label())
        self.sorted_labels.insert(index, button.item.get_label())
        self.button_list.reorder_child(button, index)
    
    def edit_button(self, button):
        self.sorted_labels.remove(button.label.get_text())
        self.order_button(button)
        label_text = ('<b>' + button.item.get_attributes()['service'] +
                      ':</b> ' + button.item.get_attributes()['username'])
        button.label.set_markup(label_text)
    
    def delete_button(self, button):
        self.sorted_labels.remove(button.label.get_text())
        button.destroy()
    
    def popup_menu(self, widget, event):
        for action_name, method in self.action_methods.items():
            action = Gio.SimpleAction(name=action_name)
            self.app.add_action(action)
            action.connect('activate', method, widget)
        if self.context_menu.get_attach_widget():
            self.context_menu.detach()
        self.context_menu.attach_to_widget(widget)
        if event != None:
            self.context_menu.popup(None, None, None, None,
                                    event.button, event.time)
        else:
            event_time = Gtk.get_current_event_time()
            self.context_menu.popup(None, None, self.menu_func, widget, 0, event_time)
    
    def menu_func(self, menu, x, y, widget):
        window = widget.get_window()
        _, wx, wy = window.get_origin()
        brect = widget.get_clip()
        x = wx + brect.x + (brect.width / 2)
        y = wy + brect.y + (brect.height / 2)
        return x, y, False
    
    def on_popup_menu(self, widget):
        self.popup_menu(widget, None)
        return True
    
    def on_button_click(self, button):
        button.item.load_secret_sync()
        text = button.item.get_secret().get_text()
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(text, len(text))
    
    def on_button_press(self, widget, event):
        # Right mouse button click
        if event.button == Gdk.BUTTON_SECONDARY:
            self.popup_menu(widget, event)
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

