'''
Module for the libsecret API
'''

from gi import require_version
require_version('Secret', '1')
from gi.repository import Secret

class LibSecret:
    '''
    LibSecret class
    '''
    
    def __init__(self, collection_name, schema_name):
        self.collection_name = collection_name
        self.make_schema(schema_name)
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
    
    def delete_item(self, item):
        item.delete_sync()

