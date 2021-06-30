"""
Copyright (c) Contributors to the Open 3D Engine Project. For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT

Hydra script that is used to test the Radius Weight Modifier component functionality inside the Editor.
Opens the EmptyLevel level & creates 2 entities: entityWithHighExposureAndRadiusWeightModifier + entityWithLowExposure
Attaches and modifies the Exposure Control, PostFX Layer, & Radius Weight Modifier components on the entities.
Three screenshots are then taken at 3 different x, y, z positions after setting up both entities.
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

from Automated.atom_utils.screenshot_utils import ScreenshotHelper
from Automated.atom_utils.automated_test_utils import TestHelper as helper

COMPONENT_PROPERTIES = [
    'Controller',
    'Controller|Configuration',
    'Controller|Configuration|Radius'
]
RADIUS = 5.0


def run():
    """
    Test Case - Radius Weight Modifier:
    1. Opens the "EmptyLevel" level
    2. Creates a "entityWithHighExposureAndRadiusWeightModifier" entity with an Exposure Control component attached.
    3. Sets the Exposure Control component's "Manual Compensation" property to 4.0 (high).
    4. Attaches a PostFX Layer & Radius Weight Modifier component to "entityWithHighExposureAndRadiusWeightModifier".
    5. Modifies the Radius Weight Modifier component's Radius property to x:512.0, y:512.0, z:34.0
    6. Creates a "entityWithLowExposure" entity and attaches an Exposure Control component.
    7. Sets the Exposure Control component's "Manual Compensation" property to -2.0 (low).
    8. Attaches a PostFX Layer component to "entityWithLowExposure" and set its Priority property to 1.
    9. Verifies Radius is correct for "entityWithHighExposureAndRadiusWeightModifier" Radius Weight Modifier component.
    10. Searches for the "Camera" entity, using it to rotate it to 3 different positions.
        It then enters game mode and takes a screenshot each time:
        - Position 1: 512.0, 512.0, 34.0
        - Position 2: 512.0, 514.5, 34.0
        - Position 3: 512.0, 520.0, 34.0
    11. The screenshots are compared against golden images to verify lerp effects on Radius Weight Modifier component.
    12. Prints general.log("Three screenshots taken.") then closes the Editor and the test ends.

    Tests will fail immediately if any of these log lines are found:
    1. Trace::Assert
    2. Trace::Error
    3. Traceback (most recent call last):

    :return: None
    """
    # Open EmptyLevel level.
    helper.init_idle()
    helper.open_level("EmptyLevel")

    # Create entity and attach an Exposure Control component then set its Manual Compensation property to 4.0 (high).
    entityWithHighExposureAndRadiusWeightModifier = azlmbr.editor.ToolsApplicationRequestBus(
        azlmbr.bus.Broadcast, 'CreateNewEntity', EntityId())
    exposure_component = helper.attach_component_to_entity(
        entityWithHighExposureAndRadiusWeightModifier, 'Exposure Control')
    azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast,
        'SetComponentProperty',
        exposure_component,
        'Controller|Configuration|Manual Compensation',
        4.0)

    # Attach PostFX Layer & Radius Weight Modifier components, then modify Radius property.
    helper.attach_component_to_entity(entityWithHighExposureAndRadiusWeightModifier, 'PostFX Layer')
    radius_weight_modifier_component = helper.attach_component_to_entity(
        entityWithHighExposureAndRadiusWeightModifier, 'Radius Weight Modifier')
    helper.compare_property_list(radius_weight_modifier_component, COMPONENT_PROPERTIES)
    radius_property_path = 'Controller|Configuration|Radius'
    azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast,
        'SetComponentProperty',
        radius_weight_modifier_component,
        radius_property_path,
        RADIUS)
    pos = azlmbr.math.Vector3(512.0, 512.0, 34.0)
    azlmbr.components.TransformBus(
        azlmbr.bus.Event, "SetWorldTranslation", entityWithHighExposureAndRadiusWeightModifier, pos)

    # Create entity and attach an Exposure Control component then set its Manual Compensation property to -2.0 (low).
    entityWithLowExposure = azlmbr.editor.ToolsApplicationRequestBus(
        azlmbr.bus.Broadcast, 'CreateNewEntity', EntityId())
    exposure_component = helper.attach_component_to_entity(entityWithLowExposure, 'Exposure Control')
    azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast,
        'SetComponentProperty',
        exposure_component,
        'Controller|Configuration|Manual Compensation',
        -2.0)

    # Attach PostFX Layer component and set its Priority property to 1
    postfx_layer_component = helper.attach_component_to_entity(entityWithLowExposure, 'PostFX Layer')
    azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast,
        'SetComponentProperty',
        postfx_layer_component,
        'Controller|Configuration|Priority',
        1)

    # Verify Radius Weight Modifier component's Radius property was set correctly.
    radius = azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'GetComponentProperty', radius_weight_modifier_component, radius_property_path)
    if radius.GetValue() == RADIUS:
        general.log("Radius property of radius weight modifier is correctly set")

    # Search for entity containing the camera so we can move it around and observe changes in exposure.
    searchFilter = azlmbr.entity.SearchFilter()
    searchFilter.names = ['Camera']
    cameraEntityId = azlmbr.entity.SearchBus(azlmbr.bus.Broadcast, 'SearchEntities', searchFilter)[0]

    # Take screenshots on multiple locations to verify lerp effect of Radius Weight Modifier component.
    new_position1 = azlmbr.math.Vector3(512.0, 512.0, 34.0)
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetWorldTranslation", cameraEntityId, new_position1)
    screenshot_helper = ScreenshotHelper(general.idle_wait_frames)
    screenshot_helper.capture_screenshot_blocking_in_game_mode(
        'screenshot_atom_RadiusWeightModifierComponent_FullExposure.ppm')
    new_position2 = azlmbr.math.Vector3(512.0, 514.5, 34.0)
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetWorldTranslation", cameraEntityId, new_position2)
    screenshot_helper.capture_screenshot_blocking_in_game_mode(
        'screenshot_atom_RadiusWeightModifierComponent_HalfExposure.ppm')
    new_position3 = azlmbr.math.Vector3(512.0, 520.0, 34.0)
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetWorldTranslation", cameraEntityId, new_position3)
    screenshot_helper.capture_screenshot_blocking_in_game_mode(
        'screenshot_atom_RadiusWeightModifierComponent_NoExposure.ppm')
    general.log("Three screenshots taken.")
    helper.close_editor()


if __name__ == "__main__":
    run()
