#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

os.system('cp schema/com.idlecore.passman.gschema.xml '
          'pynsist_pkgs/gnome/share/glib-2.0/schemas/')

os.system('glib-compile-schemas '
          'pynsist_pkgs/gnome/share/glib-2.0/schemas/')

# Build all except collection.page, it's not necessary on Windows.
# It's essential the collection.page file isn't built. Removing the file
# after a full build still leaves links to that file on index.html.
os.system('ls help/*.page | '
          'grep -v collection.page | '
          'xargs yelp-build html -o help')

os.system('pynsist installer.cfg')
