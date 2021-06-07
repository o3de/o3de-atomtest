"""
All or portions of this file Copyright (c) Amazon.com, Inc. or its affiliates or
its licensors.

For complete copyright and license terms please see the LICENSE at the root of this
distribution (the "License"). All use of this software is governed by the License,
or, if provided, by the license below or the license accompanying this file. Do not
remove or modify any license notices. This file is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.


Creating Subfolders within Library

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


class TestCreatingSubfoldersInLibrary(MaterialEditorHelper):
    def __init__(self):
        MaterialEditorHelper.__init__(self, log_prefix="CreatingSubfoldersInLibrary_test_case")

    def run_test(self):
        """
        Summary:
        Creating Subfolders within Library

        Test Steps:
        1) Initialize QT objects
        2) Navigate to the test folder
        3) Right click and create new folder
        4) Verify if the folder is created

        Expected Result:
        A context menu appears allowing you to select various options.
        A Prompt to enter the name appears in it's own GUI.
        An empty library is created.

        :return: None
        """

        FOLDER_NAME = "AtomTestData"
        NEW_SUB_FOLDER = "New Sub Folder"
        SUB_FOLDER_PATH = os.path.join(azlmbr.paths.devroot, "Gems", "Atom", "TestData", NEW_SUB_FOLDER)
        self.focus_changed = False

        def get_asset_browser(editor_window):
            asset_browser = get_asset_browser_qt_object()
            if asset_browser is None or not asset_browser.isVisible():
                action = pyside_utils.find_child_by_pattern(editor_window, {"iconText": "Asset Browser"})
                action.trigger()
            self.wait_for_condition(lambda: get_asset_browser_qt_object() is not None)
            asset_browser = get_asset_browser_qt_object()
            return asset_browser

        def get_asset_browser_qt_object():
            return editor_window.findChild(QtWidgets.QDockWidget, "Asset Browser_DockWidget")

        def find_folder_in_browser():
            tree.expandAll()
            return pyside_utils.find_child_by_pattern(tree, FOLDER_NAME) is not None

        def on_focus_changed(old, new):
            """
            This method deals with the Modal Widget which opens after doing Right Click-> Create Sub Folder.
            Sets the folder name and click OK button.
            """
            modal_widget = QtWidgets.QApplication.activeModalWidget()
            if modal_widget and not self.focus_changed:
                self.focus_changed = True
                line_edit = modal_widget.findChild(QtWidgets.QLineEdit)
                line_edit.setText(NEW_SUB_FOLDER)
                button_box = modal_widget.findChild(QtWidgets.QDialogButtonBox)
                button_box.button(QtWidgets.QDialogButtonBox.Ok).click()

        # 1) Initialize QT objects
        editor_window = pyside_utils.get_editor_main_window()
        asset_browser = get_asset_browser(editor_window)
        search_frame = asset_browser.findChild(QtWidgets.QFrame, "m_searchWidget")
        search_bar = search_frame.findChild(QtWidgets.QWidget, "textSearch")
        tree = asset_browser.findChild(QtWidgets.QTreeView, "m_assetBrowserTreeViewWidget")

        # 2) Navigate to the test folder
        search_bar.setText(FOLDER_NAME)
        self.wait_for_condition(find_folder_in_browser, 2.0)
        model_index = pyside_utils.find_child_by_pattern(tree, FOLDER_NAME)

        # 3) Right click and create new folder
        tree.collapse(model_index)
        pyside_utils.item_view_index_mouse_click(tree, model_index)
        app = QtWidgets.QApplication.instance()
        try:
            app.focusChanged.connect(on_focus_changed)
            pyside_utils.trigger_context_menu_entry(tree, "Create new sub folder...", index=model_index)
        finally:
            app.focusChanged.disconnect(on_focus_changed)

        # 4) Verify if the folder is created
        result = self.wait_for_condition(lambda: os.path.exists(SUB_FOLDER_PATH))
        print(f"New sub folder created: {result}")


test = TestCreatingSubfoldersInLibrary()
test.run()
