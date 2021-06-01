"""
All or portions of this file Copyright (c) Amazon.com, Inc. or its affiliates or
its licensors.

For complete copyright and license terms please see the LICENSE at the root of this
distribution (the "License"). All use of this software is governed by the License,
or, if provided, by the license below or the license accompanying this file. Do not
remove or modify any license notices. This file is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""

# Test case ID : C34792870
# Test Case Title : PostFx Gradient Weight Modifier
# URL of the test case : https://testrail.agscollab.com/index.php?/cases/view/34792870

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
        4 # clamp to zero
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
    gradient_id = azlmbr.editor.EditorComponentAPIBus(azlmbr.bus.Broadcast, 'GetComponentProperty', gradient_weight_modifier_component, gradientEntityId_property_path)
    if gradient_id.GetValue() == gradient_provider_entity_id:
        general.log('Gradient Entity Id property of gradient weight modifier is correctly set')
    opacity = azlmbr.editor.EditorComponentAPIBus(azlmbr.bus.Broadcast, 'GetComponentProperty', gradient_weight_modifier_component, opacity_property_path)
    if opacity.GetValue() == OPACITY:
        general.log('Opacity property of gradient weight modifier is correctly set')


def run():
    helper.init_idle()
    helper.open_level("DefaultLevel")

    # create entities
    entityId = create_high_exposure_entity()
    gradient_provider_entityId = create_gradient_provider_entity()
    create_low_exposure_entity()

    # attach gradient weight modifier component
    gradient_weight_modifier_component = helper.attach_component_to_entity(entityId, 'PostFX Gradient Weight Modifier')
    set_and_verify_gradient_weight_modifier_component(gradient_weight_modifier_component, gradient_provider_entity_id=gradient_provider_entityId)

    # Search for entity containing the camera so we can move it around and observe changes in exposure
    searchFilter = azlmbr.entity.SearchFilter()
    searchFilter.names = ['Camera']
    cameraEntityId = azlmbr.entity.SearchBus(azlmbr.bus.Broadcast, 'SearchEntities', searchFilter)[0]

    # Take screenshots on multiple locations to verify gradient weight modifier component
    new_position1 = azlmbr.math.Vector3(512.0, 512.0, 34.0)
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetWorldTranslation", cameraEntityId, new_position1)
    screenshot_helper = ScreenshotHelper(general.idle_wait_frames)
    screenshot_helper.capture_screenshot_blocking_in_game_mode('screenshot_atom_GradientWeightModifierComponent_RandomExposure1.ppm')
    new_position2 = azlmbr.math.Vector3(512.0, 514.5, 34.0)
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetWorldTranslation", cameraEntityId, new_position2)
    screenshot_helper.capture_screenshot_blocking_in_game_mode('screenshot_atom_GradientWeightModifierComponent_RandomExposure2.ppm')
    new_position3 = azlmbr.math.Vector3(512.0, 525.0, 34.0)
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetWorldTranslation", cameraEntityId, new_position3)
    screenshot_helper.capture_screenshot_blocking_in_game_mode('screenshot_atom_GradientWeightModifierComponent_NoExposure.ppm')
    general.log("Three screenshots taken.")
    helper.close_editor()


if __name__ == "__main__":
    run()