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
        '''
        This method creates an instance variable to store the schema
        that will be used to store items in the collection.
        '''
        args = [name + '.schema']
        args += [Secret.SchemaFlags.NONE]
        args += [{'logo': Secret.SchemaAttributeType.STRING,
                  'service': Secret.SchemaAttributeType.STRING,
                  'username': Secret.SchemaAttributeType.STRING}]
        self.schema = Secret.Schema.new(*args)
    
    def get_collection(self):
        '''
        This method finds the collection we need to store items, or
        if that collection doesn't exist yet, it creates it.
        '''
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
        '''
        This method loads the collections items in a reliable way.
        Ideally just doing the get_collection() method call would be enough,
        however if the collection is initially locked the item attributes,
        label and secret, at least, aren't updated. So we need to either
        go into dbus to do it manually, or just reconnect the service.
        We do the later here for convenience.
        '''
        self.service.disconnect()
        flags = Secret.ServiceFlags.LOAD_COLLECTIONS
        self.service = Secret.Service.get_sync(flags)
        for c in self.service.get_collections():
            if c.get_label() == self.collection_name:
                self.collection = c
                break
    
    def create_item(self, logo, service, username, password, notes):
        '''
        This method creates an item on the collection
        currently in use, and returns that item.
        '''
        attributes = {'logo': logo, 'service': service, 'username': username}
        secret = repr((password, notes))
        value = Secret.Value(secret, len(secret), 'text/plain')
        args = (self.collection, self.schema, attributes,
                service + ': ' + username, value,
                Secret.ItemCreateFlags.NONE, None)
        item = Secret.Item.create_sync(*args)
        return item
    
    def edit_item(self, item, logo, service, username, password, notes):
        '''
        This method can edit the attributes, the secret value
        and the label of the item in question.
        '''
        secret = repr((password, notes))
        value = Secret.Value(secret, len(secret), 'text/plain')
        item.set_secret_sync(value)
        attributes = {'logo': logo, 'service': service, 'username': username}
        item.set_attributes_sync(self.schema, attributes)
        item.set_label_sync(service + ': ' + username)
    
    def delete_item(self, item):
        '''
        This method deletes the item referenced.
        '''
        item.delete_sync()
    
    def get_secret(self, item):
        '''
        This method returns the secret associated with the item provided.
        It needs to eval() before returning since it's stored with repr().
        '''
        item.load_secret_sync()
        return eval(item.get_secret().get_text())
    
    def lock(self):
        return self.service.lock_sync([self.collection])[0] == 1
    
    def unlock(self):
        return self.service.unlock_sync([self.collection])[0] == 1
    
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

