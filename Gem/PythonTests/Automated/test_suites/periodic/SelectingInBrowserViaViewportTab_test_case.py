"""
All or portions of this file Copyright (c) Amazon.com, Inc. or its affiliates or
its licensors.

For complete copyright and license terms please see the LICENSE at the root of this
distribution (the "License"). All use of this software is governed by the License,
or, if provided, by the license below or the license accompanying this file. Do not
remove or modify any license notices. This file is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.


Selecting in Browser via Viewport Tab

import azlmbr.materialeditor will fail with a ModuleNotFound error when using this script with Editor.exe
This is because azlmbr.materialeditor only binds to MaterialEditor.exe and not Editor.exe
You need to launch this script with MaterialEditor.exe in order for azlmbr.materialeditor to appear.
"""

import os
import sys

from PySide2 import QtWidgets

import azlmbr.paths

sys.path.append(os.path.join(azlmbr.paths.devroot, "AtomTest", "Gem", "PythonTests"))

from editor_python_test_tools import pyside_utils
from Automated.atom_utils.material_editor_utils import MaterialEditorHelper
import Automated.atom_utils.material_editor_utils as material_editor

ASSET_1 = "basic_grey.material"
ASSET_2 = "DefaultPBR.material"
FOLDER_PATH = os.path.join(azlmbr.paths.devroot, "AtomTest", "Materials")

class SelectingInBrowserViaViewportTabTest(MaterialEditorHelper):
    def __init__(self):
        MaterialEditorHelper.__init__(self, log_prefix="SelectingInBrowserViaViewportTab_test_case")

    def run_test(self):
        """
        Summary:
        Selecting in Browser via Viewport Tab

        Test Steps:
        1) Open existing materials
        2) Initialize QT objects
        3) Verify currently selected material is the second asset opened
        4) Right Click on the first material and click "Select"
        5) Verify if the material is selected in the Asset Browser

        Expected Result:
        The first material is open and has a tab in viewport.
        DefaultPBR opens and there are now two materials open in the viewport tab area,
        DefaultPBR is the currently selected material.
        The material browser reselects the material, Material Browser locates and selects Basic_Grey.material.

        :return: None
        """

        # 1) Open existing materials
        document_1_id = material_editor.open_material(os.path.join(FOLDER_PATH, ASSET_1))
        print(f"Material 1 opened: {material_editor.is_open(document_1_id)}")
        document_2_id = material_editor.open_material(os.path.join(FOLDER_PATH, ASSET_2))
        print(f"Material 2 opened: {material_editor.is_open(document_2_id)}")

        # 2) Initialize QT objects
        editor_window = pyside_utils.get_editor_main_window()
        asset_browser = self.get_asset_browser(editor_window)
        tab_widget = editor_window.findChild(QtWidgets.QTabWidget, "TabWidget")
        tab_bar = tab_widget.findChild(QtWidgets.QTabBar)
        tree = asset_browser.findChild(QtWidgets.QTreeView, "m_assetBrowserTreeViewWidget")

        # 3) Verify currently selected material is the second asset opened
        currently_selected_material = tab_widget.tabText(tab_widget.currentIndex())
        print(f"Second tab is selected: {currently_selected_material == ASSET_2}")

        # 4) Right Click on the first material and click "Select"
        pyside_utils.move_mouse(tab_bar, position=tab_bar.tabRect(0).center())
        pyside_utils.trigger_context_menu_entry(tab_bar, "Select", pos=tab_bar.tabRect(0).center())

        # 5) Verify if the material is selected in the Asset Browser
        result = self.wait_for_condition(lambda: tree.selectedIndexes()[0].data() == ASSET_1, 2.0)
        print(f"First material is reselected in Browser: {result}")
    
    def get_asset_browser(self, editor_window):
        """
        Opens the Asset Browser if not opened already and returns the Qt object of Asset Browser
        :param editor_window - editor_window Qt object
        :return asset_browser - Qt object
        """
        asset_browser = self.get_asset_browser_dock_widget(editor_window)
        if asset_browser is None or not asset_browser.isVisible():
            action = pyside_utils.find_child_by_pattern(editor_window, {"iconText": "Asset Browser"})
            action.trigger()
        self.wait_for_condition(lambda: self.get_asset_browser_dock_widget(editor_window) is not None)
        asset_browser = self.get_asset_browser_dock_widget(editor_window)
        return asset_browser

    def get_asset_browser_dock_widget(self, editor_window):
        """
        Returns the Qt object of Asset Browser
        :param editor_window - editor_window Qt object
        :return asset_browser - Qt object (QDockWidget)
        """
        return editor_window.findChild(QtWidgets.QDockWidget, "Asset Browser_DockWidget")


test = SelectingInBrowserViaViewportTabTest()
test.run()
