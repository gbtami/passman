# -*- coding: utf-8 -*-

'''
Module for the Password Random Generator class
'''


from gi.repository import Gio
import random


class PassGen:
    '''
    Password Random Generator
    '''
    
    def __init__(self, app):
        settings = app.settings.get_child('password')
        self.size = settings['size']
        self.alphabet = settings['alphabet']
        r = random.SystemRandom()
        self.password = [r.choice(self.alphabet) for i in range(self.size)]
        self.password = ''.join([chr(p) for p in self.password])

