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

class MainView(Gtk.ScrolledWindow):
    '''
    MainView
    '''
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.collection_name = app.name.lower()
        self.action_methods = {'delete': self.on_delete,
                               'edit': self.on_edit}
        self.make_context_menu()
        self.make_schema(app.app_id)
        self.get_collection()
        self.load_widgets()
    
    def make_context_menu(self):
        builder = Gtk.Builder.new_from_file(self.app.menus_file)
        context_menu_model = builder.get_object('context_menu')
        self.context_menu = Gtk.Menu.new_from_model(context_menu_model)
    
    def make_schema(self, name):
        args = [name + '.schema']
        args += [Secret.SchemaFlags.NONE]
        args += [{'logo': Secret.SchemaAttributeType.STRING,
                  'service': Secret.SchemaAttributeType.STRING,
                  'username': Secret.SchemaAttributeType.STRING,
                  'notes': Secret.SchemaAttributeType.STRING}]
        self.schema = Secret.Schema.new(*args)
    
    def get_collection(self):
        flags = Secret.ServiceFlags.LOAD_COLLECTIONS
        service = Secret.Service.get_sync(flags, None)
        for c in service.get_collections():
            if c.get_label() == self.collection_name:
                self.collection = c
                break
        else:
            flags = Secret.CollectionCreateFlags.COLLECTION_CREATE_NONE
            args = (service, self.collection_name, None, flags, None)
            self.collection = Secret.Collection.create_sync(*args)
        if self.collection.get_locked():
            service.unlock_sync([self.collection])
            # This is a bug in libsecret, unlock doesn't trigger an item
            # update and so it keeps using a cached version. We need to
            # either notify dbus manually, or reconnect the service and
            # get_collections() again. Reconnecting is easier and cleaner.
            service.disconnect()
            service = Secret.Service.get_sync(flags, None)
            for c in service.get_collections():
                if c.get_label() == self.collection_name:
                    self.collection = c
                    break
    
    def load_widgets(self):
        self.button_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.button_list.set_spacing(self.app.spacing)
        self.button_list.set_border_width(self.app.spacing)
        items = self.collection.get_items()
        sorted_items = sorted(items, key=lambda x:x.get_label())
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
        label_text = '<b>' + item.get_attributes()['service'] + ':' + '</b>'
        label_text += ' ' + item.get_attributes()['username']
        label = Gtk.Label(label_text, **{'use-markup': True})
        button.label = label
        image_dir = str(self.app.img_dir / 'test')
        image = Gtk.Image.new_from_file(image_dir)
        button.add(box)
        box.pack_start(image, False, False, 0)
        box.pack_start(label, True, False, 0)
        return button
    
    def insert_item(self, item):
        button = self.create_button(item)
        index = bisect.bisect(self.sorted_labels, item.get_label())
        self.sorted_labels.insert(index, item.get_label())
        self.button_list.pack_start(button, False, False, 0)
        self.button_list.reorder_child(button, index)
        self.show_all()
    
    def create_item(self, service, username, password, notes):
        attributes = {'logo': '', 'service': service,
                      'username': username, 'notes': notes}
        value = Secret.Value(password, len(password), 'text/plain')
        
        args = (self.collection, self.schema, attributes,
                service + ': ' + username, value,
                Secret.ItemCreateFlags.NONE, None)
        item = Secret.Item.create_sync(*args)
        return item
    
    def edit_item(self, item, service, username, password, notes):
        value = Secret.Value(password, len(password), 'text/plain')
        item.set_secret_sync(value)
        attributes = {'logo': '', 'service': service,
                      'username': username, 'notes': notes}
        item.set_attributes_sync(self.schema, attributes)
        item.set_label_sync(service + ': ' + username)
    
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
            self.context_menu.popup(None, None, None, None, 0, event_time)
    
    def on_popup_menu(self, widget):
        self.popup_menu(widget, None)
        return True
    
    def on_button_click(self, button):
        print(button)
    
    def on_button_press(self, widget, event):
        # Right mouse button click
        if event.button == Gdk.BUTTON_SECONDARY:
            self.popup_menu(widget, event)
        # We just want right clicks here, left clicks will
        # be handled elsewhere. So we return False.
        return False
    
    def on_delete(self, obj, param, arg1):
        item = arg1.item.get_label()
        message = 'Are you sure you want to delete account {}?'.format(item)
        dialog = Gtk.MessageDialog(self.app.window, 0,
                                   Gtk.MessageType.QUESTION,
                                   Gtk.ButtonsType.YES_NO, message)
        message2 = 'This operation will be permanent and irreversible.'
        dialog.format_secondary_text(message2)
        response = dialog.run()
        if response == Gtk.ResponseType.YES:
            self.sorted_labels.remove(arg1.item.get_label())
            arg1.item.delete_sync()
            arg1.destroy()
        dialog.destroy()
    
    def on_edit(self, obj, param, arg1):
        dialog = dialogs.Edit(self.app, arg1.item)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            service = dialog.service.get_text()
            username = dialog.username.get_text()
            password = dialog.password.get_text()
            buffer = dialog.notes.get_buffer()
            bounds = buffer.get_bounds()
            notes = buffer.get_text(bounds[0], bounds[1], False)
            self.edit_item(arg1.item, service, username, password, notes)
            arg1.label.set_text(arg1.item.get_label())
        dialog.destroy()

