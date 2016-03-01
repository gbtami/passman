# -*- coding: utf-8 -*-

'''
Module for the Windows Credentials util library
'''

import ctypes
from ctypes.wintypes import DWORD, LPTSTR, FILETIME, LPBYTE, \
                            PCREDENTIAL_ATTRIBUTE


class Credential(ctypes.Structure):
    '''
    Credential ctypes structure
    '''

    _fields_ = [('Flags', DWORD),
                ('Type', DWORD),
                ('TargetName', LPTSTR),
                ('Comment', LPTSTR),
                ('LastWritten', FILETIME),
                ('CredentialBlobSize', DWORD),
                ('CredentialBlob', LPBYTE),
                ('Persist', DWORD),
                ('AttributeCount', DWORD),
                ('Attributes', PCREDENTIAL_ATTRIBUTE),
                ('TargetAlias', LPTSTR),
                ('UserName', LPTSTR)]


class CredAttributes(ctypes.Structure):
    '''
    Credential Attributes ctypes structure
    '''
    
    _fields_ = [('logo', LPTSTR)]


class CredBlob(ctypes.Structure):
    '''
    Credential Blob ctypes structure
    '''
    
    _fields_ = [('password', LPTSTR), ('notes', LPTSTR)]


class LibCred:
    '''
    LibCred class
    '''
    
    advapi32 = ctypes.CDLL('Advapi32.dll')
    CRED_TYPE_GENERIC = DWORD(1)
    # Windows Vista Home Basic, Windows Vista Home Premium, Windows Vista
    # Starter, and Windows XP Home Edition:  This value is not supported.
    CRED_PERSIST_LOCAL_MACHINE = DWORD(2)
    
    def __init__(self):
        pass
    
    def get_collection(self):
        '''
        Not implemented on Windows
        '''
        pass
        
    def load_collection(self):
        '''
        Not implemented on Windows
        '''
        pass
    
    def create_item(self, logo, service, username, password, notes):
        cred_attributes_type = CredAttributes * 1
        attributes = cred_attributes_type(logo)
        blob = CredBlob(password, notes)
        cred_flags = DWORD(0)
        cred_type = self.CRED_TYPE_GENERIC
        cred_target_name = LPTSTR(service)
        cred_comment = LPTSTR('')
        cred_last_written = FILETIME(0)
        cred_credential_blob_size = ctypes.sizeof(blob)
        cred_credential_blob = ctypes.byref(blob)
        cred_persist = self.CRED_PERSIST_LOCAL_MACHINE
        cred_attribute_count = DWORD(len(attributes))
        cred_attributes = ctypes.byref(attributes)
        cred_target_alias = LPTSTR('passman')
        cred_username = LPTSTR(username)
        cred = Credential(cred_flags, cred_type, cred_target_name,
                          cred_comment, cred_last_written,
                          cred_credential_blob_size, cred_credential_blob,
                          cred_persist, cred_attribute_count, cred_attributes,
                          cred_target_alias, cred_username)
        self.advapi32.CredWrite(ctypes.byref(cred), 0)
    
    def edit_item(self, logo, service, username, password, notes):
        pass  
    
    def delete_item(self, item):
        pass
    
    def get_secret(self, item):
        pass
    
    def lock(self):
        '''
        Not implemented on Windows
        '''
        pass
    
    def unlock(self):
        '''
        Not implemented on Windows
        '''
        pass
    
    def is_locked(self):
        '''
        Not implemented on Windows
        '''
        pass
    
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

