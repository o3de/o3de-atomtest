"""
Copyright (c) Contributors to the Open 3D Engine Project.
For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT

Hydra script that is used to test the Material component functionality inside the Editor.
Opens the MeshTest level & creates an entity w/ Mesh component, then uses this entity to test the Material component.
Uses 3 different types of materials: a grouping of materials, 3 different LOD materials, and 1 default material.
Results are verified using log messages & screenshot comparisons diffed against golden images.

See the run() function for more in-depth test info.
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
from Automated.atom_utils.hydra_editor_utils import \
    helper_create_entity_with_mesh
from Automated.atom_utils.screenshot_utils import ScreenshotHelper

TESTDATA_ASSET_PATH = os.path.join(
    azlmbr.paths.devroot, "Gems", "Atom", "TestData", "TestData"
)

class ModelReloadHelper():
    def __init__(self):
        self.isModelReady = False
    
    def model_is_ready_predicate(self):
        """
        A predicate function what will be used in wait_for_condition.
        """
        return self.isModelReady

    def on_model_ready(self, parameters):
        self.isModelReady = True

    def copy_file_and_wait_for_on_model_ready(self, entityId, sourceFile):
        self.isModelReady = False
        # Connect to the MeshNotificationBus
        # Listen for notifications when entities are created/deleted
        self.onModelReadyHandler = azlmbr.bus.NotificationHandler('MeshComponentNotificationBus')
        self.onModelReadyHandler.connect(entityId)
        self.onModelReadyHandler.add_callback('OnModelReady', self.on_model_ready)
        if copy_file(sourceFile, 'Objects/ModelHotReload/hotreload.fbx'):
            waitCondition = partial(self.model_is_ready_predicate)
            if helper.wait_for_condition(waitCondition, 20.0):
                return True
            else:
                return False
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
    12. Closes the Editor and the test ends.

    :return: None
    """
    # Open EmptyLevel.
    helper.init_idle()
    helper.open_level("EmptyLevel")

    # Create a new entity and attach a Mesh+Material component to it.
    meshOffset = azlmbr.math.Vector3(4.5, 3.0, 0.0)
    myEntityId = azlmbr.editor.ToolsApplicationRequestBus(azlmbr.bus.Broadcast, 'CreateNewEntity', azlmbr.entity.EntityId())
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetWorldTranslation", myEntityId, meshOffset)
    if myEntityId.IsValid():
        general.log("Entity successfully created.")

    meshComponent = helper.attach_component_to_entity(myEntityId, 'Mesh')
    materialComponent = helper.attach_component_to_entity(myEntityId, 'Material')

    
    # Find the entity with a camera  
    searchFilter = azlmbr.entity.SearchFilter()
    searchFilter.names = ['Camera']
    cameraEntityId = azlmbr.entity.SearchBus(azlmbr.bus.Broadcast, 'SearchEntities', searchFilter)[0]

    # Make the camera look at the mesh component entity
    cameraPosition = meshOffset.Add(azlmbr.math.Vector3(-5.0, 0.0, 0.0))
    forwardAxis = 2 #YPositive
    cameraTransform = azlmbr.math.Transform_CreateLookAt(cameraPosition, meshOffset, forwardAxis)
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetWorldTM", cameraEntityId, cameraTransform)
    azlmbr.editor.EditorCameraRequestBus(
        azlmbr.bus.Broadcast, "SetViewAndMovementLockFromEntityPerspective", cameraEntityId, False)

    # Apply a material that will display the vertex color
    displayVertexColorPath = 'testdata/objects/modelhotreload/displayvertexcolor.azmaterial'
    displayVertexColorAssetId = azlmbr.asset.AssetCatalogRequestBus(azlmbr.bus.Broadcast, 'GetAssetIdByPath', displayVertexColorPath, azlmbr.math.Uuid(), False)
    property_path = 'Default Material|Material Asset'
    azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'SetComponentProperty', materialComponent, property_path, displayVertexColorAssetId)

    # Set mesh asset 'testdata/objects/modelhotreload/hotreload.azmodel'
    # Note, this mesh does not yet exist. Part of the test is that it reloads once it is added
    # Since it doesn't exist in the asset catalog yet, and we have no way to auto-generate the correct sub-id, we must use the hard coded assetId
    modelId = azlmbr.asset.AssetId_CreateString("{66ADF6FF-3CA4-51F6-9681-5697D4A29F56}:10241ecb")
    mesh_property_path = 'Controller|Configuration|Mesh Asset'
    newObj = azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'SetComponentProperty', meshComponent, mesh_property_path, modelId)

    modelReloadHelper = ModelReloadHelper()

    # Copy the vertexcolor.fbx file to the location of hotreload.azmodel, and wait for it to be ready
    if not modelReloadHelper.copy_file_and_wait_for_on_model_ready(myEntityId, 'Objects/ModelHotReload/vertexcolor.fbx'):
        general.log("OnModelReady never happened - vertexcolor.fbx")

    # Use a screenshot for validation since the presence of a vertex color stream should change the appearance of the object
    screenshotHelper = ScreenshotHelper(general.idle_wait_frames)
    screenshotHelper.capture_screenshot_blocking_in_game_mode('screenshot_atom_ModelHotReload_VertexColor.ppm')

    # Test that removing a vertex stream functions
    if not modelReloadHelper.copy_file_and_wait_for_on_model_ready(myEntityId, 'Objects/ModelHotReload/novertexcolor.fbx'):
        general.log("OnModelReady never happened - novertexcolor.fbx")

    # Use a screenshot for validation since the absence of a vertex color stream should change the appearance of the object
    screenshotHelper.capture_screenshot_blocking_in_game_mode('screenshot_atom_ModelHotReload_NoVertexColor.ppm')
    
    # hot-reload the mesh that multiple materials, plus more/fewer vertices
    if not modelReloadHelper.copy_file_and_wait_for_on_model_ready(myEntityId, 'Multi-mat_fbx/multi-mat_mesh-groups_1m_cubes.fbx'):
        general.log("OnModelReady never happened - multi-mat_mesh-groups_1m_cubes.fbx")

    # Use the presence of multiple material slots in the material component to validate that the model was reloaded
    # and to verify the material component was updated
    lodMaterialList = ["StingrayPBS1", "Red_Xaxis", "Green_Yaxis", "Blue_Zaxis", "With_Texture"]
    modelMaterialOverrideLod = 18446744073709551615
    materialLabelDict = {modelMaterialOverrideLod:lodMaterialList, 0:lodMaterialList}    
    validate_material_slot_labels(myEntityId, materialLabelDict)

    # Test that increasing the lod count functions
    if not modelReloadHelper.copy_file_and_wait_for_on_model_ready(myEntityId, 'Objects/ModelHotReload/sphere_5lods.fbx'):
        general.log("OnModelReady never happened - sphere_5lods.fbx")
    
    # The model material overrides have 5 slots, each individual lod only has 1 slot
    materialLabelDict = {modelMaterialOverrideLod:["lambert0", "lambert3", "lambert4", "lambert5", "lambert6"], 0:["lambert0"], 1:["lambert3"], 2:["lambert4"], 3:["lambert5"], 4:["lambert6"]}
    validate_material_slot_labels(myEntityId, materialLabelDict)

    # Test that adding a vertex stream and removing lods functions
    if not modelReloadHelper.copy_file_and_wait_for_on_model_ready(myEntityId, 'Objects/ModelHotReload/vertexcolor.fbx'):
        general.log("OnModelReady never happened - vertexcolor.fbx")
    # Use the presence of a single material slot in the material component to validate the m
    lodMaterialList = ["Material"]
    materialLabelDict = {modelMaterialOverrideLod:lodMaterialList, 0:lodMaterialList}
    validate_material_slot_labels(myEntityId, materialLabelDict)
    
    # Future steps for other test cases
    # apply a material override to two of the materials
    # apply a property override to one of the materials
    
    # Default material not properly being cleared
    # - apply default material on one model
    #  - reload to different model (sphere5_lods)
    # - apply material slot overrides
    # - clear the default material assignment (this might have been done before reloading the mesh, or without reloading at all, just assigning a new mesh) (it might have been done before or after applying the slot overrides)
    # - expected: slots without overrides use their default material
    # - actual: slots without overrides use the old default material

    # remove one of the materials
    # change some faces to use the same material as one of the already overriden slots
    # also change some faces to use one of the materials that has the default applied in the material component
    # also change some faces to use a newly added material

    # enable lod material override
    
    # Repeat with the actor component

    
    # Close the Editor to end the test.
    helper.close_editor()

def print_material_slot_labels(entityId):
    # Helper function useful while writing/modifying the test that will output the available materials slots
    general.log("Printing Material Slot AssignmentIds and Labels")
    materialAssignmentMap = azlmbr.render.MaterialComponentRequestBus(azlmbr.bus.Event, 'GetOriginalMaterialAssignments', entityId)
    for assignmentId in materialAssignmentMap:
        general.log("  AssignementId (slotId:lod): {0}".format(assignmentId.ToString()))
        slotLabel = azlmbr.render.MaterialComponentRequestBus(azlmbr.bus.Event, 'GetMaterialSlotLabel', entityId, assignmentId)
        general.log("  SlotLabel: {0}".format(slotLabel))


def validate_material_slot_labels(entityId, materialLabelDict):
    # keep track of whether or not each materialLabel for each lod is found
    foundLabels = dict()
    for lod in materialLabelDict:
        foundLabels[lod] = dict()
        for label in materialLabelDict[lod]:
            foundLabels[lod][label] = False

    # Look for lods or slots that were not expected. Mark the expected ones as found
    materialAssignmentMap = azlmbr.render.MaterialComponentRequestBus(azlmbr.bus.Event, 'GetOriginalMaterialAssignments', entityId)
    for assignmentId in materialAssignmentMap:
        # Ignore the default assignment, since it exists for every model/lod
        if not assignmentId.IsDefault():
            if assignmentId.lodIndex not in foundLabels:
                general.log("There is an unexpected lod in the material map")
                general.log("  lod: {0}".format(assignmentId.lodIndex))
                return False
            else:
                slotLabel = azlmbr.render.MaterialComponentRequestBus(azlmbr.bus.Event, 'GetMaterialSlotLabel', entityId, assignmentId)
                if slotLabel not in foundLabels[assignmentId.lodIndex]:
                    general.log("There is an unexpected material slot in the lod")
                    general.log("  lod: {0} slot label: {1}".format(assignmentId.lodIndex, slotLabel))
                    return False
                else:
                    foundLabels[assignmentId.lodIndex][slotLabel] = True

    # Check to see that all the expected lods and labels were found
    for materialLod in foundLabels:
        for label in foundLabels[materialLod]:
            if not foundLabels[materialLod][label]:
                general.log("There was an expected material slot/lod combination that was not found")
                general.log("  lod: {0} slot label: {1}".format(assignmentId.lodIndex, slotLabel))
                return False

    # All the expected material slot/lod combinations were found
    return True

def copy_file(srcPath, dstPath):
    srcPath = os.path.join(TESTDATA_ASSET_PATH, srcPath)
    dstPath = os.path.join(TESTDATA_ASSET_PATH, dstPath)
    dstDir = os.path.dirname(dstPath)
    if not os.path.isdir(dstDir):
        os.makedirs(dstDir)
    try:
        shutil.copyfile(srcPath, dstPath)
        return True
    except BaseException as error:
        general.log(f"ERROR: {error}")
        return False

if __name__ == "__main__":
    run()
