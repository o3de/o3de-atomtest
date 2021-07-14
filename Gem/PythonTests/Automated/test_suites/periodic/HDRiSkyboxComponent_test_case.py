"""
Copyright (c) Contributors to the Open 3D Engine Project. For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT

Hydra script that is used to test the HDRi Skybox component functionality inside the Editor.
Opens the MeshTest level & creates an entity and attaches the HDRi Skybox component.
It will then add a texture, obtain cubemap + exposure properties, then take a screenshot in game mode.
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
    'Controller|Configuration|Cubemap Texture',
    'Controller|Configuration|Exposure'
]


def run():
    """
    Test Case - HDRi Skybox:
    1. Opens the "MeshTest" level
    2. Creates a new entity and attaches the HDRi Skybox component to it.
    3. Sets the HDRi Skybox component's Exposure to 1.
    4. Sets the HDRi Skybox component's Cubemap Texture using set file paths.
    5. Verifies the Cubemap Texture paths & Exposure values were set correctly after setting them.
    6. Enters game mode to take a screenshot for comparison, then exits game mode.
    7. Closes the Editor and the test ends.

    Tests will fail immediately if any of these log lines are found:
    1. Trace::Assert
    2. Trace::Error
    3. Traceback (most recent call last):

    :return: None
    """
    # Open MeshTest level.
    helper.init_idle()
    helper.open_level("MeshTest")

    # Create a new entity and attach an HDRi Skybox component to it.
    myEntityId = azlmbr.editor.ToolsApplicationRequestBus(azlmbr.bus.Broadcast, 'CreateNewEntity', EntityId())
    azlmbr.editor.EditorEntityAPIBus(azlmbr.bus.Event, 'SetName', myEntityId, "Skybox")
    if myEntityId.IsValid():
        general.log("Entity successfully created.")
    component = helper.attach_component_to_entity(myEntityId, 'HDRi Skybox')
    helper.compare_property_list(component, COMPONENT_PROPERTIES)

    # Set the Exposure and Cubemap Texture configurations for the HDRi Skybox component.
    exposure_property_path = 'Controller|Configuration|Exposure'
    exposure_value = 1
    cubemap_property_path = 'Controller|Configuration|Cubemap Texture'
    texture_filepath = 'lightingpresets/lowcontrast/artist_workshop_4k_iblskyboxcm.exr.streamingimage'
    texture_asset_id = azlmbr.asset.AssetCatalogRequestBus(
        azlmbr.bus.Broadcast, 'GetAssetIdByPath', texture_filepath, azlmbr.math.Uuid(), False)
    texture_asset_path = azlmbr.asset.AssetCatalogRequestBus(
        azlmbr.bus.Broadcast, 'GetAssetPathById', texture_asset_id)
    if texture_asset_path != None:
        general.log("Cubemap texture for skybox component is valid.")
    azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'SetComponentProperty', component, cubemap_property_path, texture_asset_id)
    azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'SetComponentProperty', component, exposure_property_path, exposure_value)

    # Verify the Exposure and Cubemap Texture were set correctly.
    asset_id = azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'GetComponentProperty', component, cubemap_property_path)
    if asset_id.GetValue().to_string() == texture_asset_id.to_string():
        general.log("Cubemap property of skybox is correctly set")
    exposure = azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'GetComponentProperty', component, exposure_property_path)
    if exposure.GetValue() == exposure_value:
        general.log("Exposure property of skybox is correctly set")

    # Generate screenshot to compare with golden image, then close the Editor.
    ScreenshotHelper(general.idle_wait_frames).capture_screenshot_blocking_in_game_mode(
        'screenshot_atom_HDRiSkyboxComponent.ppm')
    helper.close_editor()


if __name__ == "__main__":
    run()
