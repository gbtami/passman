#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

os.system('cp schema/com.idlecore.passman.gschema.xml '
          'pynsist_pkgs/gnome/share/glib-2.0/schemas/')

os.system('glib-compile-schemas '
          'pynsist_pkgs/gnome/share/glib-2.0/schemas/')

# I choose the files individually because on Windows there is no need for the
# collection.html file, I could just individually remove it but the index.html
# file would include a link to it anyway. This way collection.page isn't
# present during building so index.html won't create a link to it.
os.system('yelp-build html -o help help/delete.page help/edit.page \
           help/general.page help/index.page help/mode.page help/new.page \
           help/passwords.page help/shortcuts.page help/size.page \
           help/tutorial.page')

os.system('pynsist installer.cfg')
