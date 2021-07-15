"""
Copyright (c) Contributors to the Open 3D Engine Project.
For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT

Exiting Client Via File Menu
"""

import os
import sys
import azlmbr.paths
from editor_python_test_tools import pyside_utils
from PySide2 import QtWidgets

sys.path.append(os.path.join(azlmbr.paths.devassets, "Gem", "PythonTests"))
from Automated.atom_utils.material_editor_utils import MaterialEditorHelper


class TestMaterialEditorBasicTests(MaterialEditorHelper):
    def __init__(self):
        MaterialEditorHelper.__init__(self, log_prefix="MaterialEditorExitFromFileMenu_test_case")

    def run_test(self):
        """
        Summary:
        Exiting the Material Editor using File Menu
        1. Make sure Material Editor main window is visible
        2. Click on Exit option from File Menu

        Expected Result:
        Material Editor closes without issue.

        :return: None
        """

        # 1. Make sure Material Editor main window is visible
        editor_window = pyside_utils.get_editor_main_window()
        if editor_window.isVisible():
            print("Material Editor main window is visible")

        # 2. Click on Exit option from File Menu
        exit_action = pyside_utils.find_child_by_pattern(editor_window, {"text": "E&xit", "type": QtWidgets.QAction})
        exit_action.trigger()

        if not editor_window.isVisible():
            print("Material Editor exited from File menu")


test = TestMaterialEditorBasicTests()
test.run_test()
