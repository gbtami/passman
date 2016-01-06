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
import logging

import requests

from gi import require_version
require_version('Gtk', '3.0')
require_version('GdkPixbuf', '2.0')
require_version('Pango', '1.0')
from gi.repository import Gtk, GdkPixbuf, Gio, GLib, Pango

import dialogs


class LogoGen:
    '''
    LogoGen class
    '''
    
    logo_size = 128
    logo_server = 'http://localhost:8080/logo_server/'
    timeout = 2
    interp = GdkPixbuf.InterpType.BILINEAR
    
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.img_dir = data_dir / 'images'
        self.size = 4
        self.mode = 'grid'
        self.logo = ''
        self.grid = Gtk.Grid()
        self.image = Gtk.Image()
        self.grid.add(self.image)
        self.make_default_image()
        self.set_default_image()
        self.load_cache()
    
    def make_default_image(self):
        icon_theme = Gtk.IconTheme.get_default()
        size = self.resolve_size()
        self.default_image = icon_theme.load_icon('image-missing', size, 0)
    
    def set_default_image(self):
        size = self.resolve_size()
        image = self.default_image.scale_simple(size, size, self.interp)
        self.image.set_from_pixbuf(image)
        self.image.show()
    
    def load_cache(self):
        '''
        When the user is creating a new password, the service field is set
        so that when there is a change the client will automatically see if
        there is a logo by that name. This created a problem because each
        character input by the user would generate a GET request to the logo
        server. So we created a local cache of popular names, that is used
        to check if the text on the Service entry is an actual logo name,
        and if it is, it's requested, locally or remotely.
        This will leave some gaps as the cache of names might not include all
        available in the logo server, but when the password is created, there
        is one last unconditional logo check that will catch those cases.
        '''
        path = self.data_dir / 'logo_name_cache.bz2'
        with bz2.open(str(path), 'rb') as logo_name_cache_file:
            logo_name_cache_bytes = logo_name_cache_file.read()
            self.logo_name_cache = pickle.loads(logo_name_cache_bytes)
    
    def make_grid(self, logo, service, username, size, mode):
        self.service = service
        logo_name = service.lower()
        self.username = username
        self.size = size
        self.mode = mode
        self.logo = logo
        if not self.set_local_logo(logo_name):
            self.set_remote_logo(logo_name)
        self.label = Gtk.Label()
        self.label.set_justify(Gtk.Justification.CENTER)
        self.label.set_hexpand(True)
        self.label.set_ellipsize(Pango.EllipsizeMode.END)
        self.label.set_max_width_chars(4)
        self.grid.add(self.label)
        self.set_view(mode)
        self.set_size(size)
    
    def set_cached_logo(self, service):
        self.service = service
        logo_name = service.lower()
        if logo_name in self.logo_name_cache:
            if not self.set_local_logo(logo_name):
                self.set_remote_logo(logo_name)
        else:
            self.set_default_image()
        return False
    
    def set_remote_logo(self, logo_name):
        target = self.set_remote_logo_worker
        kwargs = {'logo_name': logo_name}
        thread = threading.Thread(target=target, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        self.start_spin()
    
    def set_local_logo(self, logo_name):
        if self.logo:
            self.set_logo(self.logo)
            return True
        else:
            if logo_name in os.listdir(str(self.img_dir)):
                if logo_name == self.service.lower():
                    path = str(self.img_dir / logo_name / 'logo.png')
                    self.set_logo(path)
                return True
            else:
                self.set_default_image()
                return False
    
    def set_remote_logo_worker(self, logo_name):
        import time
        time.sleep(2)
        url = '{}{}'.format(self.logo_server, logo_name)
        try:
            r = requests.get(url, timeout=self.timeout)
            if r.status_code == requests.codes.ok and len(r.content) > 0:
                with io.BytesIO(r.content) as in_memory_file:
                    logo_file = tarfile.open(fileobj=in_memory_file, mode='r:')
                    path = str(self.data_dir)
                    logo_file.extractall(path=path)
                    logo_file.close()
        except requests.exceptions.RequestException as e:
            logging.error(e)
        GLib.idle_add(self.set_remote_logo_finish, logo_name)
    
    def set_remote_logo_finish(self, logo_name):
        self.stop_spin()
        self.set_local_logo(logo_name)
    
    def set_view(self, mode):
        self.mode = mode
        self.grid.remove(self.label)
        if mode == 'list':
            self.grid.set_halign(Gtk.Align.FILL)
            self.grid.set_orientation(Gtk.Orientation.HORIZONTAL)
            self.separator = '<b>: </b>'
        else:
            self.grid.set_halign(Gtk.Align.CENTER)
            self.grid.set_orientation(Gtk.Orientation.VERTICAL)
            self.separator = '\n'
        self.grid.add(self.label)
        self.set_local_logo(self.service.lower())
        self.set_label()
    
    def set_size(self, size):
        self.size = size
        self.set_local_logo(self.service.lower())
        self.set_label()
    
    def set_label(self):
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
    
    def resolve_size(self):
        if self.mode == 'list':
            return self.size * 24
        else:   
            return self.size * 32
    
    def start_spin(self):
        # It's possible the widget is already waiting for an image to load.
        if self.image.get_parent():
            self.grid.remove(self.image)
        else:
            self.grid.remove(self.spinner)
        self.spinner = Gtk.Spinner()
        size = self.resolve_size()
        self.spinner.set_size_request(size, size)
        self.grid.attach(self.spinner, 0, 0, 1, 1)
        self.spinner.start()
        self.spinner.show()
    
    def stop_spin(self):
        # I need this condition because this might end up being
        # called after the dialog has already been closed.
        if self.spinner.get_parent():
            self.grid.remove(self.spinner)
            self.spinner.stop()
            self.grid.attach(self.image, 0, 0, 1, 1)
    
    def custom_logo_dialog(self, window):
        dialog = Gtk.FileChooserDialog()
        dialog.set_transient_for(window)
        dialog.set_action(Gtk.FileChooserAction.OPEN)
        dialog.set_title('Select an image')
        dialog.add_button('Open', Gtk.ResponseType.OK)
        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.add_button('Cancel', Gtk.ResponseType.CANCEL)
        image_filter = Gtk.FileFilter()
        image_filter.set_name('Images')
        for f in GdkPixbuf.Pixbuf.get_formats():
            for mime_type in f.get_mime_types():
                image_filter.add_mime_type(mime_type)
        dialog.add_filter(image_filter)
        all_filter = Gtk.FileFilter()
        all_filter.set_name('All Files')
        all_filter.add_pattern('*')
        dialog.add_filter(all_filter)
        dialog.set_current_folder(str(self.img_dir))
        response = dialog.run()
        logo_name = ''
        if response == Gtk.ResponseType.OK:
            logo_name = dialog.get_filename()
            self.logo = logo_name
            self.set_logo(logo_name)
        dialog.destroy()
        return logo_name
    
    def set_logo(self, logo):
        image = Gtk.Image.new_from_file(logo)
        size = self.resolve_size()
        interp = GdkPixbuf.InterpType.BILINEAR
        pixbuf = image.get_pixbuf()
        if pixbuf:
            pixbuf = pixbuf.scale_simple(size, size, self.interp)
            self.image.set_from_pixbuf(pixbuf)
        else:
            self.set_default_image()

