#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import pathlib

os.system('cp schema/com.idlecore.passman.gschema.xml '
          'pynsist_pkgs/gnome/share/glib-2.0/schemas/')

os.system('glib-compile-schemas '
          'pynsist_pkgs/gnome/share/glib-2.0/schemas/')

# Build all except collection.page, it's not necessary on Windows.
# It's essential the collection.page file isn't built. Removing the file
# after a full build still leaves links to that file on index.html.
help_path = pathlib.Path('help')
help_walk = os.walk(str(help_path))
dirpath, dirnames, filenames = next(help_walk)
for directory in dirnames:
    language_path = str(help_path / directory / 'passman')
    os.system('find ' + language_path + ' -name *.page | '
              'grep -v collection.page | '
              'xargs yelp-build html -o ' + language_path)

os.system('pynsist installer.cfg')

os.system('find help -name *.html -o -name *.js -o -name *.css | xargs rm')

