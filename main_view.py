'''
Module for the MainView class
'''

from gi.repository import Gtk


class MainView(Gtk.ScrolledWindow):
    '''
    MainView
    '''
    
    icons = ['16.png', '22.png', '24.png', '32.png',
             '36.png', '48.png', '64.png', '96.png']
    
    def __init__(self, app):
        super().__init__()
        self.load_widgets(app)
    
    def load_widgets(self, app):
        button_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        button_list.set_spacing(app.spacing)
        button_list.set_border_width(app.spacing)
        for i in range(len(self.icons)):
            button = Gtk.Button()
            box = Gtk.Box(Gtk.Orientation.HORIZONTAL)
            label = Gtk.Label('Test Test\nTest Test')
            image_dir = str(app.img_dir / self.icons[5])
            image = Gtk.Image.new_from_file(image_dir)
            button.add(box)
            box.pack_start(image, False, False, 0)
            box.pack_start(label, True, False, 0)
            button_list.pack_start(button, False, False, 0)
        self.add(button_list)

