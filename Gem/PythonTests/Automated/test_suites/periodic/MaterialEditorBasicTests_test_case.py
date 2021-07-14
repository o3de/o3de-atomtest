"""
Copyright (c) Contributors to the Open 3D Engine Project. For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT

import azlmbr.materialeditor will fail with a ModuleNotFound error when using this script with Editor.exe
This is because azlmbr.materialeditor only binds to MaterialEditor.exe and not Editor.exe
You need to launch this script with MaterialEditor.exe in order for azlmbr.materialeditor to appear.
"""

import os
import sys
import time

import azlmbr.paths
import azlmbr.math as math
import azlmbr.asset as asset
import azlmbr.bus as bus

sys.path.append(os.path.join(azlmbr.paths.devassets, "Gem", "PythonTests"))

import Automated.atom_utils.material_editor_utils as material_editor
from Automated.atom_utils.material_editor_utils import MaterialEditorHelper


class TestMaterialEditorBasicTests(MaterialEditorHelper):
    def __init__(self):
        MaterialEditorHelper.__init__(self, log_prefix="MaterialEditorBasicTests_test_case")

    def run_test(self):
        """
        Summary:
        Material Editor basic tests including the below
        1. Opening an Existing Asset
        1. Creating a New Asset
        1. Closing Selected Material
        1. Closing All Materials
        1. Closing all but Selected Material
        1. Saving Material
        1. Saving as a Child Material
        1. Saving as a New Material
        1. Saving all Open Materials

        Expected Result:
        All the above functions work as expected in Material Editor.

        :return: None
        """

        NEW_MATERIAL = "test_material.material"
        NEW_MATERIAL_1 = "test_material_1.material"
        NEW_MATERIAL_2 = "test_material_2.material"
        TEST_MATERIAL_1 = "001_DefaultWhite.material"
        TEST_MATERIAL_2 = "002_BaseColorLerp.material"
        TEST_MATERIAL_3 = "003_MetalMatte.material"
        TEST_DATA_PATH = os.path.join(
            azlmbr.paths.devroot, "Gems", "Atom", "TestData", "TestData", "Materials", "StandardPbrTestCases"
        )
        MATERIAL_TYPE_PATH = os.path.join(
            azlmbr.paths.devroot,
            "Gems",
            "Atom",
            "Feature",
            "Common",
            "Assets",
            "Materials",
            "Types",
            "StandardPBR.materialtype",
        )
        BUFFER = 0.00001

        def compare_colors(color1, color2, buffer=BUFFER):
            return (
                self.is_close(color1.r, color2.r, buffer)
                and self.is_close(color1.g, color2.g, buffer)
                and self.is_close(color1.b, color2.b, buffer)
            )

        #########################################
        # Test Case: Opening an Existing Asset
        #########################################
        # Open existing material
        document_id = material_editor.open_material(MATERIAL_TYPE_PATH)
        print(f"Material opened: {material_editor.is_open(document_id)}")

        # Verify if the test material exists initially
        target_path = os.path.join(azlmbr.paths.devroot, "AtomTest", "Materials", NEW_MATERIAL)
        print(f"Test asset doesn't exist initially: {not os.path.exists(target_path)}")

        ###################################
        # Test Case: Creating a New Asset
        ###################################
        # Create a new material using existing one
        material_editor.save_document_as_child(document_id, target_path)
        self.wait_for_condition(lambda: os.path.exists(target_path), 2.0)
        print(f"New asset created: {os.path.exists(target_path)}")

        # Verify if the newly created document is open
        new_document_id = material_editor.open_material(target_path)
        self.wait_for_condition(lambda: material_editor.is_open(new_document_id))
        print(f"New Material opened: {material_editor.is_open(new_document_id)}")

        ########################################
        # Test Case: Closing Selected Material
        ########################################
        # Close selected material
        print(f"Material closed: {material_editor.close_document(new_document_id)}")

        # Open materials initially
        document1_id, document2_id, document3_id = (
            material_editor.open_material(os.path.join(TEST_DATA_PATH, material))
            for material in [TEST_MATERIAL_1, TEST_MATERIAL_2, TEST_MATERIAL_3]
        )

        ####################################
        # Test Case: Closing All Materials
        ####################################
        # Close all documents and verify if closed
        print(f"All documents closed: {material_editor.close_all_documents()}")

        ################################################
        # Test Case: Closing all but Selected Material
        ################################################
        document1_id, document2_id, document3_id = (
            material_editor.open_material(os.path.join(TEST_DATA_PATH, material))
            for material in [TEST_MATERIAL_1, TEST_MATERIAL_2, TEST_MATERIAL_3]
        )
        result = material_editor.close_all_except_selected(document1_id)
        print(f"Close All Except Selected worked as expected: {result and material_editor.is_open(document1_id)}")

        ##############################################################################################################
        # Test Case: Saving Material
        # Test Case: Saving as a Child Material
        # Test Case: Saving as a New Material
        ##############################################################################################################
        document_id = material_editor.open_material(os.path.join(TEST_DATA_PATH, TEST_MATERIAL_1))
        property_name = azlmbr.name.Name("baseColor.color")
        initial_color = material_editor.get_property(document_id, property_name)
        # Assign new color to the material file and save the actual material
        expected_color = math.Color(0.25, 0.25, 0.25, 1.0)
        material_editor.set_property(document_id, property_name, expected_color)
        material_editor.save_document(document_id)

        # Assign new color to the material file and save the document as copy
        expected_color_1 = math.Color(0.5, 0.5, 0.5, 1.0)
        material_editor.set_property(document_id, property_name, expected_color_1)
        target_path_1 = os.path.join(azlmbr.paths.devroot, "AtomTest", "Materials", NEW_MATERIAL_1)
        material_editor.save_document_as_copy(document_id, target_path_1)
        time.sleep(2.0)

        # Assign new color to the material file save the document as child
        expected_color_2 = math.Color(0.75, 0.75, 0.75, 1.0)
        material_editor.set_property(document_id, property_name, expected_color_2)
        target_path_2 = os.path.join(azlmbr.paths.devroot, "AtomTest", "Materials", NEW_MATERIAL_2)
        material_editor.save_document_as_child(document_id, target_path_2)
        time.sleep(2.0)

        # Close/Reopen documents
        material_editor.close_all_documents()
        document_id = material_editor.open_material(os.path.join(TEST_DATA_PATH, TEST_MATERIAL_1))
        document1_id = material_editor.open_material(target_path_1)
        document2_id = material_editor.open_material(target_path_2)

        # Verify if the changes are saved in the actual document
        actual_color = material_editor.get_property(document_id, property_name)
        print(f"Actual Document saved with changes: {compare_colors(actual_color, expected_color)}")

        # Verify if the changes are saved in the document saved as copy
        actual_color = material_editor.get_property(document1_id, property_name)
        print(f"Document saved as copy is saved with changes: {compare_colors(actual_color, expected_color_1)}")

        # Verify if the changes are saved in the document saved as child
        actual_color = material_editor.get_property(document2_id, property_name)
        print(f"Document saved as child is saved with changes: {compare_colors(actual_color, expected_color_2)}")

        # Revert back the changes in the actual document
        material_editor.set_property(document_id, property_name, initial_color)
        material_editor.save_document(document_id)
        material_editor.close_all_documents()

        ########################################
        # Test Case: Saving all Open Materials
        ########################################
        # Open first material and make change to the values
        document1_id = material_editor.open_material(os.path.join(TEST_DATA_PATH, TEST_MATERIAL_1))
        property1_name = azlmbr.name.Name("metallic.factor")
        initial_metalic_factor = material_editor.get_property(document1_id, property1_name)
        expected_metallic_factor = 0.444
        material_editor.set_property(document1_id, property1_name, expected_metallic_factor)

        # Open second material and make change to the values
        document2_id = material_editor.open_material(os.path.join(TEST_DATA_PATH, TEST_MATERIAL_2))
        property2_name = azlmbr.name.Name("baseColor.color")
        initial_color = material_editor.get_property(document2_id, property2_name)
        expected_color = math.Color(0.4156, 0.0196, 0.6862, 1.0)
        material_editor.set_property(document2_id, property2_name, expected_color)

        # Save all and close all documents
        material_editor.save_all()
        material_editor.close_all_documents()

        # Reopen materials and verify values
        document1_id = material_editor.open_material(os.path.join(TEST_DATA_PATH, TEST_MATERIAL_1))
        result = self.is_close(
            material_editor.get_property(document1_id, property1_name), expected_metallic_factor, BUFFER
        )
        document2_id = material_editor.open_material(os.path.join(TEST_DATA_PATH, TEST_MATERIAL_2))
        result = result and compare_colors(expected_color, material_editor.get_property(document2_id, property2_name))
        print(f"Save All worked as expected: {result}")

        # Revert the changes made
        material_editor.set_property(document1_id, property1_name, initial_metalic_factor)
        material_editor.set_property(document2_id, property2_name, initial_color)
        material_editor.save_all()
        material_editor.close_all_documents()


test = TestMaterialEditorBasicTests()
test.run()
