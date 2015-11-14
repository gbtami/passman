'''
Module for the Dialog classes
'''

from gi import require_version
require_version('Gtk', '3.0')
from gi.repository import Gtk


class Add(Gtk.Dialog):
    '''
    Add Dialog
    '''
    
    title = 'New Password'
    
    def __init__(self, app):
        buttons = ('_Cancel', Gtk.ResponseType.CANCEL,
                   '_OK', Gtk.ResponseType.OK)
        properties = {'use_header_bar': True}
        super().__init__(None, app.window, 0, buttons, **properties)
        # I set the title on the next line instead of the constructor because
        # this way the window width is recalculated to show the entire title.
        self.get_header_bar().set_custom_title(Gtk.Label(self.title))
        
        grid = Gtk.Grid()
        grid.set_column_spacing(app.spacing)
        grid.set_row_spacing(app.spacing)
        grid.set_border_width(app.spacing)
        
        button = Gtk.Button()
        args = ('image-missing', Gtk.IconSize.DIALOG)
        image = Gtk.Image.new_from_icon_name(*args)
        button.set_image(image)
        button.set_halign(Gtk.Align.CENTER)
        grid.attach(button, 0, 0, 2, 1)
        
        label = Gtk.Label('Service')
        self.service = Gtk.Entry()
        self.service.set_hexpand(True)
        grid.attach(label, 0, 1, 1, 1)
        grid.attach(self.service, 1, 1, 1, 1)
        
        label = Gtk.Label('Username')
        self.username = Gtk.Entry()
        grid.attach(label, 0, 2, 1, 1)
        grid.attach(self.username, 1, 2, 1, 1)
        
        label = Gtk.Label('Password')
        args = {'caps-lock-warning': True,
                'input-purpose': Gtk.InputPurpose.PASSWORD,
                'visibility': False}
        self.password = Gtk.Entry(**args)
        grid.attach(label, 0, 3, 1, 1)
        grid.attach(self.password, 1, 3, 1, 1)
        
        label = Gtk.Label('Notes')
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_min_content_height(64)
        scrolled_window.set_vexpand(True)
        self.notes = Gtk.TextView()
        scrolled_window.add(self.notes)
        grid.attach(label, 0, 4, 1, 1)
        grid.attach(scrolled_window, 1, 4, 1, 1)
        
        box = self.get_content_area()
        box.add(grid)
        
        self.show_all()

