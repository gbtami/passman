# -*- coding: utf-8 -*-

'''
Module for the libsecret API
'''

from gi import require_version
require_version('Secret', '1')
from gi.repository import GLib, Secret, Gio

class LibSecret:
    '''
    LibSecret class
    '''
    
    def __init__(self, app):
        self.collection_name = app.name.lower()
        self.make_schema(app.app_id)
        self.get_collection()
    
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
        self.service = Secret.Service.get_sync(flags)
        for c in self.service.get_collections():
            if c.get_label() == self.collection_name:
                self.collection = c
                break
        else:
            flags = Secret.CollectionCreateFlags.COLLECTION_CREATE_NONE
            args = (self.service, self.collection_name, None, flags)
            try:
                self.collection = Secret.Collection.create_sync(*args)
            except GLib.GError as e:
                self.collection = None
        
    def load_collection(self):
        # This is a bug in libsecret, unlock doesn't trigger an item
        # update and so it keeps using a cached version. We need to
        # either notify dbus manually, or reconnect the service and
        # get_collections() again. Reconnecting is easier and cleaner.
        self.service.disconnect()
        flags = Secret.ServiceFlags.LOAD_COLLECTIONS
        self.service = Secret.Service.get_sync(flags)
        for c in self.service.get_collections():
            if c.get_label() == self.collection_name:
                self.collection = c
                break
    
    def create_item(self, logo, service, username, password, notes):
        attributes = {'logo': logo, 'service': service,
                      'username': username, 'notes': notes}
        value = Secret.Value(password, len(password), 'text/plain')
        args = (self.collection, self.schema, attributes,
                service + ': ' + username, value,
                Secret.ItemCreateFlags.NONE, None)
        item = Secret.Item.create_sync(*args)
        return item
    
    def edit_item(self, item, logo, service, username, password, notes):
        value = Secret.Value(password, len(password), 'text/plain')
        item.set_secret_sync(value)
        attributes = {'logo': logo, 'service': service,
                      'username': username, 'notes': notes}
        item.set_attributes_sync(self.schema, attributes)
        item.set_label_sync(service + ': ' + username)
    
    def delete_item(self, item):
        item.delete_sync()
    
    def get_secret(self, item):
        item.load_secret_sync()
        return item.get_secret().get_text()
    
    def lock(self):
        return self.service.lock_sync([self.collection])[0] == 1
    
    def unlock(self):
        return self.service.unlock_sync([self.collection])[0] == 1
    
    def is_locked(self):
        return self.collection.get_locked()
    
    def change_password(self):
        bus = Gio.bus_get_sync(Gio.BusType.SESSION)
        bus_name = 'org.freedesktop.secrets'
        object_path = '/org/freedesktop/secrets'
        interface = 'org.gnome.keyring.InternalUnsupportedGuiltRiddenInterface'
        method = 'ChangeWithPrompt'
        collection_path = self.collection.get_object_path()
        variant = GLib.Variant.new_object_path(collection_path)
        parameters = GLib.Variant.new_tuple(variant)
        flags = Gio.DBusCallFlags.NONE
        prompt = bus.call_sync(bus_name, object_path, interface, method,
                               parameters, None, flags, -1, None)
        interface = 'org.freedesktop.Secret.Prompt'
        method = 'Prompt'
        parameters = GLib.Variant.new_tuple(GLib.Variant('s', ''))
        bus.call_sync(bus_name, prompt.unpack()[0], interface, method,
                      parameters, None, flags, -1, None)
    
    def set_default(self):
        self.service.set_alias_sync('default', self.collection)
    
    def is_default(self):
        flags = Secret.CollectionFlags.NONE
        args = (self.service, 'default', flags)
        default = self.collection.for_alias_sync(*args)
        return default.get_label() == self.collection_name

