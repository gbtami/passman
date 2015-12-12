# -*- coding: utf-8 -*-

'''
Module for the Dialog classes
'''

import string

from gi import require_version
require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gio
from passgen import PassGen


class Add(Gtk.Dialog):
    '''
    Add Dialog
    '''
    
    title = _('New Account')
    
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
        
        label = Gtk.Label(_('<b>Service</b>'), **{'use-markup': True})
        frame = Gtk.Frame(label_widget=label)
        frame.set_shadow_type(Gtk.ShadowType.NONE)
        self.service = Gtk.Entry()
        self.service.set_activates_default(True)
        self.service.set_hexpand(True)
        frame.add(self.service)
        grid.attach(frame, 0, 1, 1, 1)
        self.service.grab_focus()
        
        label = Gtk.Label(_('<b>Username</b>'), **{'use-markup': True})
        frame = Gtk.Frame(label_widget=label)
        frame.set_shadow_type(Gtk.ShadowType.NONE)
        self.username = Gtk.Entry()
        self.username.set_activates_default(True)
        frame.add(self.username)
        grid.attach(frame, 0, 2, 1, 1)
        
        expander = Gtk.Expander()
        expander.set_use_markup(True)
        expander.set_label(_('<b>Password</b>'))
        expander.set_resize_toplevel(True)
        password_grid = Gtk.Grid()
        style = password_grid.get_style_context()
        style.add_class('linked')
        args = {'caps-lock-warning': True,
                'input-purpose': Gtk.InputPurpose.PASSWORD}
        self.password = Gtk.Entry(**args)
        self.password.set_activates_default(True)
        self.password.set_text(PassGen(self.app).password)
        self.password.set_hexpand(True)
        password_grid.add(self.password)
        button = Gtk.Button()
        icon = Gio.ThemedIcon(name='view-refresh-symbolic')
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.connect('clicked', self.refresh_password)
        password_grid.add(button)
        expander.add(password_grid)
        grid.attach(expander, 0, 3, 1, 1)
        
        expander = Gtk.Expander()
        expander.set_use_markup(True)
        expander.set_label(_('<b>Notes</b>'))
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
        box.set_border_width(0)
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
    
    title = _('Edit Account')
    
    def __init__(self, app, item):
        super().__init__(app)
        attributes = item.get_attributes()
        self.service.set_text(attributes['service'])
        self.username.set_text(attributes['username'])
        self.notes.get_buffer().set_text(attributes['notes'])
        item.load_secret_sync()
        self.password.set_text(item.get_secret().get_text())


class Preferences(Gtk.Dialog):
    '''
    Preferences Dialog
    '''
    
    title = _('Preferences')
    
    def __init__(self, app):
        self.app = app
        properties = {'use_header_bar': True}
        super().__init__(None, app.window, 0, None, **properties)
        # I set the title on the next line instead of the constructor because
        # this way the window width is recalculated to show the entire title.
        self.get_header_bar().set_custom_title(Gtk.Label(self.title))
        
        self.builder = Gtk.Builder.new_from_file(app.gui_glade)
        self.builder.connect_signals(self)
        notebook = self.builder.get_object('notebook')
        
        self.general = app.settings.get_child('general')
        autorun = self.builder.get_object('autorun')
        autorun.set_active(self.general['autorun'])
        autohide = self.builder.get_object('autohide')
        autohide.set_active(self.general['autohide'])
        
        self.collection = app.settings.get_child('collection')
        default = self.builder.get_object('default')
        default.set_active(self.collection['default'])
        autolock = self.builder.get_object('autolock')
        autolock.set_active(self.collection['autolock'])
        autounlock = self.builder.get_object('autounlock')
        autounlock.set_active(self.collection['autounlock'])
        
        self.passwords = app.settings.get_child('passwords')
        size = self.builder.get_object('size')
        size.set_value(self.passwords['size'])
        # 'self.interval' needs to be defined before 'timeout' because during
        # the check button construction there is a toggled signal that gets
        # processed, and I need to use self.interval on that signal's handler.
        self.interval = self.builder.get_object('interval')
        self.interval.set_value(self.passwords['interval'])
        timeout = self.builder.get_object('timeout')
        timeout.set_active(self.passwords['timeout'])
        if not timeout.get_active():
            self.interval.set_sensitive(False)
        lowercase = self.builder.get_object('lowercase')
        lowercase.set_active(self.passwords['lowercase'])
        uppercase = self.builder.get_object('uppercase')
        uppercase.set_active(self.passwords['uppercase'])
        digits = self.builder.get_object('digits')
        digits.set_active(self.passwords['digits'])
        punctuation = self.builder.get_object('punctuation')
        # I connect this signal here instead of glade because I need
        # the signal handle so I can block it when manually toggling.
        self.handle = punctuation.connect('toggled',
                                          self.on_punctuation_toggled)
        # I don't want to trigger the toggled signal, I just want
        # to appearance to change, so I need to block the signal.
        punctuation.handler_block(self.handle)
        # The 'punctuation' setting here is a list, it's boolean
        # value will be False if it's empty, True otherwise.
        punctuation.set_active(self.passwords['punctuation'])
        punctuation.handler_unblock(self.handle)
        
        self.shortcuts = app.settings.get_child('shortcuts')
        store = Gtk.TreeStore(str, str)
        account = store.append(None, ['Account', ''])
        store.append(account, ['New', self.shortcuts['account-new']])
        store.append(account, ['Edit', self.shortcuts['account-edit']])
        store.append(account, ['Delete', self.shortcuts['account-delete']])
        view = store.append(None, ['View', ''])
        store.append(view, ['Tile/List', self.shortcuts['view-time-list']])
        store.append(view, ['Size', self.shortcuts['view-size']])
        application = store.append(None, ['Application', ''])
        store.append(application, ['Start', self.shortcuts['app-start']])
        store.append(application, ['Quit', self.shortcuts['app-quit']])
        tree = Gtk.TreeView(store)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn('Action', renderer, text=0)
        column.set_expand(True)
        column.set_alignment(0.5)
        tree.append_column(column)
        renderer = Gtk.CellRendererAccel()
        renderer.set_alignment(0.5, 0.5)
        column = Gtk.TreeViewColumn('Shortcut key', renderer, text=1)
        column.set_expand(True)
        column.set_alignment(0.5)
        tree.append_column(column)
        tree.expand_all()
        shortcuts_parent = self.builder.get_object('shortcuts_scrolled_window')
        shortcuts_parent.add(tree)
        
        box = self.get_content_area()
        box.set_border_width(0)
        box.add(notebook)
        self.show_all()
    
    def on_autorun_toggled(self, toggle_button):
        self.general.set_boolean('autorun', toggle_button.get_active())
    
    def on_autohide_toggled(self, toggle_button):
        self.general.set_boolean('autohide', toggle_button.get_active())
    
    def on_default_toggled(self, toggle_button):
        self.collection.set_boolean('default', toggle_button.get_active())
    
    def on_autolock_toggled(self, toggle_button):
        self.collection.set_boolean('autolock', toggle_button.get_active())
    
    def on_autounlock_toggled(self, toggle_button):
        self.collection.set_boolean('autounlock', toggle_button.get_active())
    
    def on_timeout_toggled(self, toggle_button):
        if toggle_button.get_active():
            self.interval.set_sensitive(True)
        else:
            self.interval.set_sensitive(False)
        self.passwords.set_boolean('timeout', toggle_button.get_active())
    
    def on_password_size_value_changed(self, adjustment):
        value = GLib.Variant('q', adjustment.get_value())
        self.passwords.set_value('size', value)
    
    def on_timeout_interval_value_changed(self, adjustment):
        value = GLib.Variant('q', adjustment.get_value())
        self.passwords.set_value('interval', value)
    
    def on_lowercase_toggled(self, toggle_button):
        self.passwords.set_boolean('lowercase', toggle_button.get_active())
    
    def on_uppercase_toggled(self, toggle_button):
        self.passwords.set_boolean('uppercase', toggle_button.get_active())
    
    def on_digits_toggled(self, toggle_button):
        self.passwords.set_boolean('digits', toggle_button.get_active())
    
    def on_punctuation_toggled(self, toggle_button):
        buttons = ('_OK', Gtk.ResponseType.OK,
                   '_Cancel', Gtk.ResponseType.CANCEL)
        properties = {'use_header_bar': True}
        dialog = Gtk.Dialog(None, self, 0, buttons, **properties)
        # I set the title on the next line instead of the constructor because
        # this way the window width is recalculated to show the entire title.
        dialog.get_header_bar().set_custom_title(Gtk.Label(_('Punctuation')))
        dialog.set_default_response(Gtk.ResponseType.OK)
        box = dialog.get_content_area()
        box.set_border_width(0)
        grid = self.builder.get_object('grid')
        box.add(grid)
        
        for c in self.passwords['punctuation']:
            key = self.builder.get_object(str(c))
            key.set_active(True)

        response = dialog.run()
        punctuation = []
        if response == Gtk.ResponseType.OK:
            for c in ' ' + string.punctuation:
                key = self.builder.get_object(str(ord(c)))
                if key.get_active():
                    punctuation.append(ord(c))
            value = GLib.Variant('aq', punctuation)
            self.passwords.set_value('punctuation', value)
        
        # I don't want to trigger the toggled signal, I just want
        # the appearance to change, so I need to block the signal.
        toggle_button.handler_block(self.handle)
        # The 'punctuation' setting is a list, It's boolean
        # value is False if it's empty, True otherwise.
        toggle_button.set_active(self.passwords['punctuation'])
        toggle_button.handler_unblock(self.handle)
        # I remove the grid from the dialog before destroying it so that it
        # doesn't get destroyed as well, since the user might decide to reopen
        # the punctuation dialog again, and this way I don't need to create a
        # new builder object, the dialog is the only widget recreated.
        box.remove(grid)
        dialog.destroy()
    
    def on_all_clicked(self, button):
        for c in ' ' + string.punctuation:
            key = self.builder.get_object(str(ord(c)))
            key.set_active(True)
    
    def on_none_clicked(self, button):
        for c in ' ' + string.punctuation:
            key = self.builder.get_object(str(ord(c)))
            key.set_active(False)

