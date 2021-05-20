"""
All or portions of this file Copyright (c) Amazon.com, Inc. or its affiliates or
its licensors.

For complete copyright and license terms please see the LICENSE at the root of this
distribution (the "License"). All use of this software is governed by the License,
or, if provided, by the license below or the license accompanying this file. Do not
remove or modify any license notices. This file is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.


Test Case Title : Searching Assets in Material Browser
"""

import os
import sys

import azlmbr.paths
from editor_python_test_tools import pyside_utils
from PySide2 import QtWidgets, QtCore
import azlmbr.materialeditor.general as general

sys.path.append(os.path.join(azlmbr.paths.devroot, "AtomTest", "Gem", "PythonTests"))

import Automated.atom_utils.material_editor_utils as material_editor
from Automated.atom_utils.material_editor_utils import MaterialEditorHelper


class TestMaterialBrowserSearchAssetsWorks(MaterialEditorHelper):
    def __init__(self):
        MaterialEditorHelper.__init__(self, log_prefix="MaterialBrowser_SearchAssets_Works")

    def run_test(self):
        """
        Summary:
        Searching Assets in Material Browser

        Expected Result:
        Seaching materials with 'basic' keyword results multiple materials appear dynamically, indicating all materials with the word 'basic' in their name.
        Included in results should be (but not limited to):
        basic.material
        basic_m00_r00.material
        basic_m00_r01.material
        basic_m00_r02.material

        Seaching with 'basic_grey.material' results basic_grey.material only in Material Browser

        :return: None
        """

        # Open Asset Browser
        pane_name = "Asset Browser"
        result = material_editor.is_pane_visible(pane_name)
        if not result:
            material_editor.set_pane_visibility(pane_name, True)
        result = material_editor.is_pane_visible(pane_name)
        print(f"{pane_name} opened: {result}")
        general.idle_wait_frames(15)

        # Search assets with "basic" in Material Browser
        editor_window = pyside_utils.get_editor_main_window()
        asset_browser = editor_window.findChildren(QtWidgets.QDockWidget, "Asset Browser")[0]
        search_bar = asset_browser.findChildren(QtWidgets.QLineEdit, "textSearch")[0]
        search_bar.setText("basic")
        general.idle_wait_frames(1)
        asset_browser_tree = asset_browser.findChild(QtWidgets.QTreeView, "m_assetBrowserTreeViewWidget")

        # Make sure all materials with the word 'basic' in their names are filtered
        if (asset_browser_tree.indexBelow(asset_browser_tree.currentIndex())) != (QtCore.QModelIndex()):
            print("All materials with the word 'basic' in their names are filtered in Asset Browser")

        # Search assets with "basic_grey" in Material Browser
        search_bar.setText("basic_grey.material")
        general.idle_wait_frames(1)
        asset_browser_tree = asset_browser.findChild(QtWidgets.QTreeView, "m_assetBrowserTreeViewWidget")

        # Make sure basic_grey.material asset is filtered only
        if (asset_browser_tree.indexBelow(asset_browser_tree.currentIndex())) == (QtCore.QModelIndex()):
            print("basic_grey.material asset is filtered in Asset Browser")


test = TestMaterialBrowserSearchAssetsWorks()
test.run()
