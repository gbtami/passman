# -*- coding: utf-8 -*-

'''
Module for the logo generation classes
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
from gi.repository import Gtk, GdkPixbuf, GLib, Pango


class LogoHeader:
    '''
    LogoHeader class
    '''
    
    size = 128
    interp = GdkPixbuf.InterpType.BILINEAR
    
    def __init__(self, app):
        self.service = ''
        self.app = app
        self.grid = Gtk.Grid()
        self.image = Gtk.Image()
        self.grid.attach(self.image, 0, 0, 1, 1)
        self.logo_server = LogoServer(app)
        self.spin = LogoSpin(self.grid, self.image)
        self.set_image()
    
    def set_default_image(self):
        '''
        This method sets the logo image to the default one.
        '''
        icon_theme = Gtk.IconTheme.get_default()
        default_image = icon_theme.load_icon('image-missing', self.size, 0)
        self.image.set_from_pixbuf(default_image)
        self.image.show()
    
    def set_service(self, service):
        '''
        This method sets the service name so it will later
        be used when setting the logo image.
        '''
        self.service = service
    
    def set_image(self, logo=''):
        '''
        This method will set the logo image based on a custom logo, or if that
        isn't provided it will try getting one locally first and remotely
        after, but only if the name is cached, this prevents remote calls to
        logos that don't exist. Preventing these remote calls is important
        because otherwise each letter input into the service field would
        trigger one such call.
        '''
        self.logo = logo
        if logo:
            pixbuf = self.logo_server.get_custom(logo)
            if pixbuf:
                self.set_pixbuf(pixbuf)
                return
            self.logo = ''
        logo_name = self.service.lower()
        pixbuf = self.logo_server.get_local(logo_name)
        if pixbuf:
            self.set_pixbuf(pixbuf)
        else:
            if self.logo_server.get_cache(logo_name, self.callback):
                self.spin.start(self.size)
            else:
                self.set_default_image()
    
    def set_pixbuf(self, pixbuf):
        '''
        This method sets the logo image based on a particular pixbuf,
        it's a lower level private method to be used by this class only.
        '''
        pixbuf = pixbuf.scale_simple(self.size, self.size, self.interp)
        self.image.set_from_pixbuf(pixbuf)
        self.image.show()
    
    def callback(self, logo_name):
        '''
        This method is called when an asynchronous call to get_remote is done.
        It's a private method that should only be called by this class.
        '''
        self.spin.stop()
        pixbuf = self.logo_server.get_local(logo_name)
        if pixbuf:
            self.set_pixbuf(pixbuf)
        else:
            self.set_default_image()
    
    def custom_logo_dialog(self, window):
        '''
        This method shows a dialog to let the user select a custom logo.
        '''
        dialog = Gtk.FileChooserDialog()
        dialog.set_transient_for(window)
        dialog.set_action(Gtk.FileChooserAction.OPEN)
        dialog.set_title(_('Select an image'))
        dialog.add_button(_('Open'), Gtk.ResponseType.OK)
        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.add_button(_('Cancel'), Gtk.ResponseType.CANCEL)
        image_filter = Gtk.FileFilter()
        image_filter.set_name(_('Images'))
        for f in GdkPixbuf.Pixbuf.get_formats():
            for mime_type in f.get_mime_types():
                image_filter.add_mime_type(mime_type)
        dialog.add_filter(image_filter)
        all_filter = Gtk.FileFilter()
        all_filter.set_name(_('All Files'))
        all_filter.add_pattern('*')
        dialog.add_filter(all_filter)
        dialog.set_current_folder(str(self.app.img_dir))
        response = dialog.run()
        logo_name = ''
        if response == Gtk.ResponseType.OK:
            logo_name = dialog.get_filename()
            self.set_image(logo_name)
        dialog.destroy()
        return logo_name
    
    def make_logo_tile(self, username, size, mode):
        '''
        This method is used to create a LogoTile from this current LogoHeader.
        '''
        return LogoTile(self.app, self.logo, self.service,
                        username, size, mode)


class LogoTile:
    '''
    LogoTile class
    '''
    
    interp = GdkPixbuf.InterpType.BILINEAR
    
    def __init__(self, app, logo, service, username, size, mode):
        self.app = app
        self.logo = logo
        self.service = service
        self.username = username
        self.size = size
        self.mode = mode
        self.grid = Gtk.Grid()
        self.image = Gtk.Image()
        self.grid.attach(self.image, 0, 0, 1, 1)
        self.label = Gtk.Label()
        self.label.set_justify(Gtk.Justification.CENTER)
        self.label.set_hexpand(True)
        self.label.set_ellipsize(Pango.EllipsizeMode.END)
        self.label.set_max_width_chars(4)
        if mode == 'grid':
            self.grid.set_halign(Gtk.Align.CENTER)
            self.grid.attach(self.label, 0, 1, 1, 1)
            self.separator = '\n'
        else:
            self.grid.set_halign(Gtk.Align.FILL)
            self.grid.attach(self.label, 1, 0, 1, 1)
            self.separator = '<b>: </b>'
        self.logo_server = LogoServer(app)
        self.spin = LogoSpin(self.grid, self.image)
        self.set_image(logo, True)
        self.set_label()
    
    def set_default_image(self):
        '''
        This method sets the logo image to the default one.
        '''
        icon_theme = Gtk.IconTheme.get_default()
        size = self.resolve_size()
        default_image = icon_theme.load_icon('image-missing', size, 0)
        self.image.set_from_pixbuf(default_image)
        self.image.show()
    
    def set_image(self, logo, remote=False):
        '''
        This method will set the logo image based on a custom logo, or if that
        isn't provided it will try getting one locally first and remotely
        later, but the remote call will only be performed if 'remote' is set.
        '''
        self.logo = logo
        if logo:
            pixbuf = self.logo_server.get_custom(logo)
            if pixbuf:
                self.set_pixbuf(pixbuf)
                return
            else:
                self.logo = ''
                self.set_default_image()
                return
        pixbuf = self.logo_server.get_local(self.service.lower())
        if pixbuf:
            self.set_pixbuf(pixbuf)
            return
        if remote:
            logo_name = self.service.lower()
            pixbuf = self.logo_server.get_remote(logo_name, self.callback)
            self.spin.start(self.resolve_size())
        else:
            self.set_default_image()
    
    def set_pixbuf(self, pixbuf):
        '''
        This method sets the logo image based on a particular pixbuf,
        it's a lower level private method to be used by this class only.
        '''
        size = self.resolve_size()
        pixbuf = pixbuf.scale_simple(size, size, self.interp)
        self.image.set_from_pixbuf(pixbuf)
        self.image.show()
    
    def callback(self, logo_name):
        '''
        This method is called when an asynchronous call to get_remote is done.
        It's a private method that should only be called by this class.
        '''
        self.spin.stop()
        pixbuf = self.logo_server.get_local(logo_name)
        if pixbuf:
            self.set_pixbuf(pixbuf)
        else:
            self.set_default_image()
    
    def set_mode(self, mode):
        '''
        This method updates logo size and text when the view mode is changed.
        '''
        self.mode = mode
        self.grid.remove(self.label)
        if mode == 'grid':
            self.grid.set_halign(Gtk.Align.CENTER)
            self.grid.attach(self.label, 0, 1, 1, 1)
            self.separator = '\n'
        else:
            self.grid.set_halign(Gtk.Align.FILL)
            self.grid.attach(self.label, 1, 0, 1, 1)
            self.separator = '<b>: </b>'
        self.set_image(self.logo)
        self.set_label()
    
    def set_size(self, size):
        '''
        This method updates logo size and text when the view size is changed.
        '''
        self.size = size
        self.set_image(self.logo)
        self.set_label()
    
    def set_label(self):
        '''
        This method updates the label text based on instance state.
        This is a private method that is used by the class only.
        '''
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
        '''
        This method returns the pixel size corresponding to the index value
        on the scale widget that is used to control the logo size.
        '''
        if self.mode == 'grid':
            return self.size * 32
        else:   
            return self.size * 24

    def make_logo_header(self):
        '''
        This method is used to create a LogoHeader from this current LogoTile.
        '''
        logo_header = LogoHeader(self.app)
        logo_header.set_service(self.service)
        logo_header.set_image(self.logo)
        return logo_header


class LogoServer:
    '''
    LogoImage class
    '''
    
    logo_server = 'http://idlecore.com/logo_server'
    timeout = 2
    
    def __init__(self, app):
        self.app = app
        self.load_cache()
    
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
        path = self.app.sys_data_dir / 'cache' / 'logo_name_cache.bz2'
        with bz2.open(str(path), 'rb') as logo_name_cache_file:
            logo_name_cache_bytes = logo_name_cache_file.read()
            self.logo_name_cache = set(pickle.loads(logo_name_cache_bytes))
    
    def get_cache(self, logo_name, callback):
        '''
        This method will get a remote logo image, if the name of the service
        is included on a local cache. This cache is used when the user is
        writing the name of the service, and the logo automatically changes
        when it detects a service it knows. If there was no cache, each time
        the user input a character, that new string would have to be sent to
        the logo server to check if it was indeed the name of a known service,
        and then give an answer back to the client. That would be inefficient.
        '''
        if logo_name in self.logo_name_cache:
            self.get_remote(logo_name, callback)
            return True
        return False
    
    def get_custom(self, path):
        '''
        This method returns the pixbuf of a custom logo, specified by the path.
        '''
        return GdkPixbuf.Pixbuf.new_from_file(path)
    
    def get_local(self, logo_name):
        '''
        This method tries getting a logo locally only, from the list of images
        the application collected during it's use, or none at all.
        '''
        if logo_name in os.listdir(str(self.app.img_dir)):
            path = str(self.app.img_dir / logo_name / 'logo.png')
            return GdkPixbuf.Pixbuf.new_from_file(path)
    
    def get_remote(self, logo_name, callback):
        '''
        This method gets a logo remotely. It will contact the logo server,
        and ask if there is a logo for the service name provided.
        '''
        target = self.get_remote_worker
        kwargs = {'logo_name': logo_name, 'callback': callback}
        thread = threading.Thread(target=target, kwargs=kwargs)
        thread.daemon = True
        thread.start()
    
    def get_remote_worker(self, logo_name, callback):
        '''
        This method will be run on a different thread, not to block the GUI.
        It's the method that actually does the work of making the request to
        the logo server, and waits for the response. With or without success,
        at the end of the request a user specified callback is called.
        '''
        try:
            r = requests.get(self.logo_server,
                             timeout=self.timeout,
                             params={'name': logo_name})
            if r.status_code == requests.codes.ok and len(r.content) > 0:
                with io.BytesIO(r.content) as in_memory_file:
                    logo_file = tarfile.open(fileobj=in_memory_file, mode='r:')
                    path = str(self.app.user_data_dir)
                    logo_file.extractall(path=path)
                    logo_file.close()
        except requests.exceptions.RequestException as e:
            logging.error(e)
        GLib.idle_add(callback, logo_name)


class LogoSpin:
    '''
    LogoSpin class
    '''
    
    def __init__(self, grid, image):
        self.grid = grid
        self.image = image
        self.spinner = Gtk.Spinner()
    
    def start(self, size):
        # It's possible the widget is already waiting for an image to load.
        if self.image.get_parent():
            self.grid.remove(self.image)
        else:
            self.grid.remove(self.spinner)
        self.spinner = Gtk.Spinner()
        self.spinner.set_size_request(size, size)
        self.grid.attach(self.spinner, 0, 0, 1, 1)
        self.spinner.start()
        self.spinner.show()
    
    def stop(self):
        # I need this condition because this might end up being
        # called after the dialog has already been closed.
        if self.spinner.get_parent():
            self.spinner.stop()
            self.grid.remove(self.spinner)
            self.grid.attach(self.image, 0, 0, 1, 1)

