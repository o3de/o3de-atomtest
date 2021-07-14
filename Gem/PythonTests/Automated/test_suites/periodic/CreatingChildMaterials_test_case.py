"""
All or portions of this file Copyright (c) Amazon.com, Inc. or its affiliates or
its licensors.

For complete copyright and license terms please see the LICENSE at the root of this
distribution (the "License"). All use of this software is governed by the License,
or, if provided, by the license below or the license accompanying this file. Do not
remove or modify any license notices. This file is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

Test for Creating child materials

import azlmbr.materialeditor will fail with a ModuleNotFound error when using this script with Editor.exe
This is because azlmbr.materialeditor only binds to MaterialEditor.exe and not Editor.exe
You need to launch this script with MaterialEditor.exe in order for azlmbr.materialeditor to appear.
"""

import os
import sys
import time

import azlmbr.paths
import azlmbr.math as math

sys.path.append(os.path.join(azlmbr.paths.devassets, "Gem", "PythonTests"))

from Automated.atom_utils.material_editor_utils import MaterialEditorHelper
import Automated.atom_utils.material_editor_utils as material_editor_utils

ASSET = "001_DefaultWhite.material"
CHILD_ASSET = "test_child_material.material"
ASSET_PATH = os.path.join(
    azlmbr.paths.devroot, "Gems", "Atom", "TestData", "TestData", "Materials", "StandardPbrTestCases"
)
BUFFER = 0.00001
COLOR_PROPERTY_NAME = azlmbr.name.Name("baseColor.color")


class CreatingChildMaterialsTest(MaterialEditorHelper):
    def __init__(self):
        MaterialEditorHelper.__init__(self, log_prefix="CreatingChildMaterials_test_case")

    def run_test(self):
        """
        Summary:
        Test for Creating child materials

        Test Steps:
        1) Open parent material
        2) Create child material and verify if exists
        3) Get the initial color of child material
        4) Close child material and open the parent material
        5) Update color value in parent document and save it
        6) Reopen child material and verify color
        7) Reset the parent material color

        Expected Result:
        A material utilizing all of the properties of the original parent is created.
        After updating color in parent material and upon opening child material, it should load and now
        inherit the changed color appearing darker red/grey, identical to '001_defaultwhite.material'

        :return: None
        """

        # 1) Open parent material
        parent_doc_id = material_editor_utils.open_material(os.path.join(ASSET_PATH, ASSET))

        # 2) Create child material and verify if exists
        material_editor_utils.save_document_as_child(parent_doc_id, os.path.join(ASSET_PATH, CHILD_ASSET))
        time.sleep(2.0)
        print(f"Child Material created: {os.path.exists(os.path.join(ASSET_PATH, CHILD_ASSET))}")

        # 3) Get the initial color of child material
        child_doc_id = material_editor_utils.open_material(os.path.join(ASSET_PATH, CHILD_ASSET))

        # 4) Close child material and open the parent material
        material_editor_utils.close_document(child_doc_id)
        parent_doc_id = material_editor_utils.open_material(os.path.join(ASSET_PATH, ASSET))

        # 5) Update color value in parent document and save it
        parent_new_color = math.Color(102.0 / 255.0, 30.0 / 255.0, 30.0 / 255.0, 255.0 / 255.0)
        material_editor_utils.set_property(parent_doc_id, COLOR_PROPERTY_NAME, parent_new_color)
        material_editor_utils.save_document(parent_doc_id)

        # 6) Reopen child material and verify color
        child_doc_id = material_editor_utils.open_material(os.path.join(ASSET_PATH, CHILD_ASSET))
        # TODO: Need to take screenshot

        # 7) Reset the parent material color
        parent_doc_id = material_editor_utils.open_material(os.path.join(ASSET_PATH, ASSET))
        initial_base_color = math.Color(255.0 / 255.0, 255.0 / 255.0, 255.0 / 255.0, 255.0 / 255.0)
        material_editor_utils.set_property(parent_doc_id, COLOR_PROPERTY_NAME, initial_base_color)
        material_editor_utils.save_document(parent_doc_id)
        print("Parent material reset done")


test = CreatingChildMaterialsTest()
test.run()
