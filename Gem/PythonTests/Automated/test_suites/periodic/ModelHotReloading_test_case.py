"""
Copyright (c) Contributors to the Open 3D Engine Project.
For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT
"""

import os
import shutil
import sys
from functools import partial

import azlmbr.editor
import azlmbr.legacy.general as general
import azlmbr.paths
import azlmbr.asset

sys.path.append(os.path.join(azlmbr.paths.devassets, "Gem", "PythonTests"))

from Automated.atom_utils.automated_test_utils import TestHelper as helper
from Automated.atom_utils.screenshot_utils import ScreenshotHelper
from Automated.atom_utils import hydra_editor_utils as hydra

class ModelReloadHelper():
    def __init__(self):
        self.is_model_ready = False
    
    def model_is_ready_predicate(self):
        """
        A predicate function what will be used in wait_for_condition.
        """
        return self.is_model_ready

    def on_model_ready(self, parameters):
        self.is_model_ready = True

    def copy_file_and_wait_for_on_model_ready(self, entityId, sourceFile):
        # Connect to the MeshNotificationBus
        # Listen for notifications when entities are created/deleted
        self.on_model_ready_handler = azlmbr.bus.NotificationHandler('MeshComponentNotificationBus')
        self.on_model_ready_handler.connect(entityId)
        self.on_model_ready_handler.add_callback('OnModelReady', self.on_model_ready)
        # Set is_model_ready to false after connecting, but before copying the new model
        # in case an OnModelReady event is fired when adding the callback
        self.is_model_ready = False
        if copy_file(sourceFile, 'Objects/ModelHotReload/hotreload.fbx'):
            return helper.wait_for_condition(lambda: self.is_model_ready, 20.0)
        else:
            # copy_file failed
            return False

def run():
    """
    Test Case - Material:
    1. Opens the "Empty" level
    2. Creates a new entity and attaches the Mesh+Material components to it.
    3. Sets a camera to point at the entity.
    4. Applies a material that will display the vertex color.
    5. Applies a mesh that does not exist yet to the Mesh component.
    6. Copies a model with a vertex color stream to the location of the asset applied to the mesh component.
    7. Verifies the vertex color is consumed by a shader correctly via screenshot comparison.
    8. Reloads the model using one without a vertex color stream.
    9. Verifies the vertex color is no longer consumed by the shader via screenshot comparison.
    10. Reloads the model using one with multiple materials
    11. Verifies the correct material slots appear on the material component.
    12. Reloads the model using one with different materials and multiple lods.
    13. Verifies the correct material slots appear on the material component.
    14. Reloads the model using one without lods and with an extra color stream.
    15. Verifies the correct material slots appear on the material component.
    16. Closes the Editor and the test ends.

    :return: None
    """
    # Open EmptyLevel.
    helper.init_idle()
    helper.open_level("EmptyLevel")

    # Create a new entity and attach a Mesh+Material component to it.
    mesh_offset = azlmbr.math.Vector3(4.5, 3.0, 0.0)
    my_entity_id = azlmbr.editor.ToolsApplicationRequestBus(azlmbr.bus.Broadcast, 'CreateNewEntity', azlmbr.entity.EntityId())
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetWorldTranslation", my_entity_id, mesh_offset)
    if my_entity_id.IsValid():
        general.log("Entity successfully created.")

    mesh_component = helper.attach_component_to_entity(my_entity_id, 'Mesh')
    material_component = helper.attach_component_to_entity(my_entity_id, 'Material')

    
    # Find the entity with a camera  
    search_filter = azlmbr.entity.SearchFilter()
    search_filter.names = ['Camera']
    camera_entity_id = azlmbr.entity.SearchBus(azlmbr.bus.Broadcast, 'SearchEntities', search_filter)[0]

    # Make the camera look at the mesh component entity
    camera_position = mesh_offset.Add(azlmbr.math.Vector3(-5.0, 0.0, 0.0))
    forward_axis = 2 #YPositive
    camera_transform = azlmbr.math.Transform_CreateLookAt(camera_position, mesh_offset, forward_axis)
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetWorldTM", camera_entity_id, camera_transform)
    azlmbr.editor.EditorCameraRequestBus(
        azlmbr.bus.Broadcast, "SetViewAndMovementLockFromEntityPerspective", camera_entity_id, False)

    # Apply a material that will display the vertex color
    display_vertex_color_path = os.path.join("testdata", "objects", "modelhotreload", "displayvertexcolor.azmaterial")
    display_vertex_color_asset_id = hydra.get_asset_by_path(display_vertex_color_path)
    property_path = 'Default Material|Material Asset'
    azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'SetComponentProperty', material_component, property_path, display_vertex_color_asset_id)

    # Set mesh asset 'testdata/objects/modelhotreload/hotreload.azmodel'
    # Note, this mesh does not yet exist. Part of the test is that it reloads once it is added
    # Since it doesn't exist in the asset catalog yet, and we have no way to auto-generate the correct sub-id, we must use the hard coded assetId
    model_id = azlmbr.asset.AssetId_CreateString("{66ADF6FF-3CA4-51F6-9681-5697D4A29F56}:10241ecb")
    mesh_property_path = 'Controller|Configuration|Mesh Asset'
    newObj = azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'SetComponentProperty', mesh_component, mesh_property_path, model_id)

    model_reload_helper = ModelReloadHelper()

    # Copy the vertexcolor.fbx file to the location of hotreload.azmodel, and wait for it to be ready
    if not model_reload_helper.copy_file_and_wait_for_on_model_ready(my_entity_id, 'Objects/ModelHotReload/vertexcolor.fbx'):
        general.log("OnModelReady never happened - vertexcolor.fbx")

    # Use a screenshot for validation since the presence of a vertex color stream should change the appearance of the object
    screenshot_helper = ScreenshotHelper(general.idle_wait_frames)
    screenshot_helper.capture_screenshot_blocking_in_game_mode('screenshot_atom_ModelHotReload_VertexColor.ppm')

    # Test that removing a vertex stream functions
    if not model_reload_helper.copy_file_and_wait_for_on_model_ready(my_entity_id, 'Objects/ModelHotReload/novertexcolor.fbx'):
        general.log("OnModelReady never happened - novertexcolor.fbx")

    # Use a screenshot for validation since the absence of a vertex color stream should change the appearance of the object
    screenshot_helper.capture_screenshot_blocking_in_game_mode('screenshot_atom_ModelHotReload_NoVertexColor.ppm')
    
    # hot-reload the mesh that multiple materials, plus more/fewer vertices
    if not model_reload_helper.copy_file_and_wait_for_on_model_ready(my_entity_id, 'Multi-mat_fbx/multi-mat_mesh-groups_1m_cubes.fbx'):
        general.log("OnModelReady never happened - multi-mat_mesh-groups_1m_cubes.fbx")

    # Use the presence of multiple material slots in the material component to validate that the model was reloaded
    # and to verify the material component was updated
    lod_material_list = ["StingrayPBS1", "Red_Xaxis", "Green_Yaxis", "Blue_Zaxis", "With_Texture"]
    model_material_override_lod = 18446744073709551615
    material_label_dict = {
        model_material_override_lod:lod_material_list, 
        0:lod_material_list,
        }    
    validate_material_slot_labels(my_entity_id, material_label_dict)

    # Test that increasing the lod count functions
    if not model_reload_helper.copy_file_and_wait_for_on_model_ready(my_entity_id, 'Objects/ModelHotReload/sphere_5lods.fbx'):
        general.log("OnModelReady never happened - sphere_5lods.fbx")
    
    # The model material overrides have 5 slots, each individual lod only has 1 slot
    material_label_dict = {
        model_material_override_lod:["lambert0", "lambert3", "lambert4", "lambert5", "lambert6"],
        0:["lambert0"],
        1:["lambert3"],
        2:["lambert4"],
        3:["lambert5"],
        4:["lambert6"],
        }
    validate_material_slot_labels(my_entity_id, material_label_dict)

    # Test that adding a vertex stream and removing lods functions
    if not model_reload_helper.copy_file_and_wait_for_on_model_ready(my_entity_id, 'Objects/ModelHotReload/vertexcolor.fbx'):
        general.log("OnModelReady never happened - vertexcolor.fbx")
    # Use the presence of a single material slot in the material component to validate the model reloaded
    lod_material_list = ["Material"]
    material_label_dict = {
        model_material_override_lod:lod_material_list,
        0:lod_material_list,
        }
    validate_material_slot_labels(my_entity_id, material_label_dict)
    print_material_slot_labels(my_entity_id)
    """
    Future steps for other test cases
    
    apply a material override to two of the materials
    apply a property override to one of the materials
    
    Default material not properly being cleared
    - apply default material on one model
    -- reload to different model (sphere5_lods)
    - apply material slot overrides
    - clear the default material assignment (this might have been done before reloading the mesh, or without reloading at all, just assigning a new mesh) (it might have been done before or after applying the slot overrides)
    - expected: slots without overrides use their default material
    - actual: slots without overrides use the old default material

    remove one of the materials
    change some faces to use the same material as one of the already overriden slots
    also change some faces to use one of the materials that has the default applied in the material component
    also change some faces to use a newly added material

    enable lod material override
    
    Repeat with the actor component
    Reload model with cloth component
    """

    
    # Close the Editor to end the test.
    helper.close_editor()

def print_material_slot_labels(entityId):
    # Helper function useful while writing/modifying the test that will output the available materials slots
    general.log("Printing Material Slot AssignmentIds and Labels")
    material_assignment_map = azlmbr.render.MaterialComponentRequestBus(azlmbr.bus.Event, 'GetOriginalMaterialAssignments', entityId)
    for assignment_id in material_assignment_map:
        general.log(f"  AssignementId (slotId:lod): {assignment_id.ToString()}")
        slot_label = azlmbr.render.MaterialComponentRequestBus(azlmbr.bus.Event, 'GetMaterialSlotLabel', entityId, assignment_id)
        general.log(f"  SlotLabel: {slot_label}")


def validate_material_slot_labels(entityId, material_label_dict):
    """
    Validate that the original material assignment map on the entity matches what is expected

    :param entityId: The entity with the material component
    :param material_label_dict: A dict where each key is an lod index and each value a list of expected material slot labels.
    :return: True if all the expected slot/lod combinations are found and no unexpected combinations are found. False otherwise.
    """
    # keep track of whether or not each materialLabel for each lod is found
    found_labels = dict()
    for lod in material_label_dict:
        found_labels[lod] = dict()
        for label in material_label_dict[lod]:
            found_labels[lod][label] = False

    # Look for lods or slots that were not expected. Mark the expected ones as found
    material_assignment_map = azlmbr.render.MaterialComponentRequestBus(azlmbr.bus.Event, 'GetOriginalMaterialAssignments', entityId)
    for assignment_id in material_assignment_map:
        # Ignore the default assignment, since it exists for every model/lod
        if not assignment_id.IsDefault():
            if assignment_id.lodIndex not in found_labels:
                general.log("There is an unexpected lod in the material map")
                general.log(f"  lod: {assignment_id.lodIndex}")
                return False
            else:
                slot_label = azlmbr.render.MaterialComponentRequestBus(azlmbr.bus.Event, 'GetMaterialSlotLabel', entityId, assignment_id)
                if slot_label not in found_labels[assignment_id.lodIndex]:
                    general.log("There is an unexpected material slot in the lod")
                    general.log(f"  lod: {assignment_id.lodIndex} slot label: {slot_label}")
                    return False
                else:
                    found_labels[assignment_id.lodIndex][slot_label] = True

    # Check to see that all the expected lods and labels were found
    for material_lod in found_labels:
        for label in found_labels[material_lod]:
            if not found_labels[material_lod][label]:
                general.log("There was an expected material slot/lod combination that was not found")
                general.log(f"  lod: {assignment_id.lodIndex} slot label: {slot_label}")
                return False

    # All the expected material slot/lod combinations were found
    return True

TESTDATA_ASSET_PATH = os.path.join(
    azlmbr.paths.devroot, "Gems", "Atom", "TestData", "TestData"
)

def copy_file(src_path, dst_path):
    src_path = os.path.join(TESTDATA_ASSET_PATH, src_path)
    dst_path = os.path.join(TESTDATA_ASSET_PATH, dst_path)
    dst_dir = os.path.dirname(dst_path)
    if not os.path.isdir(dst_dir):
        os.makedirs(dst_dir)
    try:
        shutil.copyfile(src_path, dst_path)
        return True
    except Exception as error:
        general.log(f"ERROR: {error}")
        return False

if __name__ == "__main__":
    run()
