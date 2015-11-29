'''
Module for the LogoGen class
'''

from gi import require_version
require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio
import dialogs


class LogoGen:
    '''
    LogoGen class
    '''
    
    def __init__(self, app, service, username):
        settings = app.settings.get_child('logo')
        size = settings['size']
        icon_theme = Gtk.IconTheme.get_default()
        pixbuf = icon_theme.load_icon('image-missing', size * 32, 0)
        image = Gtk.Image.new_from_pixbuf(pixbuf)
        label_text = '<b>{}:</b> {}'.format(service, username)
        if size == 1:
            label_text = '<small>{}</small>'.format(label_text)
        elif size == 3:
            label_text = '<big>{}</big>'.format(label_text)
        label = Gtk.Label(label_text, **{'use-markup': True})
        self.box = Gtk.Box()
        self.box.pack_start(image, False, False, 0)
        self.box.pack_start(label, True, False, 0)

