# -*- coding: utf-8 -*-

'''
Module for the LogoGen class
'''

import os
import io
import bz2
import tarfile
import pickle
import threading

import requests

from gi import require_version
require_version('Gtk', '3.0')
require_version('Pango', '1.0')
from gi.repository import Gtk, Gio, GLib, Pango

import dialogs


class LogoGen:
    '''
    LogoGen class
    '''
    
    logo_size = 128
    logo_server = 'http://localhost:8080/logo_server/'
    
    def __init__(self, app, service, username, size, mode,
                 refresh_function=lambda:None):
        self.app = app
        self.service = service
        self.username = username
        self.size = size
        self.mode = mode
        self.refresh_function = refresh_function
        self.grid = Gtk.Grid()
        self.image = Gtk.Image()
        self.label = Gtk.Label()
        self.label.set_justify(Gtk.Justification.CENTER)
        self.label.set_hexpand(True)
        self.label.set_ellipsize(Pango.EllipsizeMode.END)
        self.label.set_max_width_chars(4)
        self.grid.add(self.image)
        self.grid.add(self.label)
        self.set_view(self.mode)
        self.set_size(self.size)
        
        self.load_cache()
        icon_theme = Gtk.IconTheme.get_default()
        if mode == 'grid':
            size = size * 32
        else:
            size = size * 24
        self.missing_image = icon_theme.load_icon('image-missing', size, 0)
    
    def load_cache(self):
        path = self.app.data_dir / 'logo_name_cache.bz2'
        with bz2.open(str(path), 'rb') as logo_name_cache_file:
            logo_name_cache_bytes = logo_name_cache_file.read()
            self.logo_name_cache = pickle.loads(logo_name_cache_bytes)
    
    def update_local(self, logo_name):
        if logo_name in self.logo_name_cache:
            if not self.get_local_logo(logo_name):
                self.update_remote(logo_name)
                return False
        else:
            self.image.set_from_pixbuf(self.missing_image)
        self.refresh_function()
        return True
    
    def update_remote(self, logo_name):
        target = self.update_remote_worker
        kwargs = {'logo_name': logo_name}
        thread = threading.Thread(target=target, kwargs=kwargs)
        thread.daemon = True
        thread.start()
    
    def get_local_logo(self, logo_name):
        if logo_name in os.listdir(str(self.app.img_dir)):
            if logo_name == self.service:
                path = str(self.app.img_dir / logo_name / 'logo.png')
                self.image.set_from_file(path)
                self.refresh_function()
            return True
        return False
    
    def wrap_get_local_logo(self, logo_name):
        '''
        I need this wrapper to call this method from GLib.idle_add.
        So that it will automatically stop when it returns False.
        I need the actual get_local_logo method to return True sometimes.
        '''
        self.get_local_logo(logo_name)
        return False
    
    def update_remote_worker(self, logo_name):
        import time
        time.sleep(2)
        url = '{}{}'.format(self.logo_server, logo_name)
        r = requests.get(url)
        if r.status_code == requests.codes.ok:
            with io.BytesIO(r.content) as in_memory_file:
                logo_file = tarfile.open(fileobj=in_memory_file, mode='r:')
                path = str(self.app.data_dir)
                logo_file.extractall(path=path)
                logo_file.close()
        GLib.idle_add(self.wrap_get_local_logo, logo_name)
    
    def set_view(self, mode):
        self.grid.remove(self.label)
        self.mode = mode
        if mode == 'list':
            self.grid.set_halign(Gtk.Align.FILL)
            self.grid.set_orientation(Gtk.Orientation.HORIZONTAL)
            self.separator = '<b>: </b>'
        else:
            self.grid.set_halign(Gtk.Align.CENTER)
            self.grid.set_orientation(Gtk.Orientation.VERTICAL)
            self.separator = '\n'
        self.grid.add(self.label)
        self._set_label()
        self._set_image()
    
    def set_size(self, size):
        self.size = size
        self._set_image()
        self._set_label()
    
    def _set_image(self):
        icon_theme = Gtk.IconTheme.get_default()
        if self.mode == 'list':
            size = self.size * 24
        else:   
            size = self.size * 32
        pixbuf = icon_theme.load_icon('image-missing', size, 0)
        self.image.set_from_pixbuf(pixbuf)
    
    def _set_label(self):
        if not self.username:
            self.separator = ''
        text = '<b>{}</b>{}{}'.format(self.service,
                                      self.separator,
                                      self.username)
        if self.mode == 'grid':
            if self.size == 1:
                text = '{}{}{}'.format('<small>' * 2, text, '</small>' * 2)
            elif self.size == 2:
                text = '{}{}{}'.format('<small>' * 1, text, '</small>' * 1)
            elif self.size == 3:
                text = '{}{}{}'.format('<big>' * 0, text, '</big>' * 0)
            elif self.size == 4:
                text = '{}{}{}'.format('<big>' * 1, text, '</big>' * 1)
        else:
            if self.size == 1:
                text = '{}{}{}'.format('<small>' * 1, text, '</small>' * 1)
            elif self.size == 2:
                text = '{}{}{}'.format('<big>' * 1, text, '</big>' * 1)
            elif self.size == 3:
                text = '{}{}{}'.format('<big>' * 3, text, '</big>' * 3)
            elif self.size == 4:
                text = '{}{}{}'.format('<big>' * 5, text, '</big>' * 5)
        self.label.set_markup(text)

