'''
Module for the MainView class
'''

from gi.repository import Gtk


class MainView(Gtk.ScrolledWindow):

    '''
    MainView
    '''

    def __init__(self):
        super().__init__()
        button_list = Gtk.ButtonBox(orientation=Gtk.Orientation.VERTICAL)
        button_list.set_layout(Gtk.ButtonBoxStyle.EXPAND)
        for i in range(4):
            button = Gtk.Button()
            box = Gtk.Box(Gtk.Orientation.HORIZONTAL)
            label = Gtk.Label('test test\ntest test')
            image = Gtk.Image.new_from_file('grid.png')
            button.add(box)
            box.pack_start(image, False, False, 0)
            box.pack_start(label, True, False, 0)
            button_list.pack_start(button, True, True, 0)
        self.add(button_list)

