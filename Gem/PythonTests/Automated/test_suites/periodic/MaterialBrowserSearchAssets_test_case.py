"""
All or portions of this file Copyright (c) Amazon.com, Inc. or its affiliates or
its licensors.

For complete copyright and license terms please see the LICENSE at the root of this
distribution (the "License"). All use of this software is governed by the License,
or, if provided, by the license below or the license accompanying this file. Do not
remove or modify any license notices. This file is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.


Searching Assets in Material Browser

import azlmbr.materialeditor will fail with a ModuleNotFound error when using this script with Editor.exe
This is because azlmbr.materialeditor only binds to MaterialEditor.exe and not Editor.exe
You need to launch this script with MaterialEditor.exe in order for azlmbr.materialeditor to appear.
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


class TestMaterialBrowserSearchAssets(MaterialEditorHelper):
    def __init__(self):
        MaterialEditorHelper.__init__(self, log_prefix="MaterialBrowserSearchAssets")

    def run_test(self):
        """
        Summary:
        Searching Assets in Material Browser

        Test Steps:
        1) Open Asset Browser
        2) Search assets with "basic" in Material Browser
        3) Make sure all materials with the word 'basic' in their names are filtered
        4) Search assets with "basic_grey" in Material Browser
        5) Make sure basic_grey.material asset is filtered only

        Expected Result:
        Seaching materials with 'basic' keyword results multiple materials appear dynamically, indicating all materials with the word 'basic' in their name.
        Included in results should be (but not limited to):
        basic.material
        basic_m00_r00.material
        basic_m00_r01.material
        basic_m00_r02.material

        Seaching with 'basic_grey.material' results basic_grey.material in Material Browser

        :return: None
        """

        # 1) Open Asset Browser
        pane_name = "Asset Browser"
        result = material_editor.is_pane_visible(pane_name)
        if not result:
            material_editor.set_pane_visibility(pane_name, True)
        result = material_editor.is_pane_visible(pane_name)
        print(f"{pane_name} opened: {result}")
        general.idle_wait_frames(3)

        # 2) Search assets with "basic" in Material Browser
        editor_window = pyside_utils.get_editor_main_window()
        asset_browser = editor_window.findChildren(QtWidgets.QWidget, "Asset Browser")[0]
        search_bar = asset_browser.findChildren(QtWidgets.QLineEdit, "textSearch")[0]
        search_bar.setText("basic")
        general.idle_wait_frames(1)
        asset_browser_tree = asset_browser.findChild(QtWidgets.QTreeView, "m_assetBrowserTreeViewWidget")
        asset_browser_tree.expandAll()

        # 3) Make sure all materials with the word 'basic' in their names are filtered
        self.incorrect_file_found = False
        model = asset_browser_tree.model()
        indexes = [QtCore.QModelIndex()]
        while len(indexes) > 0:
            parent_index = indexes.pop()
            for row in range(model.rowCount(parent_index)):
                cur_index = model.index(row, 0, parent_index)
                cur_data = cur_index.data(QtCore.Qt.DisplayRole)
                if cur_data.endswith(".material") and ("basic" not in cur_data):
                    print(f"Incorrect file found: {cur_data}")
                    self.incorrect_file_found = True
                    indexes = []
                    break
                indexes.append(cur_index)

        print(
            f"All materials with the word 'basic' in their names are filtered in Asset Browser: {not self.incorrect_file_found}"
        )

        # 4) Search assets with "basic_grey" in Material Browser
        search_bar.setText("basic_grey.material")
        general.idle_wait_frames(1)
        asset_browser_tree = asset_browser.findChild(QtWidgets.QTreeView, "m_assetBrowserTreeViewWidget")
        model_index = pyside_utils.find_child_by_pattern(asset_browser_tree, "basic_grey.material")

        # 5) Make sure basic_grey.material asset is filtered only
        if (asset_browser_tree.indexBelow(model_index)) == (QtCore.QModelIndex()) and model_index is not None:
            print("basic_grey.material asset is filtered in Asset Browser")


test = TestMaterialBrowserSearchAssets()
test.run()
