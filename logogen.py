# -*- coding: utf-8 -*-

'''
Module for the LogoGen class
'''

from gi import require_version
require_version('Gtk', '3.0')
require_version('Pango', '1.0')
from gi.repository import Gtk, Gio, Pango

import dialogs


class LogoGen:
    '''
    LogoGen class
    '''
    
    def __init__(self, app, service, username):
        self.service = service
        self.username = username
        size = app.window.get_titlebar().view_size
        self.size = size
        view_mode = app.window.get_titlebar().view_mode
        self.mode = view_mode
        self.grid = Gtk.Grid()
        self.image = Gtk.Image()
        self.label = Gtk.Label()
        self.label.set_justify(Gtk.Justification.CENTER)
        self.label.set_hexpand(True)
        self.label.set_ellipsize(Pango.EllipsizeMode.END)
        self.label.set_max_width_chars(4)
        self.grid.add(self.image)
        self.grid.add(self.label)
        self.set_view(view_mode)
        self.set_size(size)
    
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

