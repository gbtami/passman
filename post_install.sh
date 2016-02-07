#!/bin/sh

system_data_dir=`python3 -c 'from gi.repository import GLib; \
                             print(GLib.get_system_data_dirs()[-1]);'`
glib-compile-schemas $system_data_dir/glib-2.0/schemas 2>&1|logger

