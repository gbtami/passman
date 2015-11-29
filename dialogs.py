'''
Module for the Dialog classes
'''

from gi import require_version
require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio
from passgen import PassGen

class Add(Gtk.Dialog):
    '''
    Add Dialog
    '''
    
    title = 'New Account'
    
    def __init__(self, app):
        self.app = app
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
        icon_theme = Gtk.IconTheme.get_default()
        pixbuf = icon_theme.load_icon('image-missing', 128, 0)
        image = Gtk.Image.new_from_pixbuf(pixbuf)
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
        
        expander = Gtk.Expander()
        expander.set_use_markup(True)
        expander.set_label('<b>Password</b>')
        expander.set_resize_toplevel(True)
        box = Gtk.Box()
        style = box.get_style_context()
        style.add_class('linked')
        args = {'caps-lock-warning': True,
                'input-purpose': Gtk.InputPurpose.PASSWORD}
        self.password = Gtk.Entry(**args)
        self.password.set_activates_default(True)
        self.password.set_text(PassGen(self.app).password)
        box.pack_start(self.password, True, True, 0)
        button = Gtk.Button()
        icon = Gio.ThemedIcon(name='view-refresh-symbolic')
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.connect('clicked', self.refresh_password)
        box.pack_end(button, False, False, 0)
        expander.add(box)
        grid.attach(expander, 0, 3, 1, 1)
        
        expander = Gtk.Expander()
        expander.set_use_markup(True)
        expander.set_label('<b>Notes</b>')
        expander.set_resize_toplevel(True)
        scrolled_window = Gtk.ScrolledWindow()
        expander.add(scrolled_window)
        scrolled_window.set_min_content_height(64)
        scrolled_window.set_vexpand(True)
        self.notes = Gtk.TextView()
        self.notes.set_accepts_tab(False)
        scrolled_window.add(self.notes)
        grid.attach(expander, 0, 4, 1, 1)
        
        box = self.get_content_area()
        box.add(grid)
        
        self.show_all()
    
    def refresh_password(self, button):
        self.password.set_text(PassGen(self.app).password)
    
    def get_data(self):
        service = self.service.get_text()
        username = self.username.get_text()
        password = self.password.get_text()
        buffer = self.notes.get_buffer()
        bounds = buffer.get_bounds()
        notes = buffer.get_text(bounds[0], bounds[1], False)
        return (service, username, password, notes)


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

