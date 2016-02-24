from setuptools import setup, find_packages
from gi.repository import GLib
from pathlib import Path
import os

sys_data_dir = Path(GLib.get_system_data_dirs()[-1])
sys_config_dir = Path(GLib.get_system_config_dirs()[0])
autostart_dir = str(sys_config_dir / 'autostart')
schema_dir = str(sys_data_dir / 'glib-2.0' / 'schemas')
app_dir = str(sys_data_dir / 'applications')
app_data_dir = str(sys_data_dir / 'passman')
help_dir = str(sys_data_dir / 'help' / 'C' / 'passman')
help_media_dir = str(sys_data_dir / 'help' / 'C' / 'passman' / 'media')

help_walk = list(os.walk('help'))
dirpath, dirnames, filenames = help_walk[0]
dirpath = Path(dirpath)
help_files = [str(dirpath / filename) for filename in filenames]
dirpath, dirnames, filenames = help_walk[1]
dirpath = Path(dirpath)
help_media_files = [str(dirpath / filename) for filename in filenames]

with open('README.rst', encoding='utf-8') as f:
    f.readline()
    f.readline()
    f.readline()
    long_description = f.read()

setup(
    name='PassMan',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.1.0',

    description='Easy to use password manager',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/xor/passman',

    # Author details
    author='Pedro Azevedo',
    author_email='passman@idlecore.com',

    # Choose your license
    license='GPLv3+',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Topic :: Security',

        # Pick your license as you wish (should match "license" above)
        ('License :: OSI Approved :: '
        'GNU General Public License v3 or later (GPLv3+)'),

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        
        #Platforms
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
    ],

    # What does your project relate to?
    keywords='password manager security',
    
    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    # install_requires=['peppercorn'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    # extras_require={
    #     'dev': ['check-manifest'],
    #     'test': ['coverage'],
    # },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    # package_data={'sample': ['package_data.dat']},

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],
    data_files=[(app_dir, ['freedesktop/passman.desktop']),
                (autostart_dir, ['freedesktop/passman-autostart.desktop']),
                (schema_dir, ['schema/com.idlecore.passman.gschema.xml']),
                (help_dir, help_files),
                (help_media_dir, help_media_files),
                (app_data_dir, ['gui/glade', 'gui/ui',
                                'cache/logo_name_cache.bz2'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={'console_scripts': ['passman=passman.main:main']}
)

