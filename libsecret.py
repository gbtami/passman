# -*- coding: utf-8 -*-

'''
Module for the libsecret API
'''

from gi import require_version
require_version('Secret', '1')
# Yes, I know gnome-keyring is deprecated, I also know libsecret has
# no way to change the password of a collection, so here we are.
require_version('GnomeKeyring', '1.0')
from gi.repository import Secret, GnomeKeyring

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
            self.collection = Secret.Collection.create_sync(*args)
        
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
    
    def create_item(self, service, username, password, notes):
        attributes = {'logo_type': '', 'logo': '', 'service': service,
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
        attributes = {'logo_type': '', 'logo': '', 'service': service,
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
        GnomeKeyring.change_password_sync(self.collection_name, None, None)
    
    def set_default(self):
        self.service.set_alias_sync('default', self.collection)
    
    def is_default(self):
        flags = Secret.CollectionFlags.NONE
        args = (self.service, 'default', flags)
        default = self.collection.for_alias_sync(*args)
        return default.get_label() == self.collection_name

