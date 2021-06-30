"""
Copyright (c) Contributors to the Open 3D Engine Project

SPDX-License-Identifier: Apache-2.0 OR MIT

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
from azlmbr.entity import EntityId

sys.path.append(os.path.join(azlmbr.paths.devroot, "AtomTest", "Gem", "PythonTests"))

from Automated.atom_utils.screenshot_utils import ScreenshotHelper
from Automated.atom_utils.automated_test_utils import TestHelper as helper

COMPONENT_PROPERTIES = [
    'Controller|Configuration|Gradient Sampler|Advanced|Scale',
    'Controller|Configuration|Gradient Sampler|Advanced|Rotate',
    'Controller|Configuration|Gradient Sampler|Advanced|Input Mid',
    'Controller|Configuration|Gradient Sampler|Advanced|Output Min',
    'Controller|Configuration|Gradient Sampler|Advanced|Translate',
    'Controller|Configuration|Gradient Sampler|Advanced|Input Min',
    'Controller|Configuration|Gradient Sampler|Advanced|Enable Transform',
    'Controller|Configuration|Gradient Sampler|Advanced|Input Max',
    'Controller|Configuration|Gradient Sampler|Advanced|Invert Input',
    'Controller|Configuration|Gradient Sampler|Gradient Entity Id',
    'Controller|Configuration|Gradient Sampler|Opacity',
    'Controller|Configuration|Gradient Sampler',
    'Controller|Configuration|Gradient Sampler|Advanced|Enable Levels',
    'Controller|Configuration|Gradient Sampler|Advanced|Output Max',
    'Controller',
    'Controller|Configuration'
]
OPACITY = 0.5


def run():
    """
    Test Case - PostFX Shape Weight Modifier:
    1. Opens the "EmptyLevel" level.
    2. Creates a high exposure entity with an Exposure Control component and sets it Manual Compensation to 4.0
    3. Creates a low exposure entity with the properties:
        - Manual Compensation: -2.0
        - Priority: 1.0
    4. Finds the Camera entity and manipulates it to 3 different positions to observe lerp effect:
        - Position 1: 512.0, 512.0, 34.0
        - Position 2: 512.0, 517.25, 34.0
        - Position 3: 512.0, 520.0, 34.0
    5. At each position, it will enter game mode and take a screenshot for comparison.
    6. Prints general.log("Three screenshots taken.") then closes the Editor and ends the test.

    Tests will fail immediately if any of these log lines are found:
    1. Trace::Assert
    2. Trace::Error
    3. Traceback (most recent call last):

    :return: None
    """
    helper.init_idle()
    helper.open_level("EmptyLevel")

    # Create high expsoure entity with an Exposure Control component w/ Manual Compensation set to 4.0
    entityId = create_high_exposure_entity()
    gradient_provider_entityId = create_gradient_provider_entity()

    # Create low exposure entity with -2.0 Manual Compensation and 1.0 Priority properties.
    create_low_exposure_entity()

    # Attach PostFX Gradient Weight Modifier component to the high exposure entity.
    gradient_weight_modifier_component = helper.attach_component_to_entity(entityId, 'PostFX Gradient Weight Modifier')

    # Verify all properties are present and set to the expected values.
    set_and_verify_gradient_weight_modifier_component(
        gradient_weight_modifier_component, gradient_provider_entity_id=gradient_provider_entityId)

    # Search for entity containing the camera so we can move it around and observe changes in exposure
    searchFilter = azlmbr.entity.SearchFilter()
    searchFilter.names = ['Camera']
    cameraEntityId = azlmbr.entity.SearchBus(azlmbr.bus.Broadcast, 'SearchEntities', searchFilter)[0]

    # Take screenshots on multiple locations to verify gradient weight modifier component
    new_position1 = azlmbr.math.Vector3(512.0, 512.0, 34.0)
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetWorldTranslation", cameraEntityId, new_position1)
    screenshot_helper = ScreenshotHelper(general.idle_wait_frames)
    screenshot_helper.capture_screenshot_blocking_in_game_mode(
        'screenshot_atom_GradientWeightModifierComponent_RandomExposure1.ppm')
    new_position2 = azlmbr.math.Vector3(512.0, 514.5, 34.0)
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetWorldTranslation", cameraEntityId, new_position2)
    screenshot_helper.capture_screenshot_blocking_in_game_mode(
        'screenshot_atom_GradientWeightModifierComponent_RandomExposure2.ppm')
    new_position3 = azlmbr.math.Vector3(512.0, 525.0, 34.0)
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetWorldTranslation", cameraEntityId, new_position3)
    screenshot_helper.capture_screenshot_blocking_in_game_mode(
        'screenshot_atom_GradientWeightModifierComponent_NoExposure.ppm')
    general.log("Three screenshots taken.")
    helper.close_editor()


def create_high_exposure_entity():
    entityId = azlmbr.editor.ToolsApplicationRequestBus(azlmbr.bus.Broadcast, 'CreateNewEntity', EntityId())
    exposure_component = helper.attach_component_to_entity(entityId, 'Exposure Control')
    helper.set_component_property(
        exposure_component,
        'Controller|Configuration|Manual Compensation',
        4.0
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


def create_gradient_provider_entity():
    entityId = azlmbr.editor.ToolsApplicationRequestBus(azlmbr.bus.Broadcast, 'CreateNewEntity', EntityId())
    sphere_shape_component = helper.attach_component_to_entity(entityId, 'Sphere Shape')
    helper.set_component_property(
        sphere_shape_component,
        'Sphere Shape|Sphere Configuration|Radius',
        5.0
    )
    helper.attach_component_to_entity(entityId, 'Perlin Noise Gradient')
    gradient_transform_modifier_component = helper.attach_component_to_entity(entityId, 'Gradient Transform Modifier')
    helper.set_component_property(
        gradient_transform_modifier_component,
        'Configuration|Wrapping Type',
        4  # clamp to zero
    )

    pos = azlmbr.math.Vector3(512.0, 512.0, 34.0)
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetWorldTranslation", entityId, pos)

    return entityId


def set_and_verify_gradient_weight_modifier_component(gradient_weight_modifier_component, **kwargs):
    gradientEntityId_property_path = 'Controller|Configuration|Gradient Sampler|Gradient Entity Id'
    opacity_property_path = 'Controller|Configuration|Gradient Sampler|Opacity'
    gradient_provider_entity_id = kwargs['gradient_provider_entity_id']

    # set properties of gradient weight modifier component
    helper.set_component_property(
        gradient_weight_modifier_component,
        gradientEntityId_property_path,
        gradient_provider_entity_id
    )
    helper.set_component_property(
        gradient_weight_modifier_component,
        opacity_property_path,
        OPACITY
    )

    # verify component properties
    helper.compare_property_list(gradient_weight_modifier_component, COMPONENT_PROPERTIES)
    gradient_id = azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'GetComponentProperty', gradient_weight_modifier_component,
        gradientEntityId_property_path)
    if gradient_id.GetValue() == gradient_provider_entity_id:
        general.log('Gradient Entity Id property of gradient weight modifier is correctly set')
    opacity = azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'GetComponentProperty', gradient_weight_modifier_component, opacity_property_path)
    if opacity.GetValue() == OPACITY:
        general.log('Opacity property of gradient weight modifier is correctly set')


if __name__ == "__main__":
    run()
