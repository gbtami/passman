#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
Module for the main program entry point
'''

import locale
import gettext
import platform
import pathlib

# We need to install gettext now because the _() function will be added
# to the built-ins, and it will be used in the Application class.
if platform.system() == 'Windows':
    import os
    os.environ['LANG'] = locale.getdefaultlocale()[0]
    locale_dir = str(pathlib.Path('locale').absolute())
    gettext.install('passman', locale_dir)
else:
    # This next line is required because otherwise I get the warning:
    # Warning: g_variant_new_string:
    # assertion 'g_utf8_validate (string, -1, NULL)' failed
    locale.bind_textdomain_codeset('passman', 'UTF-8')
    gettext.install('passman')

import sys

from passman.application import Application


def main():
    '''
    Main program entry point
    '''
    main_app = Application()
    exit_status = main_app.run(sys.argv)
    sys.exit(exit_status)


if __name__ == '__main__':
    main()

