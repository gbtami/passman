# -*- coding: utf-8 -*-

'''
Module for the Windows Credentials util library
'''

import ctypes
from ctypes.wintypes import DWORD, LPWSTR, FILETIME, LPBYTE


class CredAttributes(ctypes.Structure):
    '''
    Credential Attributes ctypes structure
    '''
    
    _fields_ = [('logo', LPWSTR)]


class CredBlob(ctypes.Structure):
    '''
    Credential Blob ctypes structure
    '''
    
    _fields_ = [('password', LPWSTR), ('notes', LPWSTR)]


class Credential(ctypes.Structure):
    '''
    Credential ctypes structure
    '''

    _fields_ = [('Flags', DWORD),
                ('Type', DWORD),
                ('TargetName', LPWSTR),
                ('Comment', LPWSTR),
                ('LastWritten', FILETIME),
                ('CredentialBlobSize', DWORD),
                ('CredentialBlob', LPBYTE),
                ('Persist', DWORD),
                ('AttributeCount', DWORD),
                ('Attributes', CredAttributes),
                ('TargetAlias', LPWSTR),
                ('UserName', LPWSTR)]


class CredItem:
    '''
    Credential Virtual Item class.
    This class is used to implement methods that are present in the
    libsecret Item class and are used through out the program, but
    don't exist in the Windows Credentials API. This way, instead of
    adding a bunch of platform checks everywhere in the code, I use
    the same method calls and just change the class that handles them.
    '''
    
    def __init__(self, service, username):
        self.service = service
        self.username = username
    
    def get_attributes(self):
        pass
    
    def get_label(self):
        pass


class CredCollection:
    '''
    Credential Virtual Collection class. See CredItem class for more details.
    '''
    
    def __init__(self):
        self.items = []
    
    def get_items(self):
        return self.items


class LibCred:
    '''
    LibCred class
    '''
    
    advapi32 = ctypes.CDLL('Advapi32.dll')
    CRED_TYPE_GENERIC = DWORD(1)
    # Windows Vista Home Basic, Windows Vista Home Premium, Windows Vista
    # Starter, and Windows XP Home Edition:  This value is not supported.
    CRED_PERSIST_LOCAL_MACHINE = DWORD(2)
    # Windows Server 2003 and Windows XP:  This flag is not supported.
    CRED_ENUMERATE_ALL_CREDENTIALS = DWORD(1)
    
    def __init__(self, app):
        self.app = app
    
    def get_collection(self):
        self.collection = CredCollection()
        
    def load_collection(self):
        CredEnumerateW(None, CRED_ENUMERATE_ALL_CREDENTIALS,
                       ctypes.byref(DWORD()), ctypes.POINTER())
    
    def create_item(self, logo, service, username, password, notes):
        # If I add more attributes later, I need to increment this.
        cred_attributes_type = CredAttributes * 1
        attributes = cred_attributes_type(logo)
        blob = CredBlob(password, notes)
        cred_flags = DWORD(0)
        cred_type = self.CRED_TYPE_GENERIC
        # I make this the target_name because otherwise users with multiple
        # accounts on the same service won't be able to create those
        # credentials. They would end up just overwriting the same
        # credential for the service each time a new account is added.
        cred_target_name = LPWSTR(repr(service, username))
        cred_comment = LPWSTR('')
        cred_last_written = FILETIME(0, 0)
        cred_credential_blob_size = ctypes.sizeof(blob)
        cred_credential_blob = ctypes.byref(blob)
        cred_persist = self.CRED_PERSIST_LOCAL_MACHINE
        cred_attribute_count = DWORD(len(attributes))
        cred_attributes = ctypes.byref(attributes)
        # I keep this alias to mark which credentials are created using
        # PassMan, the ones that aren't, won't be displayed.
        cred_target_alias = LPWSTR('passman')
        cred_username = LPWSTR(username)
        cred = Credential(cred_flags, cred_type, cred_target_name,
                          cred_comment, cred_last_written,
                          cred_credential_blob_size, cred_credential_blob,
                          cred_persist, cred_attribute_count, cred_attributes,
                          cred_target_alias, cred_username)
        self.advapi32.CredWriteW(ctypes.byref(cred), 0)
        return CredItem(service, username)
    
    def edit_item(self, item, logo, service, username, password, notes):
        self.create_item(logo, service, username, password, notes)
    
    def delete_item(self, item):
        target = LPSTR(repr((item.service, item.username)))
        self.advapi32.CredDeleteW(target, self.CRED_TYPE_GENERIC, 0)
    
    def get_secret(self, item):
        target = LPSTR(repr((item.service, item.username)))
        out = ctypes.byref(Credential())
        self.advapi32.CredReadW(target, self.CRED_TYPE_GENERIC, 0, out)
        return (out.CredentialBlob.password, out.CredentialBlob.notes)
    
    def lock(self):
        '''
        Not implemented on Windows
        '''
        return True
    
    def unlock(self):
        '''
        Not implemented on Windows
        '''
        return True
    
    def change_password(self):
        '''
        Not implemented on Windows
        '''
        pass
    
    def set_default(self):
        '''
        Not implemented on Windows
        '''
        pass
    
    def is_default(self):
        '''
        Not implemented on Windows
        '''
        pass
