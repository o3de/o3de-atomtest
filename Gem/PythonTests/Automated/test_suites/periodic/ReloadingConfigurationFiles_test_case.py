"""
All or portions of this file Copyright (c) Amazon.com, Inc. or its affiliates or
its licensors.

For complete copyright and license terms please see the LICENSE at the root of this
distribution (the "License"). All use of this software is governed by the License,
or, if provided, by the license below or the license accompanying this file. Do not
remove or modify any license notices. This file is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

Reloading Configuration Files in Material Editor

import azlmbr.materialeditor will fail with a ModuleNotFound error when using this script with Editor.exe
This is because azlmbr.materialeditor only binds to MaterialEditor.exe and not Editor.exe
You need to launch this script with MaterialEditor.exe in order for azlmbr.materialeditor to appear.
"""

import os
import sys

import azlmbr.paths
from editor_python_test_tools import pyside_utils
from PySide2 import QtWidgets

sys.path.append(os.path.join(azlmbr.paths.devroot, "AtomTest", "Gem", "PythonTests"))

from Automated.atom_utils.material_editor_utils import MaterialEditorHelper

class TestReloadingConfigurationFiles(MaterialEditorHelper):
    def __init__(self):
        MaterialEditorHelper.__init__(self, log_prefix="ReloadingConfigurationFiles")

    def run_test(self):
        """
        Summary:
        Reloading Configuration Files in Material Editor.

        Test Steps:
        1) Initialize QT objects
        2) Select "Reload Config Files" in File Menu

        Expected Result:
        The Material Editor should remain stable, with the below files reloading and prompting within the console.
            materialeditor/viewportmodels/shaderball.modelpreset.azasset
            materialeditor/lightingpresets/neutral_urban.lightingpreset.azasset

        :return: None
        """

        # 1) Initialize QT objects
        editor_window = pyside_utils.get_editor_main_window()
        self.get_viewport_settings(editor_window)
        model_settings = editor_window.findChild(QtWidgets.QWidget, "modelSettings")

        # 2) Select "Reload Config Files" in File Menu
        push_button = pyside_utils.find_child_by_pattern(
            model_settings, {"text": "Refresh", "type": QtWidgets.QPushButton}
        )
        push_button.click()

    def get_viewport_settings(self, editor_window):
        """
        Opens the Viewport Settings if not opened already and returns the Qt object of Viewport Settings
        :param editor_window - editor_window Qt object
        :returns asset_browser - Qt object
        """
        viewport_settings = self.get_viewport_dock_widget(editor_window)
        if viewport_settings is None or not viewport_settings.isVisible():
            action = pyside_utils.find_child_by_pattern(editor_window, {"iconText": "Viewport Settings"})
            action.trigger()
        self.wait_for_condition(lambda: self.get_viewport_dock_widget(editor_window) is not None)
        viewport_settings = self.get_viewport_dock_widget(editor_window)
        return viewport_settings

    def get_viewport_dock_widget(self, editor_window):
        """
        Returns the Qt object of Viewport Settings
        :param editor_window - editor_window Qt object
        :returns asset_browser - Qt object (QDockWidget)
        """
        return editor_window.findChild(QtWidgets.QDockWidget, "Viewport Settings_DockWidget")

test = TestReloadingConfigurationFiles()
test.run()
