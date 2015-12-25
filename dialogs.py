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
require_version('Keybinder', '3.0')
from gi.repository import Gtk, GLib, Gio, Keybinder

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
        app.main_view.secret.get_secret(item)


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
        default_button = self.builder.get_object('default_button')
        default_label = self.builder.get_object('default_label')
        is_default = self.app.main_view.secret.is_default()
        default_button.set_sensitive(not is_default)
        text = ''
        if not is_default:
            text = '<b>not</b> '
        label = 'This collection is {}the system\'s default.'.format(text)
        default_label.set_markup(label)
        autolock = self.builder.get_object('autolock')
        autolock.set_active(self.collection['autolock'])
        
        self.passwords = app.settings.get_child('passwords')
        size = self.builder.get_object('size')
        size.set_value(self.passwords['size'])
        timeout = self.builder.get_object('timeout')
        is_active = self.passwords['timeout']
        timeout.set_active(is_active)
        interval = self.builder.get_object('interval')
        seconds_label = self.builder.get_object('seconds_label')
        interval.set_sensitive(is_active)
        seconds_label.set_sensitive(is_active)
        interval.set_value(self.passwords['interval'])
        
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
        self.store = Gtk.TreeStore(str, str, str, bool, str)
        values = [('Account', '', False, ''),
                  ('New', 'account-new', True, 'app.new'),
                  ('Edit', 'account-edit', True, 'app.edit'),
                  ('Delete', 'account-delete', True, 'app.delete'),
                  ('View', '', False, ''),
                  ('Tile/List', 'view-mode', True, 'app.view_mode'),
                  ('Size', 'view-size', True, 'app.view_size'),
                  ('Application', '', False, ''),
                  ('Start', 'app-show', True, 'app.show'),
                  ('Quit', 'app-quit',  True, 'app.quit')]
        for tree_label, schema_key, edit, action in values:
            if edit:
                accel_name = self.shortcuts[schema_key]
                accel_key, accel_mods = Gtk.accelerator_parse(accel_name)
                accel_label = Gtk.accelerator_get_label(accel_key, accel_mods)
                values = [tree_label, accel_label, schema_key, True, action]
                self.store.append(node, values)
            else:
                node = self.store.append(None, [tree_label, '', '', False, ''])
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
        renderer.connect('accel-cleared', self.on_accel_cleared)
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
        status = toggle_button.get_active()
        self.general.set_boolean('autohide', status)
        self.app.main_view.autohide = status
    
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
    
    def on_default_button_clicked(self, button):
        button.set_sensitive(False)
        self.app.main_view.secret.set_default()
        label = 'This collection is the system\'s default.'
        default_label = self.builder.get_object('default_label')
        default_label.set_markup(label)
    
    def on_change_password_clicked(self, button):
        self.app.main_view.secret.change_password()
    
    def on_autolock_toggled(self, toggle_button):
        status = toggle_button.get_active()
        self.collection.set_boolean('autolock', status)
        self.app.main_view.autolock = status
    
    def on_reset_collections_clicked(self, button):
        default = self.collection.get_default_value('autolock')
        autolock = self.builder.get_object('autolock')
        autolock.set_active(default)
    
    def on_password_size_value_changed(self, adjustment):
        value = GLib.Variant('q', adjustment.get_value())
        self.passwords.set_value('size', value)
    
    def on_timeout_toggled(self, toggle_button):
        is_active = toggle_button.get_active()
        interval = self.builder.get_object('interval')
        interval.set_sensitive(is_active)
        seconds_label = self.builder.get_object('seconds_label')
        seconds_label.set_sensitive(is_active)
        self.app.main_view.timeout = is_active
        self.passwords.set_boolean('timeout', is_active)
    
    def on_timeout_interval_value_changed(self, adjustment):
        value = GLib.Variant('q', adjustment.get_value())
        self.passwords.set_value('interval', value)
        self.app.main_view.interval = adjustment.get_value()
    
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
        accel_name = Gtk.accelerator_name(accel_key, accel_mods)
        label = Gtk.accelerator_get_label(accel_key, accel_mods)
        self.store[cell_iter][1] = label
        if self.store[cell_iter][4] == 'app.show':
            self.set_app_show(accel_name)
        else:
            self.set_accel(accel_name, self.store[cell_iter][4])
        value = self.store[cell_iter][2]
        self.shortcuts.set_value(value, GLib.Variant('s', accel_name))
    
    def on_accel_cleared(self, cell_renderer_accel, path_string):
        cell_iter = self.store.get_iter_from_string(path_string)
        self.store[cell_iter][1] = ''
        if self.store[cell_iter][4] == 'app.show':
            self.set_app_show('')
        else:
            self.set_accel('', self.store[cell_iter][4])
        value = self.store[cell_iter][2]
        self.shortcuts.set_value(value, GLib.Variant('s', ''))
    
    def set_accel(self, accel_name, action):
        accels = self.app.get_accels_for_action(action)
        if accels:
            self.app.remove_accelerator(action, None)
        if accel_name:
            self.app.set_accels_for_action(action, [accel_name])
    
    def set_app_show(self, new):
        '''
        We expect gsettings hasn't been changed yet.
        '''
        Keybinder.unbind(self.shortcuts['app-show'])
        Keybinder.bind(new, self.app.add_show_shortcut)
    
    # Can't check if the shortcut is already taken by some other function.
    # Doesn't update in real time.
    def set_app_show_test(self):
        schema = 'org.gnome.settings-daemon.plugins.media-keys'
        key = 'custom-keybindings'
        custom = '/{}/{}/passman/'.format(schema.replace('.', '/'), key)
        schema = schema + '.' + key[:-1]
        settings = Gio.Settings(schema=schema, path=custom)
        shortcuts = self.app.settings.get_child('shortcuts')
        settings.set_string('binding', shortcuts['app-show'])
    
    def on_reset_shortcuts_clicked(self, button):
        for i in self.store:
            for j in i.iterchildren():
                default = self.shortcuts.get_default_value(j[2])
                accel_name = default.get_string()
                if j[4] == 'app.show':
                    self.set_app_show(accel_name)
                else:
                    self.set_accel(accel_name, j[4])
                accel_key, accel_mods = Gtk.accelerator_parse(accel_name)
                accel_label = Gtk.accelerator_get_label(accel_key, accel_mods)
                j[1] = accel_label
                self.shortcuts.set_value(j[2], default)

