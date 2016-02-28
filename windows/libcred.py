# -*- coding: utf-8 -*-

'''
Module for the Windows Credentials util library
'''

import ctypes
from ctypes.wintypes import DWORD, LPTSTR, FILETIME, LPBYTE


class LibCred:
    '''
    LibCred class
    '''
    
    def __init__(self, app):
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
        pass
    
    def edit_item(self, item, logo, service, username, password, notes):
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


class CREDENTIAL(ctypes.Structure):
    '''
    Main Application class
    '''

    _fields_ = [("Flags", DWORD),
                ("Type", DWORD),
                ("TargetName", LPTSTR),
                ("Comment", LPTSTR),
                ("LastWritten", FILETIME),
                ("CredentialBlobSize", DWORD),
                ("CredentialBlob", LPBYTE),
                ("Persist", DWORD),
                ("AttributeCount", DWORD),
                ("Attributes", ctypes.c_wchar_p),
                ("TargetAlias", LPTSTR),
                ("UserName", LPTSTR)]

advapi32 = ctypes.CDLL('Advapi32.dll')
advapi32.CredReadW.restype = ctypes.c_bool
advapi32.CredReadW.argtypes = [ctypes.c_wchar_p, ctypes.c_int, ctypes.c_int, ctypes.POINTER(CREDENTIAL)]
target = "login.example.com"
pcred = ctypes.pointer(CREDENTIAL())
ok = advapi32.CredReadW(target,1,0,pcred)
cred = pcred.contents
print(ok, pcred, cred.UserName, cred.CredentialBlob)
