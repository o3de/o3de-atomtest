"""
All or portions of this file Copyright (c) Amazon.com, Inc. or its affiliates or
its licensors.

For complete copyright and license terms please see the LICENSE at the root of this
distribution (the "License"). All use of this software is governed by the License,
or, if provided, by the license below or the license accompanying this file. Do not
remove or modify any license notices. This file is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

Hydra script that is used to test the Actor component functionality inside the Editor.
Opens the EmptyLevel level and creates an "Actor" entity and attaches an Actor component.
It then attaches a BURT/burtactor.actor asset file to the Actor component.
Several camera movements are made and screenshots taken.
Results are verified using log messages & screenshot comparisons diffed against golden images.

See the run() function for more in-depth test info.
"""

import os
import sys

import azlmbr.editor
import azlmbr.legacy.general as general
import azlmbr.paths
from azlmbr.entity import EntityId

sys.path.append(os.path.join(azlmbr.paths.devroot, "AtomTest", "Gem", "PythonTests"))

from Automated.atom_utils.automated_test_utils import TestHelper as helper
from Automated.atom_utils.screenshot_utils import ScreenshotHelper


def run():
    """
    Test Case - Actor:
    1. Opens the "EmptyLevel" level and creates a new "Actor" entity with Actor component attached.
    2. Sets the "BURT/burtactor.actor" asset file as the Actor component's asset.
    3. Verifies the "BURT/burtactor.actor" asset file was correctly set.
    4. Sets the Camera entity Translation and Rotation to face the Actor entity.
    5. Enters game mode and takes a screenshot for comparison.
    6. Closes the Editor and the test ends.

    Tests will fail immediately if any of these log lines are found:
    1. Trace::Assert
    2. Trace::Error
    3. Traceback (most recent call last):

    :return: None
    """
    # Open the EmptyLevel level.
    helper.init_idle()
    helper.open_level("EmptyLevel")

    # Create new entity
    myEntityId = azlmbr.editor.ToolsApplicationRequestBus(azlmbr.bus.Broadcast, 'CreateNewEntity', EntityId())
    azlmbr.editor.EditorEntityAPIBus(azlmbr.bus.Event, 'SetName', myEntityId, "Actor")
    vec3 = azlmbr.math.Vector3(4.0, 2.0, 0.0)
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetWorldTranslation", myEntityId, vec3)
    if myEntityId.IsValid():
        general.log("Entity successfully created.")

    # Attach the component
    actor_component = helper.attach_component_to_entity(myEntityId, 'Actor')

    # Set component properties
    actor_asset_property_path = 'Actor asset'
    actor_asset_filepath = 'BURT/burtactor.actor'
    actor_asset_id = azlmbr.asset.AssetCatalogRequestBus(
        azlmbr.bus.Broadcast, 'GetAssetIdByPath', actor_asset_filepath, azlmbr.math.Uuid(), False)
    actor_asset_path =  azlmbr.asset.AssetCatalogRequestBus(azlmbr.bus.Broadcast, 'GetAssetPathById', actor_asset_id)

    # check if the asset path is valid
    if actor_asset_path != None:
        general.log("Actor asset for actor component is valid.")
    azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'SetComponentProperty', actor_component, actor_asset_property_path, actor_asset_id)

    # verify that component contains the expected values
    asset_id = azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'GetComponentProperty', actor_component, actor_asset_property_path)
    if asset_id.GetValue().to_string() == actor_asset_id.to_string():
        general.log("Actor asset property of actor is correctly set")

    # Move camera so it sees the actor
    search_filter = azlmbr.entity.SearchFilter()
    search_filter.names = ['Camera']
    camera_entity_id = azlmbr.entity.SearchBus(azlmbr.bus.Broadcast, 'SearchEntities', search_filter)[0]

    # Move the camera near and facing the actor
    new_position = azlmbr.math.Vector3(4.0, 4.0, 1.0)
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetWorldTranslation", camera_entity_id, new_position)
    azlmbr.components.TransformBus(azlmbr.bus.Event, "RotateAroundLocalZ", camera_entity_id, 3.14)

    # generate screenshot to compare with golden
    ScreenshotHelper(general.idle_wait_frames).capture_screenshot_blocking_in_game_mode(
        'screenshot_atom_ActorComponent.ppm')
    helper.close_editor()


if __name__ == "__main__":
    run()
