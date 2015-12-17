# -*- coding: utf-8 -*-

'''
Module for the Password Random Generator class
'''

import random
import string

from gi.repository import Gio


class PassGen:
    '''
    Password Random Generator
    '''
    
    def __init__(self, app):
        settings = app.settings.get_child('passwords')
        self.size = settings['size']
        self.alphabet = ''
        if settings['lowercase']:
            self.alphabet += string.ascii_lowercase
        if settings['uppercase']:
            self.alphabet += string.ascii_uppercase
        if settings['digits']:
            self.alphabet += string.digits
        for i in settings['punctuation']:
            self.alphabet += chr(i)
        r = random.SystemRandom()
        self.password = [r.choice(self.alphabet) for i in range(self.size)]
        self.password = ''.join(self.password)

