"""
All or portions of this file Copyright (c) Amazon.com, Inc. or its affiliates or
its licensors.

For complete copyright and license terms please see the LICENSE at the root of this
distribution (the "License"). All use of this software is governed by the License,
or, if provided, by the license below or the license accompanying this file. Do not
remove or modify any license notices. This file is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.


Hydra script that opens couple of materials, and then tries to open the same material again

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


class TestSelectingOpenMaterials(MaterialEditorHelper):
    def __init__(self):
        MaterialEditorHelper.__init__(self, log_prefix="SelectingOpenMaterials_test_case")

    def run_test(self):
        """
        Summary:
        Selecting Open Materials in Browser.

        Test Steps:
        1) Initialize QT objects
        2) Initially close all the existing tabs
        3) Open Material 1 and verify if opened
        4) Open Material 2 and verify if opened
        5) Open Material 1 again and verify if new instance is not opened and initial tab is selected

        Expected Result:
        The material opens with a tab at the top of the viewport. When the same material is opened,
        Instead of opening another instance of Basic_grey.material, the initial tab and material are selected and
        available for use.

        :return: None
        """

        ASSET_1 = "basic_grey.material"
        ASSET_2 = "DefaultPBR.material"

        def open_material_from_asset_browser(material_name):
            tree.expandAll()
            search_bar.setText(material_name)
            self.wait_for_condition(lambda: pyside_utils.find_child_by_pattern(tree, material_name) is not None, 2.0)
            mi = pyside_utils.find_child_by_pattern(tree, material_name)
            tree.scrollTo(mi)
            pyside_utils.item_view_index_mouse_click(tree, mi)
            QtTest.QTest.mouseDClick(
                tree.viewport(), QtCore.Qt.LeftButton, QtCore.Qt.NoModifier, tree.visualRect(mi).center()
            )
            tree.collapseAll()

        def get_asset_browser():
            return editor_window.findChild(QtWidgets.QDockWidget, "Asset Browser_DockWidget")

        # 1) Initialize QT objects
        editor_window = pyside_utils.get_editor_main_window()
        asset_browser = get_asset_browser()
        if asset_browser is None or not asset_browser.isVisible():
            action = pyside_utils.find_child_by_pattern(editor_window, {"iconText": "Asset Browser"})
            action.trigger()
        self.wait_for_condition(lambda: get_asset_browser() is not None)
        asset_browser = get_asset_browser()
        search_frame = asset_browser.findChild(QtWidgets.QFrame, "m_searchWidget")
        search_bar = search_frame.findChild(QtWidgets.QWidget, "textSearch")
        tab_widget = editor_window.findChild(QtWidgets.QTabWidget, "TabWidget")
        tab_bar = tab_widget.findChild(QtWidgets.QTabBar)
        tree = asset_browser.findChild(QtWidgets.QTreeView, "m_assetBrowserTreeViewWidget")

        # 2) Initially close all the existing tabs
        close_all = pyside_utils.find_child_by_pattern(editor_window, {"iconText": "Close All"})
        close_all.trigger()

        # 3) Open Material 1 and verify if opened
        open_material_from_asset_browser(ASSET_1)
        self.wait_for_condition(lambda: tab_bar.count() == 1)
        print(f"Instance count after opening first material: {tab_bar.count()}")

        # 4) Open Material 2 and verify if opened
        open_material_from_asset_browser(ASSET_2)
        self.wait_for_condition(lambda: tab_bar.count() == 2)
        print(f"Instance count after opening second material: {tab_bar.count()}")

        # 5) Open Material 1 again and verify if new instance is not opened and initial tab is selected
        open_material_from_asset_browser(ASSET_1)
        self.wait_for_condition(lambda: tab_bar.count() == 2)
        print(f"Instance count after re-open: {tab_bar.count()}")
        print(f"Initial tab is focused: {tab_widget.tabText(tab_widget.currentIndex())==ASSET_1}")


test = TestSelectingOpenMaterials()
test.run()
