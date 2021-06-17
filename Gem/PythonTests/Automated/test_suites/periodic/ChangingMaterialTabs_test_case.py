"""
All or portions of this file Copyright (c) Amazon.com, Inc. or its affiliates or
its licensors.

For complete copyright and license terms please see the LICENSE at the root of this
distribution (the "License"). All use of this software is governed by the License,
or, if provided, by the license below or the license accompanying this file. Do not
remove or modify any license notices. This file is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

Test for Changing Material Tabs

import azlmbr.materialeditor will fail with a ModuleNotFound error when using this script with Editor.exe
This is because azlmbr.materialeditor only binds to MaterialEditor.exe and not Editor.exe
You need to launch this script with MaterialEditor.exe in order for azlmbr.materialeditor to appear.
"""

import os
import sys

from PySide2 import QtWidgets, QtTest, QtCore

import azlmbr.paths

sys.path.append(os.path.join(azlmbr.paths.devroot, "AtomTest", "Gem", "PythonTests"))

from editor_python_test_tools import pyside_utils
from Automated.atom_utils.material_editor_utils import MaterialEditorHelper
import Automated.atom_utils.material_editor_utils as material_editor_utils

ASSET_0 = "001_DefaultWhite.material"
ASSET_1 = "002_BaseColorLerp.material"
ASSET_2 = "003_MetalMatte.material"
ASSET_PATH = os.path.join(
    azlmbr.paths.devroot, "Gems", "Atom", "TestData", "TestData", "Materials", "StandardPbrTestCases"
)


class ChangingMaterialTabsTest(MaterialEditorHelper):
    def __init__(self):
        MaterialEditorHelper.__init__(self, log_prefix="ChangingMaterialTabs_test_case")

    def run_test(self):
        """
        Summary:
        Changing/Rearranging Material Tabs in viewport

        Test Steps:
         1) Open materials initially
         2) Initialize QT objects
         3) Verify currently selected material is the third asset opened
         4) Deselect initial tab and verify if deselected
         5) Reselect initial tab and verify if selected
         6) Rearrange first 2 tabs and verify the order

        Expected Result:
        All materials open and create their own tab in the viewport.
        003_MetalMatte is deselected if it was before, and is reselected and appears available to edit.
        The tab moves to the left and docks in position, retaining the last place it was deselected when let go.

        :return: None
        """

        # 1) Open materials initially
        material_editor_utils.open_material(os.path.join(ASSET_PATH, ASSET_0))
        material_editor_utils.open_material(os.path.join(ASSET_PATH, ASSET_1))
        material_editor_utils.open_material(os.path.join(ASSET_PATH, ASSET_2))

        # 2) Initialize QT objects
        editor_window = pyside_utils.get_editor_main_window()
        tab_widget = editor_window.findChild(QtWidgets.QTabWidget, "TabWidget")
        tab_bar = tab_widget.findChild(QtWidgets.QTabBar)

        # 3) Verify currently selected material is the third asset opened
        currently_selected_material = tab_widget.tabText(tab_widget.currentIndex())
        print(f"Initially 3rd tab is selected: {currently_selected_material == ASSET_2}")

        # 4) Deselect initial tab and verify if deselected
        tab_rect = tab_bar.tabRect(0)
        QtTest.QTest.mouseClick(tab_bar, QtCore.Qt.LeftButton, QtCore.Qt.NoModifier, tab_rect.center())
        self.wait_for_condition(lambda: tab_widget.tabText(tab_widget.currentIndex()) == ASSET_0)
        currently_selected_material = tab_widget.tabText(tab_widget.currentIndex())
        print(f"Tab delected upon clicking on other tab: {currently_selected_material == ASSET_0}")

        # 5) Reselect initial tab and verify if selected
        tab_rect = tab_bar.tabRect(2)
        QtTest.QTest.mouseClick(tab_bar, QtCore.Qt.LeftButton, QtCore.Qt.NoModifier, tab_rect.center())
        self.wait_for_condition(lambda: tab_widget.tabText(tab_widget.currentIndex()) == ASSET_2)
        currently_selected_material = tab_widget.tabText(tab_widget.currentIndex())
        print(f"Tab reselected upon clicking on it: {currently_selected_material == ASSET_2}")

        # 6) Rearrange first 2 tabs and verify the order
        tab_bar.moveTab(0, 1)
        self.wait_for_condition(lambda: tab_widget.tabText(0) == ASSET_1)
        result = (tab_widget.tabText(0) == ASSET_1) and (tab_widget.tabText(1) == ASSET_0)
        print(f"Tabs rearranged as expected: {result}")


test = ChangingMaterialTabsTest()
test.run()
