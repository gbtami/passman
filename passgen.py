'''
Module for the Password Random Generator class
'''


from gi.repository import Gio, GLib
import random


class PassGen:
    '''
    Password Random Generator
    '''
    
    def __init__(self, app):
        settings = Gio.Settings(app.schema_id + '.preferences.password')
        self.size = settings['size']
        self.alphabet = settings['alphabet']
        r = random.SystemRandom()
        self.password = [r.choice(self.alphabet) for i in range(self.size)]
        self.password = ''.join(map(chr, self.password))

