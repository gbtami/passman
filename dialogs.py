'''
Module for the Dialog classes
'''

from gi import require_version
require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio


class Add(Gtk.Dialog):
    '''
    Add Dialog
    '''
    
    title = 'New Account'
    
    def __init__(self, app):
        buttons = ('_OK', Gtk.ResponseType.OK,
                   '_Cancel', Gtk.ResponseType.CANCEL)
        properties = {'use_header_bar': True}
        super().__init__(None, app.window, 0, buttons, **properties)
        # I set the title on the next line instead of the constructor because
        # this way the window width is recalculated to show the entire title.
        self.get_header_bar().set_custom_title(Gtk.Label(self.title))
        self.set_default_response(Gtk.ResponseType.OK)
        
        grid = Gtk.Grid()
        grid.set_column_spacing(app.spacing)
        grid.set_row_spacing(app.spacing)
        grid.set_border_width(app.spacing)
        
        button = Gtk.Button()
        args = ('image-missing', Gtk.IconSize.DIALOG)
        image = Gtk.Image.new_from_icon_name(*args)
        button.set_image(image)
        button.set_halign(Gtk.Align.CENTER)
        grid.attach(button, 0, 0, 1, 1)
        
        label = Gtk.Label('<b>Service</b>', **{'use-markup': True})
        frame = Gtk.Frame(label_widget=label)
        frame.set_shadow_type(Gtk.ShadowType.NONE)
        self.service = Gtk.Entry()
        self.service.set_activates_default(True)
        self.service.set_hexpand(True)
        frame.add(self.service)
        grid.attach(frame, 0, 1, 1, 1)
        self.service.grab_focus()
        
        label = Gtk.Label('<b>Username</b>', **{'use-markup': True})
        frame = Gtk.Frame(label_widget=label)
        frame.set_shadow_type(Gtk.ShadowType.NONE)
        self.username = Gtk.Entry()
        self.username.set_activates_default(True)
        frame.add(self.username)
        grid.attach(frame, 0, 2, 1, 1)
        
        label = Gtk.Label('<b>Password</b>', **{'use-markup': True})
        frame = Gtk.Frame(label_widget=label)
        frame.set_shadow_type(Gtk.ShadowType.NONE)
        password_grid = Gtk.Grid()
        password_grid.set_column_spacing(app.spacing)
        password_grid.set_row_spacing(app.spacing)
        frame.add(password_grid)
        args = {'caps-lock-warning': True,
                'input-purpose': Gtk.InputPurpose.PASSWORD,
                'visibility': False}
        self.password = Gtk.Entry(**args)
        self.password.set_hexpand(True)
        self.password.set_activates_default(True)
        password_grid.attach(self.password, 0, 0, 2, 1)
        check_button = Gtk.CheckButton('Show password')
        check_button.connect('toggled', self.show_password)
        check_button.set_halign(Gtk.Align.CENTER)
        password_grid.attach(check_button, 0, 1, 1, 1)
        button = Gtk.Button()
        icon = Gio.ThemedIcon(name='preferences-system')
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.set_halign(Gtk.Align.CENTER)
        button.connect('clicked', self.generate_rangom)
        password_grid.attach(button, 1, 1, 1, 1)
        grid.attach(frame, 0, 3, 1, 1)

        label = Gtk.Label('<b>Notes</b>', **{'use-markup': True})
        frame = Gtk.Frame(label_widget=label)
        frame.set_shadow_type(Gtk.ShadowType.NONE)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_min_content_height(64)
        scrolled_window.set_vexpand(True)
        self.notes = Gtk.TextView()
        self.notes.set_accepts_tab(False)
        scrolled_window.add(self.notes)
        frame.add(scrolled_window)
        grid.attach(frame, 0, 4, 1, 1)
        
        box = self.get_content_area()
        box.add(grid)
        
        self.show_all()
    
    def show_password(self, check_button):
        if check_button.get_active():
            self.password.set_visibility(True)
        else:
            self.password.set_visibility(False)
    
    def generate_random(self, obj, param):
        print('generate_random')


class Edit(Add):
    '''
    Edit Dialog
    '''
    
    title = 'Edit Account'
    
    def __init__(self, app, item):
        super().__init__(app)
        attributes = item.get_attributes()
        self.service.set_text(attributes['service'])
        self.username.set_text(attributes['username'])
        self.notes.get_buffer().set_text(attributes['notes'])
        item.load_secret_sync()
        self.password.set_text(item.get_secret().get_text())

