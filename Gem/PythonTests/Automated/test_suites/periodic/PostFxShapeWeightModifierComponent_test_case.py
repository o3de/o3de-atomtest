"""
All or portions of this file Copyright (c) Amazon.com, Inc. or its affiliates or
its licensors.

For complete copyright and license terms please see the LICENSE at the root of this
distribution (the "License"). All use of this software is governed by the License,
or, if provided, by the license below or the license accompanying this file. Do not
remove or modify any license notices. This file is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

Hydra script that is used to test the PostFX Shape Weight Modifier component functionality inside the Editor.
Opens the EmptyLevel level and creates a low exposure entity and a high exposure entity.
It then moves the camera in 3 different positions, taking a screenshot each time.
Results are verified using log messages & screenshot comparisons diffed against golden images.

See the run() function for more in-depth test info.
"""

import os
import sys

import azlmbr.editor
import azlmbr.legacy.general as general
import azlmbr.paths

sys.path.append(os.path.join(azlmbr.paths.devroot, "AtomTest", "Gem", "PythonTests"))

from Automated.atom_utils.screenshot_utils import ScreenshotHelper
from Automated.atom_utils.automated_test_utils import TestHelper as helper
from azlmbr.entity import EntityId

COMPONENT_PROPERTIES = [
    'Controller',
    'Controller|Configuration',
    'Controller|Configuration|Fall-off Distance'
]

FALLOFF_DIST = 0.5


def run():
    """
    Test Case - PostFX Shape Weight Modifier:
    1. Opens the "EmptyLevel" level.
    2. Creates a high exposure entity with an Exposure Control component and sets it Manual Compensation to 4.0
    3. Attaches a Sphere Shape component to the high exposure entity with a Radius of 5.0
    4. Attaches a Post FX Layer to the high exposure entity then sets its world translation to 512.0, 512.0, 34.0
    5. Attaches PostFX Shape Weight Modifier component to the high exposure entity and sets its Fall-off Distance to 0.5
    6. Creates a low exposure entity with a similar setup as the previous one, except:
        - Manual Compensation: -2.0
        - Priority: 1.0
    7. Finds the Camera entity and manipulates it to 3 different positions to observe lerp effect:
        - Position 1: 512.0, 512.0, 34.0
        - Position 2: 512.0, 517.25, 34.0
        - Position 3: 512.0, 520.0, 34.0
    8. At each position, it will enter game mode and take a screenshot for comparison.
    9. Prints general.log("Three screenshots taken.") then closes the Editor and ends the test.

    Tests will fail immediately if any of these log lines are found:
    1. Trace::Assert
    2. Trace::Error
    3. Traceback (most recent call last):

    :return: None
    """
    # Open EmptyLevel level.
    helper.init_idle()
    helper.open_level("EmptyLevel")

    # Create new entity with Exposure Control, Sphere Shape, and Post FX Layer.
    entityId = create_high_exposure_entity_with_sphere_shape()
    create_low_exposure_entity()

    # Attach PostFX Shape Weight Modifier component and set its Fall-off Distance.
    shape_weight_modifier_component = helper.attach_component_to_entity(entityId, 'PostFX Shape Weight Modifier')
    set_and_verify_shape_weight_modifier_component(shape_weight_modifier_component)

    # Search for entity containing the camera so we can move it around and observe changes in exposure
    searchFilter = azlmbr.entity.SearchFilter()
    searchFilter.names = ['Camera']
    cameraEntityId = azlmbr.entity.SearchBus(azlmbr.bus.Broadcast, 'SearchEntities', searchFilter)[0]

    # Take screenshots on multiple locations to verify lerp effect of shape weight modifier component
    new_position1 = azlmbr.math.Vector3(512.0, 512.0, 34.0)
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetWorldTranslation", cameraEntityId, new_position1)
    screenshot_helper = ScreenshotHelper(general.idle_wait_frames)
    screenshot_helper.capture_screenshot_blocking_in_game_mode(
        'screenshot_atom_ShapeWeightModifierComponent_FullExposure.ppm')
    new_position2 = azlmbr.math.Vector3(512.0, 517.25, 34.0)
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetWorldTranslation", cameraEntityId, new_position2)
    screenshot_helper.capture_screenshot_blocking_in_game_mode(
        'screenshot_atom_ShapeWeightModifierComponent_HalfExposure.ppm')
    new_position3 = azlmbr.math.Vector3(512.0, 520.0, 34.0)
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetWorldTranslation", cameraEntityId, new_position3)
    screenshot_helper.capture_screenshot_blocking_in_game_mode(
        'screenshot_atom_ShapeWeightModifierComponent_NoExposure.ppm')
    general.log("Three screenshots taken.")
    helper.close_editor()


def create_high_exposure_entity_with_sphere_shape():
    entityId = azlmbr.editor.ToolsApplicationRequestBus(azlmbr.bus.Broadcast, 'CreateNewEntity', EntityId())
    exposure_component = helper.attach_component_to_entity(entityId, 'Exposure Control')
    helper.set_component_property(
        exposure_component,
        'Controller|Configuration|Manual Compensation',
        4.0
    )
    sphere_shape_component = helper.attach_component_to_entity(entityId, 'Sphere Shape')
    helper.set_component_property(
        sphere_shape_component,
        'Sphere Shape|Sphere Configuration|Radius',
        5.0
    )
    helper.attach_component_to_entity(entityId, 'PostFX Layer')

    pos = azlmbr.math.Vector3(512.0, 512.0, 34.0)
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetWorldTranslation", entityId, pos)

    return entityId


def create_low_exposure_entity():
    entityId = azlmbr.editor.ToolsApplicationRequestBus(azlmbr.bus.Broadcast, 'CreateNewEntity', EntityId())
    exposure_component = helper.attach_component_to_entity(entityId, 'Exposure Control')
    helper.set_component_property(
        exposure_component,
        'Controller|Configuration|Manual Compensation',
        -2.0
    )
    postfx_layer_component = helper.attach_component_to_entity(entityId, 'PostFX Layer')
    helper.set_component_property(
        postfx_layer_component,
        'Controller|Configuration|Priority',
        1
    )


def set_and_verify_shape_weight_modifier_component(shape_weight_modifier_component):
    falloff_property_path = 'Controller|Configuration|Fall-off Distance'

    # set properties
    helper.set_component_property(
        shape_weight_modifier_component,
        falloff_property_path,
        FALLOFF_DIST
    )

    # verify component properties
    helper.compare_property_list(shape_weight_modifier_component, COMPONENT_PROPERTIES)
    falloff_dist = azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'GetComponentProperty', shape_weight_modifier_component, falloff_property_path)
    if falloff_dist.GetValue() == FALLOFF_DIST:
        general.log('Fall-off distance property of shape weight modifier is correctly set')


if __name__ == "__main__":
    run()
