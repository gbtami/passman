#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os


with open('README.rst', encoding='utf-8') as f:
    f.readline()
    f.readline()
    f.readline()
    long_description = f.read()

os.system('fpm '
          '--verbose '
          '--license GPLv3+ '
          '--version 0.1.0 '
          '--maintainer passman@idlecore.com '
          '--url https://github.com/xor/passman '
          '--description \'' + long_description + '\' '
          '--depends \'keybinder3 >= 0.3\' '
          '--depends \'python3-requests >= 2.7\' '
          '--depends \'gnome-keyring >= 3.16\' '
          '--depends \'libsecret >= 0.16\' '
          '--depends \'gtk3 >= 3.16\' '
          '--python-bin python3 '
          '--python-package-name-prefix python3 '
          '--after-install post_install.sh '
          '-s python '
          '-t rpm '
          './setup.py')

