'''
Module for the HeaderBar class
'''

from gi import require_version
require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio
import dialogs


class HeaderBar(Gtk.HeaderBar):
    '''
    HeaderBar
    '''
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.set_title(app.title)
        self.set_show_close_button(True)
        
        button = Gtk.Button()
        button.connect('clicked', self.on_add)
        icon = Gio.ThemedIcon(name='list-add')
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        self.pack_start(button)
        
        button = Gtk.MenuButton()
        builder = Gtk.Builder.new_from_file(self.app.menus_file)
        bar_menu = builder.get_object('bar_menu')
        button.set_menu_model(bar_menu)
        self.pack_end(button)
    
    def on_settings(self, obj, param):
        print('on_settings')
    
    def on_test(self, obj, param):
        print('on_test')
    
    def on_add(self, button):
        dialog = dialogs.Add(self.app)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            data = dialog.get_data()
            item = self.app.main_view.secret.create_item(*data)
            button = self.app.main_view.create_button(item)
            self.app.main_view.insert_button(button)
        dialog.destroy()

