#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

os.system('cp schema/com.idlecore.passman.gschema.xml '
          'windows/pynsist_pkgs/gnome/share/glib-2.0/schemas/')

os.system('glib-compile-schemas '
          'windows/pynsist_pkgs/gnome/share/glib-2.0/schemas/')

os.system('pynsist installer.cfg')
