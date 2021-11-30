"""
Copyright (c) Contributors to the Open 3D Engine Project.
For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT

Hydra script that is used to test the Mesh component functionality inside the Editor.
Opens the MeshTest level & creates an entity w/ Mesh component.
Modifies Mesh component properties: "Mesh Asset", "Sort Key", "Lod Override", & "Exclude from reflection cubemaps".
Results are verified using log messages & screenshot comparisons diffed against golden images.

See the run() function for more in-depth test info.
"""

import os
import sys

import azlmbr.editor
import azlmbr.legacy.general as general
import azlmbr.paths
from azlmbr.entity import EntityId

sys.path.append(os.path.join(azlmbr.paths.devassets, "Gem", "PythonTests"))

from Automated.atom_utils.automated_test_utils import TestHelper as helper
from Automated.atom_utils.screenshot_utils import ScreenshotHelper

COMPONENT_PROPERTIES = [
    'Controller',
    'Controller|Configuration',
    'Controller|Configuration|Mesh Asset',
    'Controller|Configuration|Sort Key',
    'Controller|Configuration|Lod Override',
    'Controller|Configuration|Exclude from reflection cubemaps'
]


def run():
    """
    Test Case - Mesh:
    1. Opens the "MeshTest" level
    2. Creates a new entity and attaches the Mesh component to it.
    3. Sets the Mesh component's "Mesh Asset" property to an expected .azmodel asset file.
    4. Sets the Mesh component's "Sort Key" property to 10.
    5. Sets the Mesh component's "Lod Override" property to 0.
    6. Sets the Mesh component's "Exclude from reflection cubemaps" property to True.
    7. Verifies all properties were set to the expected values above on the Mesh component.
    8. Enters game mode to take a screenshot for comparison.
    9. Closes the Editor and the test ends.

    Tests will fail immediately if any of these log lines are found:
    1. Trace::Assert
    2. Trace::Error
    3. Traceback (most recent call last):

    :return: None
    """
    # Open MeshTest level.
    helper.init_idle()
    helper.open_level("MeshTest")

    # Create a new entity and attach a Mesh component to it.
    myEntityId = azlmbr.editor.ToolsApplicationRequestBus(azlmbr.bus.Broadcast, 'CreateNewEntity', EntityId())
    azlmbr.editor.EditorEntityAPIBus(azlmbr.bus.Event, 'SetName', myEntityId, "Mesh")
    vec3 = azlmbr.math.Vector3(4.0, 2.0, 0.0)
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetWorldTranslation", myEntityId, vec3)
    if myEntityId.IsValid():
        general.log("Entity successfully created.")
    typeIdsList = [azlmbr.globals.property.EditorMeshComponentTypeId]
    componentOutcome = azlmbr.editor.EditorComponentAPIBus(azlmbr.bus.Broadcast, 'AddComponentsOfType', myEntityId, typeIdsList)
    if componentOutcome.IsSuccess():
        general.log("Component added to entity.")
    component = componentOutcome.GetValue()[0]
    helper.compare_property_list(component, COMPONENT_PROPERTIES)

    # Prepare the Mesh component properties to test by verifying assets exist in the expected file paths.
    mesh_asset_property_path = 'Controller|Configuration|Mesh Asset'
    sort_key_property_path = 'Controller|Configuration|Sort Key'
    lod_override_property_path = 'Controller|Configuration|Lod Override'
    exclude_from_reflection_cubemaps_value = True
    exclude_from_reflection_cubemaps_property_path = (
        'Controller|Configuration|Reflections|Exclude from reflection cubemaps')
    mesh_asset_filepath = 'objects/lucy/lucy_low.azmodel'
    mesh_asset_id = azlmbr.asset.AssetCatalogRequestBus(
        azlmbr.bus.Broadcast, 'GetAssetIdByPath', mesh_asset_filepath, azlmbr.math.Uuid(), False)
    mesh_asset_path = azlmbr.asset.AssetCatalogRequestBus(
        azlmbr.bus.Broadcast, 'GetAssetPathById', mesh_asset_id)
    if mesh_asset_path != None:
        general.log("Mesh asset for mesh component is valid.")

    # Set the Mesh component's "Mesh Asset" property to mesh_asset_id:
    azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'SetComponentProperty', component, mesh_asset_property_path, mesh_asset_id)

    # Set the Mesh component's "Sort Key" property to 10:
    azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'SetComponentProperty', component, sort_key_property_path, 10)

    # Set the Mesh component's "Lod Override" property to 0:
    azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'SetComponentProperty', component, lod_override_property_path, 0)

    # Set the "Exclude from reflection cubemaps" property to True:
    azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'SetComponentProperty', component, exclude_from_reflection_cubemaps_property_path,
        exclude_from_reflection_cubemaps_value)

    # Verify all set properties match the expected values that were set.
    asset_id = azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'GetComponentProperty', component, mesh_asset_property_path)
    if asset_id.GetValue().to_string() == mesh_asset_id.to_string():
        general.log("Mesh asset property of mesh is correctly set")
    sort_key = azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'GetComponentProperty', component, sort_key_property_path)
    if sort_key.GetValue() == 10:
        general.log("Sort key property of mesh is correctly set")
    lod_override = azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'GetComponentProperty', component, lod_override_property_path)
    if lod_override.GetValue() == 0:
        general.log("Lod override property of mesh is correctly set")
    exposure = azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'GetComponentProperty', component, exclude_from_reflection_cubemaps_property_path)
    if exposure.GetValue() == exclude_from_reflection_cubemaps_value:
        general.log("Exclude from reflection cubemaps property of mesh is correctly set")

    # Generate screenshot to compare with golden image, then close the Editor.
    ScreenshotHelper(general.idle_wait_frames).capture_screenshot_blocking_in_game_mode(
        'screenshot_atom_MeshComponent.ppm')
    helper.close_editor()


if __name__ == "__main__":
    run()
