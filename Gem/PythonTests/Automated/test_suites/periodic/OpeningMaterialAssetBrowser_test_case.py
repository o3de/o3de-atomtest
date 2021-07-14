"""
All or portions of this file Copyright (c) Amazon.com, Inc. or its affiliates or
its licensors.

For complete copyright and license terms please see the LICENSE at the root of this
distribution (the "License"). All use of this software is governed by the License,
or, if provided, by the license below or the license accompanying this file. Do not
remove or modify any license notices. This file is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

Opening material in Material Browser

import azlmbr.materialeditor will fail with a ModuleNotFound error when using this script with Editor.exe
This is because azlmbr.materialeditor only binds to MaterialEditor.exe and not Editor.exe
You need to launch this script with MaterialEditor.exe in order for azlmbr.materialeditor to appear.
"""

import os
import sys

import azlmbr.paths
from editor_python_test_tools import pyside_utils
from PySide2 import QtWidgets, QtCore, QtTest

sys.path.append(os.path.join(azlmbr.paths.devassets, "Gem", "PythonTests"))

from Automated.atom_utils.material_editor_utils import MaterialEditorHelper

MATERIAL_NAME = "basic_grey.material"

class TestOpeningMaterialAssetBrowser(MaterialEditorHelper):
    def __init__(self):
        MaterialEditorHelper.__init__(self, log_prefix="OpeningMaterialAssetBrowser")

    def run_test(self):
        """
        Summary:
        Opening Material in Material Browser

        Test Steps:
        1) Initialize QT objects
        2) Search asset "basic_grey" in Material Browser
        3) Make sure basic_grey.material asset is filtered in asset browser
        4) Click on basic_grey.material in asset browser
        5) Make sure basic_grey.material opened in the viewport without issue

        Expected Result:
        Basic_grey.material opens in the viewport without issue.

        :return: None
        """

        # 1) Initialize QT objects
        editor_window = pyside_utils.get_editor_main_window()
        asset_browser = self.get_asset_browser(editor_window)
        search_frame = asset_browser.findChild(QtWidgets.QFrame, "m_searchWidget")
        search_bar = search_frame.findChild(QtWidgets.QWidget, "textSearch")
        tree = asset_browser.findChild(QtWidgets.QTreeView, "m_assetBrowserTreeViewWidget")

        # 2) Search asset "basic_grey" in Material Browser
        search_bar.setText("basic_grey.material")
        self.wait_for_condition(lambda: self.find_material_in_browser(tree) is not None, 2.0)
        model_index = pyside_utils.find_child_by_pattern(tree, MATERIAL_NAME)

        # 3) Make sure basic_grey.material asset is filtered in asset browser
        if (tree.indexBelow(model_index)) == (QtCore.QModelIndex()) and model_index is not None:
            print("basic_grey.material asset is filtered in Asset Browser")

        # 4) Click on basic_grey.material in asset browser
        tree.scrollTo(model_index)
        pyside_utils.item_view_index_mouse_click(tree, model_index)
        QtTest.QTest.mouseDClick(
            tree.viewport(), QtCore.Qt.LeftButton, QtCore.Qt.NoModifier, tree.visualRect(model_index).center(),
        )

        # 5) Make sure basic_grey.material opened in the viewport without issue
        tab_widget = editor_window.findChild(QtWidgets.QTabWidget, "TabWidget")
        tab_bar = tab_widget.findChild(QtWidgets.QTabBar)
        self.wait_for_condition(lambda: tab_bar.count() == 1)
        print(f"basic_grey.material opened in viewport: {tab_bar.count()==1}")

    def get_asset_browser(self, editor_window):
        """
        Opens the Asset Browser if not opened already and returns the Qt object of Asset Browser
        :param editor_window - editor_window Qt object
        :returns asset_browser - Qt object
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
        :returns asset_browser - Qt object (QDockWidget)
        """
        return editor_window.findChild(QtWidgets.QDockWidget, "Asset Browser_DockWidget")

    def find_material_in_browser(self, tree):
        """
        Finds a material in Asset Browser tree
        :param tree - QTreeView object to be searched
        :returns QModelIndex if material is found, else None
        """
        tree.expandAll()
        return pyside_utils.find_child_by_pattern(tree, MATERIAL_NAME) is not None

test = TestOpeningMaterialAssetBrowser()
test.run_test()
