# -*- coding: utf-8 -*-

'''
Module for the Password Random Generator class
'''

import random
import string


class PassGen:
    '''
    Random Password Generator
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
        if self.alphabet:
            self.password = [r.choice(self.alphabet) for i in range(self.size)]
            self.password = ''.join(self.password)
        else:
            # This, of course, isn't ideal.
            # It happens though when the user leaves no characters, in the
            # preferences, to generate the password with. An empty password
            # however will never be stored, the Add dialog detects them and
            # pops up an alert. Anything beyond that however, digit only
            # passwords, single character alphabet, and other nonsense,
            # Darwin will have to sort out.
            self.password = ''

