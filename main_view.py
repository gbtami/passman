'''
Module for the MainView class
'''

from gi.repository import Gtk


class MainView(Gtk.ScrolledWindow):
    '''
    MainView
    '''
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.button_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.load_widgets()
    
    def load_widgets(self):
        self.button_list.set_spacing(self.app.spacing)
        self.button_list.set_border_width(self.app.spacing)
        for i in reversed(self.app.collection.get_items()):
            self.load_item(i)
        self.add(self.button_list)
    
    def load_item(self, item):
        button = Gtk.Button()
        box = Gtk.Box(Gtk.Orientation.HORIZONTAL)
        label = Gtk.Label(item.get_label())
        image_dir = str(self.app.img_dir / 'test')
        image = Gtk.Image.new_from_file(image_dir)
        button.add(box)
        box.pack_start(image, False, False, 0)
        box.pack_start(label, True, False, 0)
        self.button_list.pack_start(button, False, False, 0)

