'''
Module for the MainView class
'''

from gi import require_version
require_version('Gtk', '3.0')
require_version('Gdk', '3.0')
require_version('Secret', '1')
from gi.repository import Gtk, Gdk, Gio, Secret


class MainView(Gtk.ScrolledWindow):
    '''
    MainView
    '''
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.collection_name = app.name.lower()
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
        for i in reversed(self.collection.get_items()):
            self.add_item(i)
        self.add(self.button_list)
    
    def add_item(self, item):
        button = Gtk.Button()
        button.item = item
        button.connect('button-press-event', self.on_button_press)
        button.connect('clicked', self.on_button_click)
        button.connect('popup-menu', self.on_popup_menu)
        box = Gtk.Box(Gtk.Orientation.HORIZONTAL)
        label = Gtk.Label(item.get_label())
        image_dir = str(self.app.img_dir / 'test')
        image = Gtk.Image.new_from_file(image_dir)
        button.add(box)
        box.pack_start(image, False, False, 0)
        box.pack_start(label, True, False, 0)
        self.button_list.pack_start(button, False, False, 0)
        self.show_all()
    
    def create_item(self, service, username, password, notes):
        attributes = {'logo': '', 'service': service,
                      'username': username, 'notes': notes}
        value = Secret.Value(password, len(password), 'text/plain')
        args = (self.collection, self.schema, attributes,
                service + ':' + username, value,
                Secret.ItemCreateFlags.NONE, None)
        item = Secret.Item.create_sync(*args)
        return item
    
    def popup_menu(self, widget, event):
        action_list = [('delete', self.on_delete),
                       ('properties', self.on_properties)]
        for a, m in action_list:
            action = self.app.lookup_action(a)
            action.disconnect_by_func(m)
            action.connect('activate', m, widget)
        if self.context_menu.get_for_attach_widget(widget):
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
        message = 'Are you sure you want to delete password {}?'.format(item)
        dialog = Gtk.MessageDialog(self.app.window, 0,
                                   Gtk.MessageType.QUESTION,
                                   Gtk.ButtonsType.YES_NO, message)
        message2 = 'This operation will be permanent and irreversible.'
        dialog.format_secondary_text(message2)
        response = dialog.run()
        if response == Gtk.ResponseType.YES:
            arg1.item.delete_sync()
            arg1.destroy()
        dialog.destroy()
        
    
    def on_properties(self, obj, param, arg1):
        print('on_properties')

