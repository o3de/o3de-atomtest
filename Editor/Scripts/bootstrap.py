# coding:utf-8
#!/usr/bin/python
#
# Copyright (c) Contributors to the Open 3D Engine Project.
# For complete copyright and license terms please see the LICENSE at the root of this distribution.
#
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
#
# -- This line is 75 characters -------------------------------------------
# standard imports
import sys
import os
import pathlib
from pathlib import Path
import logging as _logging

# -------------------------------------------------------------------------
# this module name
_PROJECT = 'AtomTest'
_MODULE = f'{_PROJECT}.bootstrap'

_G_DEBUG = os.getenv('DCCSI_GDEBUG', False)  # force on for debugging
os.environ["DCCSI_GDEBUG"] = str(_G_DEBUG) # propogate

#  global space debug flag
_DCCSI_DEV_MODE = os.getenv('DCCSI_DEV_MODE', False)  # force to connect debugger
os.environ["DCCSI_DEV_MODE"] = str(_DCCSI_DEV_MODE) # propogate

# if not set DCCsi bootstrapping (and other scripts) may fail
_LY_DEV = os.getenv('LY_DEV', None)  # assume usually not set
if not _LY_DEV:
    _LY_DEV = Path(azlmbr.paths.engroot)
    os.environ['LY_DEV'] = pathlib.PureWindowsPath(_LY_DEV).as_posix()   

# -------------------------------------------------------------------------
while 0:  # bootstraps the DCCsi
    # Setup paths to DccScripting Interface (DCCsi)
    # To Do: Let DCCsi boostrap itself
    # https://jira.agscollab.com/browse/SPEC-2581
    # "Editor Python Bindings gem" boostrap pattern doesn't account for nested Gems
    # Atom Gem's are nested, so DCCsi won't boostrap
    # So we are setting up the code access and executing the bootstrap here
    import add_dccsi
    import azpy
    # re-initialize logger with one configured to write a log to cache
    _LOGGER = azpy.initialize_logger(_MODULE, default_log_level=int(20))

    # early attach WingIDE debugger (can refactor to include other IDEs later)
    if _DCCSI_DEV_MODE:
        from azpy.env_bool import env_bool
        if not env_bool('DCCSI_DEBUGGER_ATTACHED', False):
            # if not already attached lets do it here
            from azpy.test.entry_test import connect_wing
            foo = connect_wing()

    # check some paths, report if debug logging
    _CWD_PATH = Path(os.getcwd()).resolve()
    _LOGGER.debug(f'CWD Path: {_CWD_PATH}')

    _MODULE_PATH = Path(__file__).resolve()
    _LOGGER.debug(f'MODULE Path: {_MODULE_PATH}')

    # standard lumberyard paths if you need to check them
    _LOGGER.debug(f'Dev root:{azlmbr.paths.devroot}')  # same as @devroot@
    _LOGGER.debug(f'Eng root:{azlmbr.paths.engroot}')  # same as @engroot@

    # from DCCsi
    from add_dccsi import _DCCSIG_PATH
    _LOGGER.debug(f'DCCSI_GEM_PATH: {_DCCSIG_PATH}')

    from add_dccsi import _DCCSI_PYTHON_LIB_PATH
    _LOGGER.debug(f'DCCSI_PYTHON_LIB_PATH: {_DCCSI_PYTHON_LIB_PATH}')

    from add_dccsi import _DCCSI_SCRIPTS_PATH
    _LOGGER.debug(f'DCCSI_SCRIPTS_PATH: {_DCCSI_SCRIPTS_PATH}')

    break
# -------------------------------------------------------------------------