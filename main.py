#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
Module for the main program entry point
'''

import sys

from application import Application


def main():
    '''
    Main program entry point
    '''
    main_app = Application()
    exit_status = main_app.run(sys.argv)
    sys.exit(exit_status)

if __name__ == '__main__':
    main()

