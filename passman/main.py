#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
Module for the main program entry point
'''

import locale
import gettext

# https://docs.python.org
# /dev/library/locale.html#access-to-message-catalogs
# Python applications should normally find no need to invoke these
# functions, and should use gettext instead. A known exception to this
# rule are applications that link with additional C libraries which
# internally invoke gettext() or dcgettext(). For these applications,
# it may be necessary to bind the text domain, so that the libraries
# can properly locate their message catalogs.
locale.bindtextdomain('passman', '/home/xor/workspace/passman/locale')

# We need to install this before anything else because the _() function will
# be added to the built-ins, and it will be used in the Application class
gettext.install('passman', '/home/xor/workspace/passman/locale')

import sys

from .application import Application


def main():
    '''
    Main program entry point
    '''
    main_app = Application()
    exit_status = main_app.run(sys.argv)
    sys.exit(exit_status)


if __name__ == '__main__':
    main()

