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
        button_list = Gtk.ButtonBox(orientation=Gtk.Orientation.VERTICAL)
        button_list.set_spacing(app.spacing)
        button_list.set_layout(Gtk.ButtonBoxStyle.EXPAND)
        button_list.set_homogeneous(False)
        # The linked class only displays well when there is no spacing between
        # the buttons, since I plan on having some, I need to get rid of it.
        button_list.get_style_context().remove_class('linked')
        for i in range(len(self.icons)):
            button = Gtk.Button()
            #button.set_valign(Gtk.Align.CENTER)
            box = Gtk.Box(Gtk.Orientation.HORIZONTAL)
            label = Gtk.Label('Test test\nTest test')
            image_dir = str(app.img_dir / self.icons[5])
            image = Gtk.Image.new_from_file(image_dir)
            button.add(box)
            box.pack_start(image, False, False, 0)
            box.pack_start(label, True, False, 0)
            button_list.pack_start(button, False, False, 0)
            # Even though I set the ButtonBox to not make the children
            # homogeneous, I still need to tell each individual child the same
            # thing. If I don't, everything is fine until the Box is resized
            # bellow the minimum size, when it decides to leave a huge vertical
            # gap at the end, proportional in size to the number of children
            # that have this setting on. Thanks Gtk+ devs.
            button_list.set_child_non_homogeneous(button, True)
        self.set_border_width(app.spacing)
        self.add(button_list)

