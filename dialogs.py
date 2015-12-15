# -*- coding: utf-8 -*-

'''
Module for the Dialog classes
'''

import os
import os.path
import string
import shutil

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
        properties = {'use_header_bar': True}
        super().__init__(transient_for=app.window, **properties)
        self.add_buttons('_OK', Gtk.ResponseType.OK,
                         '_Cancel', Gtk.ResponseType.CANCEL)
        # I set the title on the next line instead of the constructor because
        # this way the window width is recalculated to show the entire title.
        self.get_header_bar().set_custom_title(Gtk.Label(label=self.title))
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
        
        label = Gtk.Label(label=_('<b>Service</b>'), **{'use-markup': True})
        frame = Gtk.Frame(label_widget=label)
        frame.set_shadow_type(Gtk.ShadowType.NONE)
        self.service = Gtk.Entry()
        self.service.set_activates_default(True)
        self.service.set_hexpand(True)
        frame.add(self.service)
        grid.attach(frame, 0, 1, 1, 1)
        self.service.grab_focus()
        
        label = Gtk.Label(label=_('<b>Username</b>'), **{'use-markup': True})
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
        super().__init__(transient_for=app.window, **properties)
        # I set the title on the next line instead of the constructor because
        # this way the window width is recalculated to show the entire title.
        self.get_header_bar().set_custom_title(Gtk.Label(label=self.title))
        
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
        is_default = self.app.main_view.secret.is_default()
        default.set_active(is_default)
        default.set_sensitive(not is_default)
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
        self.seconds_label = self.builder.get_object('seconds_label')
        self.interval.set_value(self.passwords['interval'])
        timeout = self.builder.get_object('timeout')
        timeout.set_active(self.passwords['timeout'])
        if not timeout.get_active():
            self.interval.set_sensitive(False)
            self.seconds_label.set_sensitive(False)
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
        self.store = Gtk.TreeStore(str, str, str, bool)
        values = ['Account', '', '', False]
        account = self.store.append(None, values)
        values = ['New', self.shortcuts['account-new'],
                  'account-new', True]
        self.store.append(account, values)
        values = ['Edit', self.shortcuts['account-edit'],
                  'account-edit', True]
        self.store.append(account, values)
        values = ['Delete', self.shortcuts['account-delete'],
                  'account-delete', True]
        self.store.append(account, values)
        values = ['View', '', '', False]
        view = self.store.append(None, values)
        values = ['Tile/List', self.shortcuts['view-tile-list'],
                  'view-tile-list', True]
        self.store.append(view, values)
        values = ['Size', self.shortcuts['view-size'],
                  'view-size', True]
        self.store.append(view, values)
        values = ['Application', '', '', False]
        application = self.store.append(None, values)
        values = ['Start', self.shortcuts['app-start'],
                  'app-start', True]
        self.store.append(application, values)
        values = ['Quit', self.shortcuts['app-quit'],
                  'app-quit',  True]
        self.store.append(application, values)
        tree = Gtk.TreeView(model=self.store)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn('Action', renderer, text=0)
        column.set_expand(True)
        column.set_alignment(0.5)
        tree.append_column(column)
        renderer = Gtk.CellRendererAccel()
        renderer.set_property('editable', True)
        renderer.set_alignment(0.5, 0.5)
        renderer.connect('accel-edited', self.on_accel_edited)
        column = Gtk.TreeViewColumn('Shortcut key', renderer,
                                    text=1, editable=3)
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
        status = toggle_button.get_active()
        self.general.set_boolean('autorun', status)
        if status:
            source = str(self.app.data_dir / self.app.autostart_file)
            destination = str(self.app.autostart_dir)
            shutil.copy(source, destination)
        else:
            file_path = str(self.app.autostart_dir / self.app.autostart_file)
            if os.path.isfile(file_path):
                os.remove(file_path)
    
    def on_autohide_toggled(self, toggle_button):
        self.general.set_boolean('autohide', toggle_button.get_active())
        self.app.main_view.autohide = True
    
    def on_reset_general_clicked(self, button):
        default = self.general.get_default_value('autorun')
        autorun = self.builder.get_object('autorun')
        autorun.set_active(default)
        default = self.general.get_default_value('autohide')
        autohide = self.builder.get_object('autohide')
        autohide.set_active(default)
    
    def on_reset_all_clicked(self, button):
        reset_general = self.builder.get_object('reset_general')
        reset_collections = self.builder.get_object('reset_collections')
        reset_passwords = self.builder.get_object('reset_passwords')
        reset_shortcuts = self.builder.get_object('reset_shortcuts')
        reset_general.clicked()
        reset_collections.clicked()
        reset_passwords.clicked()
        reset_shortcuts.clicked()
    
    def on_default_toggled(self, toggle_button):
        # This toggle button only ever gets activated by the app.
        toggle_button.set_sensitive(False)
        self.app.main_view.secret.set_default()
    
    def on_autolock_toggled(self, toggle_button):
        self.collection.set_boolean('autolock', toggle_button.get_active())
    
    def on_autounlock_toggled(self, toggle_button):
        self.collection.set_boolean('autounlock', toggle_button.get_active())
    
    def on_reset_collections_clicked(self, button):
        default = self.collection.get_default_value('autolock')
        autolock = self.builder.get_object('autolock')
        autolock.set_active(default)
        default = self.collection.get_default_value('autounlock')
        autounlock = self.builder.get_object('autounlock')
        autounlock.set_active(default)
    
    def on_password_size_value_changed(self, adjustment):
        value = GLib.Variant('q', adjustment.get_value())
        self.passwords.set_value('size', value)
    
    def on_timeout_toggled(self, toggle_button):
        if toggle_button.get_active():
            self.interval.set_sensitive(True)
            self.seconds_label.set_sensitive(True)
        else:
            self.interval.set_sensitive(False)
            self.seconds_label.set_sensitive(False)
        self.passwords.set_boolean('timeout', toggle_button.get_active())
    
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
        properties = {'use_header_bar': True}
        dialog = Gtk.Dialog(transient_for=self, **properties)
        dialog.add_buttons('_OK', Gtk.ResponseType.OK,
                           '_Cancel', Gtk.ResponseType.CANCEL)
        # I set the title on the next line instead of the constructor because
        # this way the window width is recalculated to show the entire title.
        label = Gtk.Label(label=_('Punctuation'))
        dialog.get_header_bar().set_custom_title(label)
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
    
    def on_reset_passwords_clicked(self, button):
        default = self.passwords.get_default_value('size')
        size = self.builder.get_object('size')
        size.set_value(default.get_uint16())
        default = self.passwords.get_default_value('timeout')
        timeout = self.builder.get_object('timeout')
        timeout.set_active(default)
        default = self.passwords.get_default_value('interval')
        interval = self.builder.get_object('interval')
        interval.set_value(default.get_uint16())
        default = self.passwords.get_default_value('lowercase')
        lowercase = self.builder.get_object('lowercase')
        lowercase.set_active(default)
        default = self.passwords.get_default_value('uppercase')
        uppercase = self.builder.get_object('uppercase')
        uppercase.set_active(default)
        default = self.passwords.get_default_value('digits')
        digits = self.builder.get_object('digits')
        digits.set_active(default)
        default = self.passwords.get_default_value('punctuation')
        punctuation = self.builder.get_object('punctuation')
        self.passwords.set_value('punctuation', default)
        # I don't want to trigger the toggled signal, I just want
        # the appearance to change, so I need to block the signal.
        punctuation.handler_block(self.handle)
        # The 'punctuation' setting is a list, It's boolean
        # value is False if it's empty, True otherwise.
        punctuation.set_active(self.passwords['punctuation'])
        punctuation.handler_unblock(self.handle)
        
    
    def on_accel_edited(self, cell_renderer_accel, path_string,
                        accel_key, accel_mods, hardware_keycode):
        cell_iter = self.store.get_iter_from_string(path_string)
        label = Gtk.accelerator_get_label(accel_key, accel_mods)
        self.store[cell_iter][1] = label
        value = self.store[cell_iter][2]
        self.shortcuts.set_value(value, GLib.Variant('s', label))
    
    def on_reset_shortcuts_clicked(self, button):
        for i in self.store:
            for j in i.iterchildren():
                default = self.shortcuts.get_default_value(j[2])
                self.shortcuts.set_value(j[2], default)
                j[1] = default.get_string()

