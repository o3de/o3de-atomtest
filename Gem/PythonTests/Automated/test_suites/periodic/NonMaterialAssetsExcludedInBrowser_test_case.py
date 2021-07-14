"""
All or portions of this file Copyright (c) Amazon.com, Inc. or its affiliates or
its licensors.

For complete copyright and license terms please see the LICENSE at the root of this
distribution (the "License"). All use of this software is governed by the License,
or, if provided, by the license below or the license accompanying this file. Do not
remove or modify any license notices. This file is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

Non-Material based assets excluded from Browser

import azlmbr.materialeditor will fail with a ModuleNotFound error when using this script with Editor.exe
This is because azlmbr.materialeditor only binds to MaterialEditor.exe and not Editor.exe
You need to launch this script with MaterialEditor.exe in order for azlmbr.materialeditor to appear.
"""

import os
import sys

from PySide2 import QtWidgets

import azlmbr.paths

sys.path.append(os.path.join(azlmbr.paths.devassets, "Gem", "PythonTests"))

from editor_python_test_tools import pyside_utils
from Automated.atom_utils.material_editor_utils import MaterialEditorHelper


class NonMaterialAssetsExcludedInBrowserTest(MaterialEditorHelper):
    def __init__(self):
        MaterialEditorHelper.__init__(self, log_prefix="NonMaterialAssetsExcludedInBrowser_test_case")

    def run_test(self):
        """
        Summary:
        Non-Material based assets are excluded from Browser.

        Test Steps:
         1) Initialize QT objects
         2) Browse through paths and validate if expected items are present and exluded extensions are not present

        Expected Result:
        Only expected files like .fbx, .material should be shown in browser, other files like .txt or .json
        should not be shown in Asset Browser

        :return: None
        """

        # 1) Initialize QT objects
        editor_window = pyside_utils.get_editor_main_window()
        asset_browser = self.get_asset_browser(editor_window)
        tree = asset_browser.findChild(QtWidgets.QTreeView, "m_assetBrowserTreeViewWidget")

        # 2) Browse through paths and validate if expected items are present and exluded extensions are not present
        tree.expandAll()
        self.browse_validate_assets(
            tree, ("Gems", "Atom", "AtomTestData", "TestData", "LightingPresets"), "greenwich_park_03_2k_cm.exr",
        )
        self.browse_validate_assets(
            tree,
            ("Gems", "Atom", "AtomTestData", "TestData", "Materials", "StandardPbrTestCases"),
            "001_DefaultWhite.material",
        )
        self.browse_validate_assets(
            tree, ("Gems", "Atom", "AtomTestData", "TestData", "Multi-mat_fbx"), "multi-mat_1m_cube.fbx",
        )

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

    def browse_validate_assets(self, tree, path_to_verify, allowed_item):
        """
        Iterates each item of a folder under a given path and verifies if an item is present.
        Also verifies if any item ends with ".txt" or ".json". Log statements are printed accordingly.

        :param path_to_verify: Path in which items need to be browsed.
                                Ex: ("Gems", "Atom", "AtomTestData", "TestData", "LightingPresets")
        :param allowed_item: Specific item to verify inside folder. Ex: 001_DefaultWhite.material.
        :return: None
        """
        # Get the Model index for the path in which we need to verify assets
        model_index = pyside_utils.find_child_by_hierarchy(tree, *path_to_verify)
        # If path is invalid, print message accordingly
        if model_index is None:
            # NOTE: This does not necessarily mean that the functionality is not working as expected,
            # this may happen when the actual paths are updated, but this script is not updated, added the below
            # line to unexpected lines, so test would fail if that is the case, so that paths can be updated.
            print(f"Atom MaterialEditor asset path not found in browser: {path_to_verify}")
            return
        # else scroll in Asset Browser until we get to the folder
        tree.scrollTo(model_index)
        expected_item_found = False
        excluded_item_found = False
        model = tree.model()
        # Iterate through each item under that folder and perform validations
        for row in range(model.rowCount(model_index)):
            item_data = model.index(row, 0, model_index).data()
            if item_data == allowed_item:
                expected_item_found = True
            if item_data.endswith(".txt") or item_data.endswith(".json"):
                excluded_item_found = True
        # Print results accordingly
        if not expected_item_found:
            print(f"Expected item not found in folder {path_to_verify[-1]}")
        if excluded_item_found:
            print(f"Excluded item found in folder {path_to_verify[-1]}")


test = NonMaterialAssetsExcludedInBrowserTest()
test.run()
