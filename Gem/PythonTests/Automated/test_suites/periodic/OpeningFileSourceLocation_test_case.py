"""
All or portions of this file Copyright (c) Amazon.com, Inc. or its affiliates or
its licensors.
For complete copyright and license terms please see the LICENSE at the root of this
distribution (the "License"). All use of this software is governed by the License,
or, if provided, by the license below or the license accompanying this file. Do not
remove or modify any license notices. This file is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.


Opening File Source Location

import azlmbr.materialeditor will fail with a ModuleNotFound error when using this script with Editor.exe
This is because azlmbr.materialeditor only binds to MaterialEditor.exe and not Editor.exe
You need to launch this script with MaterialEditor.exe in order for azlmbr.materialeditor to appear.
"""

import os
import sys
import ctypes
import azlmbr.paths
from editor_python_test_tools import pyside_utils
from PySide2 import QtWidgets

sys.path.append(os.path.join(azlmbr.paths.devroot, "AtomTest", "Gem", "PythonTests"))

from Automated.atom_utils.material_editor_utils import MaterialEditorHelper

MATERIAL_NAME = "beach_parking_1k_iblglobalcm.exr"

class TestOpeningFileSourceLocation(MaterialEditorHelper):
    def __init__(self):
        MaterialEditorHelper.__init__(self, log_prefix="OpeningFileSourceLocation")

    def run_test(self):
        """
        Summary:
        Opening File Source Location

        Test Steps:
        1) Initialize QT objects
        2) Navigate to Gems\Atom\TestData\TestData\LightingPresets\beach_parking_1k_iblglobalcm.exr in Material Browser
        3) Right click on beach_parking_1k_iblglobalcm.exr and Select 'Open in Explorer'
        4) Make sure beach_parking_1k_iblglobalcm.exr opened with relative path: \dev\Gems\Atom\TestData\TestData\LightingPresets in WindowsExplorer

        Expected Result:
        A windows explorer opens up with the relative path:
        \dev\Gems\Atom\TestData\TestData\LightingPresets

        :return: None
        """

        # 1) Initialize QT objects
        editor_window = pyside_utils.get_editor_main_window()
        asset_browser = self.get_asset_browser(editor_window)
        search_frame = asset_browser.findChild(QtWidgets.QFrame, "m_searchWidget")
        search_bar = search_frame.findChild(QtWidgets.QWidget, "textSearch")
        tree = asset_browser.findChild(QtWidgets.QTreeView, "m_assetBrowserTreeViewWidget")

        # 2) Navigate to Gems\Atom\TestData\TestData\LightingPresets\beach_parking_1k_iblglobalcm.exr in Material Browser
        search_bar.setText(MATERIAL_NAME)
        self.wait_for_condition(lambda: self.find_material_in_browser(tree) is not None, 2.0)
        model_index = pyside_utils.find_child_by_pattern(tree, MATERIAL_NAME)

        # 3) Right click on beach_parking_1k_iblglobalcm.exr and Select 'Open in Explorer'
        pyside_utils.item_view_index_mouse_click(tree, model_index)
        pyside_utils.trigger_context_menu_entry(tree, "Open in Explorer", index=model_index)

        # 4) Make sure beach_parking_1k_iblglobalcm.exr opened with relative path: \dev\Gems\Atom\TestData\TestData\LightingPresets in WindowsExplorer
        self.wait_for_condition(lambda: self.window_exists("LightingPresets"), 2.0)
        if self.window_exists("LightingPresets"):
            print(
                "beach_parking_1k_iblglobalcm.exr opened with relative path: \dev\Gems\Atom\TestData\TestData\LightingPresets in WindowsExplorer"
            )

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

    def window_exists(self, title):
        """
        Finds a material is opened or not in Windows Explorer
        :param title - Window title to be searched
        :returns 1 If Window found, else 0
        """
        EnumWindows = ctypes.windll.user32.EnumWindows
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
        GetWindowText = ctypes.windll.user32.GetWindowTextW
        GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
        IsWindowVisible = ctypes.windll.user32.IsWindowVisible
        status = []

        def foreach_window(hwnd, lParam):
            """
            Finds a window is opened or not based on windows title
            :param hwnd - Handle to A Window
            :param lParam - Signed 64-bit value in 64-bit Windows
            """
            if IsWindowVisible(hwnd):
                length = GetWindowTextLength(hwnd)
                buff = ctypes.create_unicode_buffer(length + 1)
                GetWindowText(hwnd, buff, length + 1)
                if buff.value == title:
                    status.append(True)
                    return False
                return True

        EnumWindows(EnumWindowsProc(foreach_window), 0)
        return len(status) > 0

test = TestOpeningFileSourceLocation()
test.run_test()
