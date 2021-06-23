"""
Copyright (c) Contributors to the Open 3D Engine Project

SPDX-License-Identifier: Apache-2.0 OR MIT

import azlmbr.materialeditor will fail with a ModuleNotFound error when using this script with Editor.exe
This is because azlmbr.materialeditor only binds to MaterialEditor.exe and not Editor.exe
You need to launch this script with MaterialEditor.exe in order for azlmbr.materialeditor to appear.
"""

import os
import sys

import azlmbr.paths

sys.path.append(os.path.join(azlmbr.paths.devroot, "AtomTest", "Gem", "PythonTests"))

import Automated.atom_utils.material_editor_utils as material_editor
from Automated.atom_utils.material_editor_utils import MaterialEditorHelper


class TestViewAssetBrowserMaterialInspector(MaterialEditorHelper):
    def __init__(self):
        MaterialEditorHelper.__init__(self, log_prefix="ViewAssetBrowserMaterialInspector")

    def run_test(self):
        """
        Summary:
        Opening/Closing Asset Browser and Material Inspector in Material editor.

        Expected Result:
        The Asset Browser disappears if it is currently available, and reappears if it is currently disabled.
        The Material Inspector disappears if it is currently available, and reappears if it is currently disabled.

        :return: None
        """

        def verify_pane_visibility(pane_name):
            initial_value = material_editor.is_pane_visible(pane_name)
            material_editor.set_pane_visibility(pane_name, not initial_value)
            result = (material_editor.is_pane_visible(pane_name) is not initial_value)
            material_editor.set_pane_visibility(pane_name, initial_value)
            result = result and (initial_value is material_editor.is_pane_visible(pane_name))
            print(f"{pane_name} visibility working as expected: {result}")

            
        # Asset Browser and Material Inspector are enabled by default
        # Verify Asset Browser visibility
        verify_pane_visibility("Asset Browser")

        # Verify Material Inspector visibility
        verify_pane_visibility("Inspector")

test = TestViewAssetBrowserMaterialInspector()
test.run()