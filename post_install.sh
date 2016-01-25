#!/bin/bash
# Output stdout and stderr to journal.
glib-compile-schemas /usr/share/glib-2.0/schemas 2>&1|logger

