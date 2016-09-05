#!/usr/bin/env python
# coding: utf-8

import os
import sys
from cx_Freeze import setup, Executable

import crispy
import silx

msi_data = {
	'Shortcut': [
	    ('DesktopShortcut',           # Shortcut
		'DesktopFolder',          # Directory_
		'Crispy',                 # Name
		'TARGETDIR',              # Component_
		'[TARGETDIR]Crispy.exe',  # Target
		None,                     # Arguments
		None,                     # Description
		None,                     # Hotkey
		None,                     # Icon
		None,                     # IconIndex
		None,                     # ShowCmd
		'%APPDATA%\Crispy'        # WkDir
		),
	    ('ProgramMenuShortcut',       # Shortcut
		'ProgramMenuFolder',      # Directory_
		'Crispy',                 # Name
		'TARGETDIR',              # Component_
		'[TARGETDIR]Crispy.exe',  # Target
		None,                     # Arguments
		None,                     # Description
		None,                     # Hotkey
		None,                     # Icon
		None,                     # IconIndex
		None,                     # ShowCmd
		'%APPDATA%\Crispy'        # WkDir
		)
	    ]
	}

packages = []
includes = []
excludes = ['scipy', 'tkinter']

modules = [crispy, silx]
modules_path = [os.path.dirname(module.__file__) for module in modules]
include_files = [(module, os.path.basename(module)) for module in modules_path]

options = {
	'build_exe': {
	    'packages': packages,
	    'includes': includes,
	    'excludes': excludes,
	    'include_files': include_files,
	    'include_msvcr': True,
	    },
	}

base = None
if sys.platform == 'win32':
    base = 'Win32GUI' # 'Console'

executables = [
        Executable(
            'scripts/Crispy',
            base=base,
            icon='icons/crispy.ico',
	    shortcutName='Crispy',
            shortcutDir='DesktopFolder',
            )
        ]

setup(name='Crispy',
      version='0.1.0',
      options=options,
      executables=executables)
