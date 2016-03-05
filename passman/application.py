# -*- coding: utf-8 -*-

'''
Module for the Application class
'''

import logging
import os
import platform
import pathlib

from gi import require_version
require_version('Gtk', '3.0')
require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, Gio, GLib
if platform.system() == 'Windows':
    import pyHook
else:
    require_version('Keybinder', '3.0')
    from gi.repository import Keybinder

from .header_bar import HeaderBar
from .main_view import MainView
from .dialogs import PreferencesDialog


class Application(Gtk.Application):
    '''
    Main Application class
    '''
    
    name = 'PassMan'
    title = name
    version = '0.1.0'
    icon = 'dialog-password'
    website = 'https://github.com/xor/passman'
    spacing = 8
    app_id = 'com.idlecore.passman'
    app_dir = name.lower()
    user_data_dir = pathlib.Path(GLib.get_user_data_dir()) / app_dir
    if platform.system() == 'Windows':
        # Currently working directory
        sys_data_dir = pathlib.Path()
    else:
        sys_data_dir = pathlib.Path(GLib.get_system_data_dirs()[-1]) / app_dir
    log_dir = user_data_dir / 'logs'
    log_file = str(log_dir / (name.lower() + '.log'))
    img_dir = user_data_dir / 'images'
    gui_glade = str(sys_data_dir / 'gui' / 'glade')
    gui_ui = str(sys_data_dir / 'gui' / 'ui')
    schema_id = app_id
    
    def __init__(self):
        # Despite many examples showing __init__ being called with the
        # argument flags=Gio.ApplicationFlags.FLAGS_NONE, this is the
        # default behaviour already, so it's not required.
        super().__init__(application_id=self.app_id)
        description = ('Start the application hidden. '
                       'Useful when you start the application at login.')
        self.add_main_option('hide', 0, GLib.OptionFlags.NONE,
                             GLib.OptionArg.NONE, description, None)
        description = ('Autostart the application on login.')
        self.add_main_option('autostart', 0, GLib.OptionFlags.NONE,
                             GLib.OptionArg.NONE, description, None)
        self.hide_flag = False
        self.started_hidden = False
        self.first_run = True
        self.connect('activate', self.on_activate)
        self.connect('startup', self.on_startup)
        self.connect('shutdown', self.on_shutdown)
        self.connect('handle-local-options', self.on_handle_local_options)
    
    def on_startup(self, app):
        '''
        This method handles the startup signal.
        As per GNOME guidelines this is where most of
        the work to create the window should be done.
        '''
        self.create_directories()
        
        self.settings = Gio.Settings(schema=self.schema_id + '.preferences')
        self.win_settings = Gio.Settings(schema=self.schema_id + '.window')
        self.width = self.win_settings['width']
        self.height = self.win_settings['height']
        self.general_settings = self.settings.get_child('general')
        self.closehide = self.general_settings['closehide']
        self.about_dialog = None
        self.preferences_dialog = None
        logging.basicConfig(filename=self.log_file, level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s: %(message)s')
        
        self.window = Gtk.ApplicationWindow(application=app)
        self.window.connect('size-allocate', self.on_size_allocate)
        self.window.connect('delete-event', self.on_window_delete)
        self.window.set_title(self.title)
        self.window.set_default_size(self.width, self.height)
        self.window.set_position(Gtk.WindowPosition.MOUSE)
        self.window.set_titlebar(HeaderBar(self))
        # We need to set the icon here as a backup, the gnome system monitor
        # for instance, and for whatever reason, doesn't choose the right icon
        # sometimes, particularly after hiding the window, and showing again.
        self.window.set_icon_name(self.icon)
        self.main_view = MainView(self)
        self.window.add(self.main_view)
        
        self.add_actions()
        builder = Gtk.Builder.new_from_file(self.gui_ui)
        app_menu = builder.get_object('app_menu')
        self.set_app_menu(app_menu)
        
        self.add_global_shortcut()
    
    def add_global_shortcut(self):
        shortcuts = self.settings.get_child('shortcuts')
        if platform.system() == 'Windows':
            self.modifiers = {Gdk.ModifierType.GDK_SHIFT_MASK:
                                  ['VK_SHIFT'],
                              Gdk.ModifierType.GDK_CONTROL_MASK:
                                  ['VK_CONTROL'],
                              Gdk.ModifierType.GDK_MOD1_MASK:
                                  ['VK_MENU'],
                              Gdk.ModifierType.GDK_SUPER_MASK:
                                  ['VK_LWIN', 'VK_RWIN']}
            hook_manager = pyHook.HookManager()
            hook_manager.KeyDown = self.on_keyboard_event
            self.set_hotkey(shortcuts['app-show'])
            hook_manager.HookKeyboard()
        else:
            Keybinder.init()
            Keybinder.bind(shortcuts['app-show'], self.on_show)
    
    def set_hotkey(self, new):
        key, mods = Gtk.accelerator_parse(new)
        self.virtual_keys = []
        for mod, vks in self.modifiers.items():
            if mod & mods:
                self.virtual_keys.extend(vks)
        self.hotkey = key
    
    def on_keyboard_event(self, event):
        '''
        This method is used in Windows only.
        It will get keyboard events and find
        the ones matching the global shortcut.
        '''
        if event.Ascii == self.hotkey:
            for vk in self.virtual_keys:
                if not HookManager.GetKeyState(HookConstants.VKeyToID(vk)):
                    break
            else:
                self.activate()
                return False
        # Return True to pass the event to other handlers.
        return True
    
    def create_directories(self):
        '''
        This method makes sure all the directories that are needed
        by this application either already exist or are created.
        '''
        if not self.user_data_dir.exists():
            self.user_data_dir.mkdir(mode=0o700)
        if not self.log_dir.exists():
            self.log_dir.mkdir(mode=0o700)
        if not self.img_dir.exists():
            self.img_dir.mkdir(mode=0o700)
    
    def on_window_delete(self, widget, event):
        '''
        The window should hide most of the time.
        The program is supposed to startup quickly, and the best way to do
        that it's to not startup at all. So each time the user just wants
        the window to go away, it gets hidden, even when the close button
        is clicked. Only when the user makes an explicit effort to quit it
        should that actually be done. This can be achieved by either using
        the app menu's Quit option, or by pressing the quit shortcut.
        '''
        if self.closehide:
            self.main_view.window_hide()
            # Stop other handlers from running.
            return True
        else:
            return False
    
    def on_show(self, keystring):
        '''
        Getting the show shortcut to work as a toggle is a can of worms.
        
        Keybinder repeats the keys if you keep pressing the shortcut.
            It has no way of disabling key repeat.
        Keybinder doesn't work with the <Release> tag.
        Keybinder leaks some key presses into the currently active widget.
            It's not that it leaks all, it leaks some, it's weird.
            There is no way to tag an event as handled to prevent event leak.
        Keybinder grabs focus.
            I can't check which window has focus.
        Switching quickly from hide to activate crashes GNOME.
        There is no way to hide all toplevels consistently.
            If you have a dialog open, you need to hide it explicitly.
            If that dialog has a dialog itself, like when you need to show an
                error message, then you need to explicitly hide that one as
                well. However depending on the widgets you have on it, and the
                shortcut you set for Keybinder, some of the keys might leak
                into the widget and close the dialog, which will reactivate
                the parent, and negate the hide instruction previously sent.
        
        Leave it alone.
        '''
        self.activate()
    
    def on_handle_local_options(self, application, options):
        '''
        This method will handle the command line options.
        '''
        if options.contains('autostart'):
            settings = Gio.Settings(schema=self.schema_id + '.preferences')
            general_preferences = settings.get_child('general')
            if not general_preferences['autostart']:
                # Nop, the user doesn't want to autostart, exit app.
                return 0
        if options.contains('hide'):
            self.hide_flag = True
            self.started_hidden = True
        # All ok, process the rest of the command line.
        return -1
    
    def add_actions(self):
        '''
        This method will add actions to this application action map.
        '''
        shortcuts = self.settings.get_child('shortcuts')
        action_methods = [('preferences', self.on_preferences, ''),
                          ('help', self.on_help, ''),
                          ('about', self.on_about, ''),
                          ('new', self.on_new, 'account-new'),
                          ('edit', self.on_edit, 'account-edit'),
                          ('delete', self.on_delete, 'account-delete'),
                          ('view_mode', self.on_view_mode, 'view-mode'),
                          ('view_size', self.on_view_size, 'view-size'),
                          ('quit', self.on_quit, 'app-quit')]
        for name, method, accel in action_methods:
            action = Gio.SimpleAction(name=name)
            self.add_action(action)
            action.connect('activate', method)
            if accel and shortcuts[accel]:
                self.set_accels_for_action('app.' + name, [shortcuts[accel]])
    
    def on_activate(self, app):
        '''
        This method will activate the window, most of the time.
        This method gets called when the application is first run, so it needs
        to check if the hide flag was specified, if it was, it won't actually
        activate the window, and it won't populate the window with any data.
        The reason for this is because the data that needs to be displayed is
        inside a collection, which may be locked, asking the user for a
        password on login, which is when by default the application is run,
        will be an unintuitive experience. The password may be in the 'Login'
        keyring, in which case the collection will be unlocked automatically,
        but we can't rely on that, and so the data is only unlocked and loaded
        when the application is first shown. This will slow the first show a
        bit, but if the password to unlock the collection is required, the user
        will know why that popup asking for a password is showing.
        Also when the collection is first unlock, and the user doesn't input
        the correct password, or just cancels the popup, there will be
        different behaviour depending on whether the application was run
        initially hidden or not. We feel it's best to return the window to the
        previous state to deliver a more intuitive experience to the user.
        So if the window is hidden, then it's shown, and needs a password to
        unlock the collection, if that password query fails, it returns to
        being hidden. If the application is being started without the hide flag
        and a password query fails, then the application is shutdown.
        '''
        if self.hide_flag:
            self.hide_flag = False
            return
        # If the collection wasn't created quit
        if not self.main_view.secret.collection:
            self.quit()
            return
        if self.main_view.secret.unlock():
            # The app can start hidden to speed up showing it later,
            # but I wouldn't want to ask for a collection password right after
            # the user logs in, particularly because the collection would be
            # locked and the user would have to input the password again later
            # when showing the window. So I populate the buttons on the first
            # show instead. I also set the started_hidden flag, this makes the
            # app never quit when coming from hiding and the unlock fails,
            # it will just keep hidden.
            if self.first_run:
                self.first_run = False
                self.started_hidden = True
                self.main_view.init_buttons()
            self.window.show()
            # This line will produce warnings on journalctl when passman
            # is activated without using the keyboard shortcut.
            # This happens because Gtk doesn't set this as the current event,
            # and so we have no object to get the time from.
            self.window.get_window().focus(Keybinder.get_current_event_time())
        else:
            # If the application starts hidden, I prefer to return the app to
            # the previous state, hidden, instead of quitting.
            if not self.started_hidden:
                self.quit()
    
    def on_size_allocate(self, widget, allocation):
        '''
        This method records any changes to the window size.
        We could store these settings in real time on disk, but the smoothness
        of the resizing operation would suffer a bit too much.
        '''
        self.width = allocation.width
        self.height = allocation.height
    
    def on_shutdown(self, app):
        '''
        This method saves some settings on shutdown,
        locks the collection, and does some cleanup.
        '''
        window = Gio.Settings(schema=self.schema_id + '.window')
        self.win_settings.set_value('width', GLib.Variant('q', self.width))
        self.win_settings.set_value('height', GLib.Variant('q', self.height))
        # If the user wants timeouts while the app is running, it makes sense
        # to enforce those on exit as well, even when the timeout isn't over.
        if self.main_view.timeout:
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            clipboard.clear()
        if self.main_view.secret.collection:
            self.main_view.secret.lock()
    
    def on_preferences(self, obj, param):
        '''
        This method starts the preferences dialog, making sure it's
        the only one currently being displayed.
        '''
        # This check is required to avoid multiple 'preferences' windows.
        if self.preferences_dialog != None:
            self.preferences_dialog.present()
            return
        self.preferences_dialog = PreferencesDialog(self)
        self.preferences_dialog.run()
        self.preferences_dialog.destroy()
        self.preferences_dialog = None
    
    def on_help(self, obj, param):
        '''
        This method will launch the system's default
        application to read help files.
        '''
        Gio.AppInfo.launch_default_for_uri('help:' + self.name.lower())
    
    def on_about(self, obj, param):
        '''
        This method shows the about dialog, making sure it's
        the only one currently being displayed.
        '''
        # This check is required to avoid multiple 'about' windows.
        if self.about_dialog != None:
            self.about_dialog.present()
            return
        dialog = Gtk.AboutDialog(transient_for=self.window)
        #dialog.props.artists = ['artists']
        dialog.props.authors = ['Pedro \'xor\' Azevedo <passman@idlecore.com>']
        dialog.props.comments = _('Easy to use password manager.')
        dialog_copyright = _('Copyright © 2015 - {} authors')
        dialog.props.copyright = dialog_copyright.format(self.name)
        #dialog.props.documenters = ['documenters']
        #dialog.props.license = 'license'
        dialog.props.license_type = Gtk.License.GPL_3_0
        #dialog.props.logo = None
        dialog.props.logo_icon_name = self.icon
        dialog.props.program_name = self.name
        #dialog.props.translator_credits = 'translator_credits'
        dialog.props.version = self.version
        dialog.props.website = self.website
        dialog.props.website_label = 'Website'
        #dialog.props.wrap_license = False
        self.about_dialog = dialog
        response = dialog.run()
        dialog.destroy()
        self.about_dialog = None
    
    def on_new(self, obj, param):
        '''
        This method will be called when the accelerator to add a new account
        is used. It will delegate this task to the HeaderBar object.
        '''
        self.window.get_titlebar().on_add(None)
    
    def on_edit(self, obj, param):
        '''
        This method will be called when the accelerator to edit an account
        is used. It will delegate this task to the main_view object.
        '''
        widget = self.window.get_focus()
        if widget.get_parent() in self.main_view.flowbox:
            self.main_view.on_edit(None, None, widget)
    
    def on_delete(self, obj, param):
        '''
        This method will be called when the accelerator to delete an account
        is used. It will delegate this task to the main_view object.
        '''
        widget = self.window.get_focus()
        if widget.get_parent() in self.main_view.flowbox:
            self.main_view.on_delete(None, None, widget)
    
    def on_view_mode(self, action, param):
        '''
        This method will be called when the accelerator to change the view
        is used. This task will be handled in the HeaderBar object.
        '''
        action = self.lookup_action('view_mode_switch')
        if action.get_state() == GLib.Variant('s', 'list'):
            mode = GLib.Variant('s', 'grid')
        else:
            mode = GLib.Variant('s', 'list')
        action.activate(mode)
    
    def on_view_size(self, obj, param):
        '''
        This method will be called when the accelerator to change the size of
        the items is used. This task will be handled in the HeaderBar object.
        '''
        scale = self.window.get_titlebar().scale
        adjustment = scale.get_adjustment()
        increment = adjustment.get_step_increment()
        value = scale.get_value() + increment
        upper = adjustment.get_upper()
        if value > upper:
            value = adjustment.get_lower()
        scale.set_value(value)
    
    def on_quit(self, obj, param):
        '''
        Quit the application
        '''
        self.quit()

