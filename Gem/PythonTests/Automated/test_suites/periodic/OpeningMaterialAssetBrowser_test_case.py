"""
All or portions of this file Copyright (c) Amazon.com, Inc. or its affiliates or
its licensors.

For complete copyright and license terms please see the LICENSE at the root of this
distribution (the "License"). All use of this software is governed by the License,
or, if provided, by the license below or the license accompanying this file. Do not
remove or modify any license notices. This file is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.


Test Case Title : Opening Material via Asset Browser
"""

import os
import sys

import azlmbr.paths
from editor_python_test_tools import pyside_utils
from PySide2 import QtWidgets, QtCore, QtTest
import azlmbr.materialeditor.general as general

sys.path.append(os.path.join(azlmbr.paths.devroot, "AtomTest", "Gem", "PythonTests"))

import Automated.atom_utils.material_editor_utils as material_editor
from Automated.atom_utils.material_editor_utils import MaterialEditorHelper, capture_screenshot

screenshotsFolder = os.path.join(azlmbr.paths.devroot, "AtomTest", "Cache", "pc", "Screenshots")


class TestOpeningMaterialAssetBrowser(MaterialEditorHelper):
    def __init__(self):
        MaterialEditorHelper.__init__(self, log_prefix="OpeningMaterialAssetBrowser")

    def run_test(self):
        """
        Summary:
        Opening Material via Asset Browser

        Expected Result:
        Basic_grey.material opens in the viewport without issue.

        :return: None
        """

        # Open Asset Browser
        pane_name = "Asset Browser"
        result = material_editor.is_pane_visible(pane_name)
        if not result:
            material_editor.set_pane_visibility(pane_name, True)
        result = material_editor.is_pane_visible(pane_name)
        print(f"{pane_name} opened: {result}")
        general.idle_wait_frames(3)

        # Search asset "basic_grey" in Material Browser
        editor_window = pyside_utils.get_editor_main_window()
        asset_browser = editor_window.findChildren(QtWidgets.QWidget, "Asset Browser")[0]
        search_bar = asset_browser.findChildren(QtWidgets.QLineEdit, "textSearch")[0]
        search_bar.setText("basic_grey.material")
        general.idle_wait_frames(1)
        asset_browser_tree = asset_browser.findChild(QtWidgets.QTreeView, "m_assetBrowserTreeViewWidget")

        # Make sure basic_grey.material asset is filtered in asset browser
        if (asset_browser_tree.indexBelow(asset_browser_tree.currentIndex())) == (QtCore.QModelIndex()):
            print("basic_grey.material asset is filtered in Asset Browser")
        
        # Click on basic_grey.material in asset browser
        asset_browser_tree.expandAll()
        model_index = pyside_utils.find_child_by_pattern(asset_browser_tree, "basic_grey.material")
        asset_browser_tree.scrollTo(model_index)
        pyside_utils.item_view_index_mouse_click(asset_browser_tree, model_index)
        QtTest.QTest.mouseDClick(asset_browser_tree.viewport(), QtCore.Qt.LeftButton, QtCore.Qt.NoModifier, asset_browser_tree.visualRect(model_index).center())

        # Capture Screenshot
        capture_screenshot(os.path.join(screenshotsFolder, "screenshot_basic_grey.ppm"))
        


test = TestOpeningMaterialAssetBrowser()
test.run()
