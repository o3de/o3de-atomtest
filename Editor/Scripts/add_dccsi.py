# coding:utf-8
#!/usr/bin/python
#
# Copyright (c) Contributors to the Open 3D Engine Project
# 
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
#
# -- This line is 75 characters -------------------------------------------
# standard imports
import sys
import os
import site
import pathlib
from pathlib import Path
import logging as _logging

import azlmbr

# -------------------------------------------------------------------------
_PROJECT = 'AtomTest'
_MODULE = f'{_PROJECT}.add_dccsi'

# add the DCCsi in dev mode (we can always enable it fully later)
# because it's experimental let's not unable it unless we are debugging

# if not set DCCsi bootstrapping (and other scripts) will fail
_LY_DEV = os.getenv('LY_DEV', None)  # assume usually not set
if not _LY_DEV:
    _LY_DEV = Path(azlmbr.paths.engroot)
    os.environ['LY_DEV'] = pathlib.PureWindowsPath(_LY_DEV).as_posix()   

# Setup paths to DccScripting Interface (DCCsi)
# To Do: Let DCCsi bootstrap itself
# https://jira.agscollab.com/browse/SPEC-2581
# "Editor Python Bindings gem" bootstrap pattern doesn't account for nested Gems
# Atom Gem's are nested, so DCCsi won't bootstrap correctly naturally
# So we are setting up the code access and executing the bootstrap here
_DCCSIG_PATH = Path(_LY_DEV, 'Gems',
                       'AtomLyIntegration',
                       'TechnicalArt',
                       'DccScriptingInterface')
_DCCSIG_PATH = Path(os.getenv('DCCSIG_PATH', _DCCSIG_PATH))  # allow env override
os.environ['DCCSIG_PATH'] = pathlib.PureWindowsPath(_DCCSIG_PATH).as_posix()
sys.path.insert(1, pathlib.PureWindowsPath(_DCCSIG_PATH).as_posix())


# bootstrap site-packages by version
_PY_MAJOR = sys.version_info.major  # future proof
_PY_MINOR = sys.version_info.minor
_DCCSI_PYTHON_LIB_PATH = Path(_DCCSIG_PATH, '3rdParty',
                              'Python', 'Lib',
                              f'{_PY_MAJOR}.x',
                              f'{_PY_MAJOR}.{_PY_MINOR}.x',
                              'site-packages')
_DCCSI_PYTHON_LIB_PATH = os.getenv('DCCSI_PYTHON_LIB_PATH',
                                   _DCCSI_PYTHON_LIB_PATH)  # allow env override
sys.path.insert(2, pathlib.PureWindowsPath(_DCCSI_PYTHON_LIB_PATH).as_posix())

# bootstrap the DCCsi directly
_DCCSI_SCRIPTS_PATH = Path(_DCCSIG_PATH, 'Editor', 'Scripts')
sys.path.insert(3, pathlib.PureWindowsPath(_DCCSI_SCRIPTS_PATH).as_posix())

# Force the execution of the DCCsi bootstrap
import importlib.util
spec_dccsi_bootstrap = importlib.util.spec_from_file_location("dccsi.bootstrap",
                                                              Path(_DCCSI_SCRIPTS_PATH,
                                                                   "bootstrap.py"))
_dccsi_bootstrap = importlib.util.module_from_spec(spec_dccsi_bootstrap)
spec_dccsi_bootstrap.loader.exec_module(_dccsi_bootstrap)
_dccsi_bootstrap.init()
# -------------------------------------------------------------------------


# -------------------------------------------------------------------------
# boostrapping DCCsi and using azpy will allow us to early attach
# WingIDE debugger (can refactor to include other IDEs later)

# if we don't set this then we can't attach the debugger
_WINGHOME = os.getenv('WINGHOME', None)  # assume usually not set
if not _WINGHOME:
    _WINGHOME = Path(r"C:\Program Files (x86)\Wing Pro 7.1")
    os.environ['WINGHOME'] = pathlib.PureWindowsPath(_WINGHOME).as_posix()
    
# verify we can get to DCCsi azpy
try:
    import azpy
    _LOGGER = azpy.initialize_logger(_MODULE, default_log_level=int(20))
    _LOGGER.info(f'Bootstrapping: {_MODULE}')
    _LOGGER.info('SUCCESS: Imported azpy')
    from azpy.env_base import _BASE_ENVVAR_DICT
except ImportError as error:
    _logging.error(error)
    raise error
# -------------------------------------------------------------------------


# -------------------------------------------------------------------------
from azpy.env_bool import env_bool
from azpy.constants import ENVAR_DCCSI_GDEBUG
from azpy.constants import ENVAR_DCCSI_DEV_MODE

#  global space,
_G_DEBUG = env_bool(ENVAR_DCCSI_GDEBUG, False)
_DCCSI_DEV_MODE = env_bool(ENVAR_DCCSI_DEV_MODE, False)

# early attach WingIDE debugger (can refactor to include other IDEs later)
if _DCCSI_DEV_MODE:
    from azpy.env_bool import env_bool
    if not env_bool('DCCSI_DEBUGGER_ATTACHED', False):
        # if not already attached lets do it here
        from azpy.test.entry_test import connect_wing
        foo = connect_wing()
# -------------------------------------------------------------------------


# -------------------------------------------------------------------------
# add access to the DCCsi\SDL\Lumberyard area
# bootstrap the DCCsi directly
_DCCSI_SDK_LY_PATH = Path(_DCCSIG_PATH, 'SDK', 'Lumberyard', 'Scripts')
sys.path.insert(4, pathlib.PureWindowsPath(_DCCSI_SDK_LY_PATH).as_posix())

# create and populate menu for DCCsi in tools (Editor.exe, materialeditor.exe)
spec_dccsi_set_menu = importlib.util.spec_from_file_location("dccsi.set_menu",
                                                             Path(_DCCSI_SDK_LY_PATH,
                                                                  "set_menu.py"))
_dccsi_set_menu = importlib.util.module_from_spec(spec_dccsi_set_menu)
spec_dccsi_set_menu.loader.exec_module(_dccsi_set_menu)
# - END -------------------------------------------------------------------