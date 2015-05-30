'''
Module for the MainView class
'''

from gi.repository import Gtk
import config as cfg


class MainView(Gtk.ScrolledWindow):

    '''
    MainView
    '''

    def __init__(self):
        super().__init__()
        self.connect('parent-set', self.on_parent_set)

    def on_parent_set(self, widget, old_parent):
        if old_parent is not None:
            return
        data_dir = self.get_parent().get_application().system_data_dir
        button_list = Gtk.ButtonBox(orientation=Gtk.Orientation.VERTICAL,
                                    spacing=cfg.spacing)
        button_list.set_layout(Gtk.ButtonBoxStyle.EXPAND)
        button_list.get_style_context().remove_class('linked')
        for i in range(4):
            button = Gtk.Button()
            box = Gtk.Box(Gtk.Orientation.HORIZONTAL)
            label = Gtk.Label('test test\ntest test')
            image = Gtk.Image.new_from_file(str(data_dir / 'images/grid.png'))
            button.add(box)
            box.pack_start(image, False, False, 0)
            box.pack_start(label, True, False, 0)
            button_list.pack_start(button, True, True, 0)
        self.set_border_width(cfg.spacing)
        self.add(button_list)

