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
import time

import azlmbr.paths
from editor_python_test_tools import pyside_utils
from PySide2 import QtWidgets
import azlmbr.materialeditor.general as general

sys.path.append(os.path.join(azlmbr.paths.devroot, "AtomTest", "Gem", "PythonTests"))

import Automated.atom_utils.material_editor_utils as material_editor
from Automated.atom_utils.material_editor_utils import MaterialEditorHelper


class TestOpeningFileSourceLocation(MaterialEditorHelper):
    def __init__(self):
        MaterialEditorHelper.__init__(self, log_prefix="OpeningFileSourceLocation")

    def run_test(self):
        """
        Summary:
        Opening File Source Location

        Test Steps:
        1) Open Material Browser
        2) Navigate to Gems\Atom\TestData\TestData\LightingPresets\beach_parking_1k_iblglobalcm.exr in Material Browser
        3) Right click on beach_parking_1k_iblglobalcm.exr and Select 'Open in Explorer'
        4) Make sure beach_parking_1k_iblglobalcm.exr opened with relative path: \dev\Gems\Atom\TestData\TestData\LightingPresets in WindowsExplorer

        Expected Result:
        A windows explorer opens up with the relative path:
        \dev\Gems\Atom\TestData\TestData\LightingPresets

        :return: None
        """

        def titleExists(title):
            EnumWindows = ctypes.windll.user32.EnumWindows
            EnumWindowsProc = ctypes.WINFUNCTYPE(
                ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)
            )
            GetWindowText = ctypes.windll.user32.GetWindowTextW
            GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
            IsWindowVisible = ctypes.windll.user32.IsWindowVisible
            status = []

            def foreach_window(hwnd, lParam):
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


        # 1) Open Material Browser
        pane_name = "Asset Browser"
        result = material_editor.is_pane_visible(pane_name)
        if not result:
            material_editor.set_pane_visibility(pane_name, True)
        result = material_editor.is_pane_visible(pane_name)
        print(f"{pane_name} opened: {result}")
        general.idle_wait_frames(1)

        # 2) Navigate to Gems\Atom\TestData\TestData\LightingPresets\beach_parking_1k_iblglobalcm.exr in Material Browser
        editor_window = pyside_utils.get_editor_main_window()
        asset_browser = editor_window.findChildren(QtWidgets.QWidget, "Asset Browser")[0]
        search_bar = asset_browser.findChildren(QtWidgets.QLineEdit, "textSearch")[0]
        search_bar.setText("beach_parking_1k_iblglobalcm.exr")
        general.idle_wait_frames(1)

        # 3) Right click on beach_parking_1k_iblglobalcm.exr and Select 'Open in Explorer'
        asset_browser_tree = asset_browser.findChild(QtWidgets.QTreeView, "m_assetBrowserTreeViewWidget")
        asset_browser_tree.expandAll()
        model_index = pyside_utils.find_child_by_pattern(asset_browser_tree, "beach_parking_1k_iblglobalcm.exr")
        pyside_utils.trigger_context_menu_entry(asset_browser_tree, "Open in Explorer", index=model_index)
        general.idle_wait_frames(1)

        # 4) Make sure beach_parking_1k_iblglobalcm.exr opened with relative path: \dev\Gems\Atom\TestData\TestData\LightingPresets in WindowsExplorer
        while True:
            if titleExists("LightingPresets"):
                print("beach_parking_1k_iblglobalcm.exr opened with relative path: \dev\Gems\Atom\TestData\TestData\LightingPresets in WindowsExplorer")
                exit(0)
            time.sleep(1)


test = TestOpeningFileSourceLocation()
test.run()

