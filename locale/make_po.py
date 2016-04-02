#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os


os.system('xgettext -o passman.po --join-existing --language glade '
          '--no-location ../gui/*.ui')
os.system('xgettext -o passman.po --join-existing --language python '
          '--no-location ../passman/*.py')

