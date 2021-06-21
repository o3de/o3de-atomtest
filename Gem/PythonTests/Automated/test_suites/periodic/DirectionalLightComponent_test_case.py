"""
All or portions of this file Copyright (c) Amazon.com, Inc. or its affiliates or
its licensors.

For complete copyright and license terms please see the LICENSE at the root of this
distribution (the "License"). All use of this software is governed by the License,
or, if provided, by the license below or the license accompanying this file. Do not
remove or modify any license notices. This file is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

Hydra script that is used to test the Directional Light component functionality inside the Editor.
Opens the EmptyLevel level & creates a bunny and floor entity with components needed to test Directional Light.
It then makes 7 different configurations of Directional Light component property options.
A screenshot is taken for each of the 7 different configurations.
Results are verified using log messages & screenshot comparisons diffed against golden images.

See the run() function for more in-depth test info.
"""

import os
import sys
import math

import azlmbr.bus as bus
import azlmbr.components as components
import azlmbr.editor as editor
import azlmbr.legacy.general as general
import azlmbr.math
import azlmbr.paths

sys.path.append(os.path.join(azlmbr.paths.devroot, "AtomTest", "Gem", "PythonTests"))

from Automated.atom_utils.automated_test_utils import TestHelper as helper
from Automated.atom_utils.screenshot_utils import ScreenshotHelper
from Automated.atom_utils.hydra_editor_utils import helper_create_entity_with_mesh

COMPONENT_PROPERTIES = [
    'Controller',
    'Controller|Configuration',
    'Controller|Configuration|Color',
    'Controller|Configuration|Intensity Mode',
    'Controller|Configuration|Intensity',
    'Controller|Configuration|Angular Diameter',
    'Controller|Configuration|Shadow|Camera',
    'Controller|Configuration|Shadow|Shadow Far Clip',
    'Controller|Configuration|Shadow|Shadowmap Size',
    'Controller|Configuration|Shadow|Cascade Count',
    'Controller|Configuration|Shadow|Split Automatic',
    'Controller|Configuration|Shadow|Split Ratio',
    'Controller|Configuration|Shadow|Far Depth Cascade',
    'Controller|Configuration|Shadow|Ground Height',
    'Controller|Configuration|Shadow|Enable Cascade Correction?',
    'Controller|Configuration|Shadow|Enable Debug Coloring?',
    'Controller|Configuration|Shadow|Shadow Filter Method',
    'Controller|Configuration|Shadow|Softening Boundary Width',
    'Controller|Configuration|Shadow|Prediction Sample Count',
    'Controller|Configuration|Shadow|Filtering Sample Count'
]


def run():
    """
    Test Case - Directional Light:
    1. Opens the "EmptyLevel" level
    2. Finds the "Camera" entity in the default level setup and set its translation and rotation values.
    3. Creates a "Floor" entity with a Mesh component and "objects/plane.azmodel" mesh attached.
    4. Creates a "Bunny" entity with a Mesh component and "objects/bunny.azmodel" mesh attached.
    5. Sets the translation and scale for each entity so that the Bunny entity is standing on the Floor entity.
    6. Creates a "DirectionalLight" entity with a Directional Light component.
    7. Verifies all Directional Light component properties listed in COMPONENT_PROPERTIES constant are there.
    8. Points the new "DirectionalLight" entity at the bunny to give it lighting.
    9. After that it will make 7 different scene arrangements with the entities by modifying component properties:
        - For each of these arrangements, it will enter game mode and take a screenshot for comparison.
            1: Sets the Directional Light component's following properties before taking a screenshot:
             - Color: light green (0.5, 1.0, 0.5, 1.0).
             - Intensity: 1.
            2: Sets the Directional Light component's following properties before taking a screenshot:
                - Split Automatic: 3
                - Far Depth Cascade: False
                - Enable Debug Coloring: 2.0, 3.0, 4.0, 20.0
                - Enable Debug Coloring: True.
            3: Sets the Directional Light component's following properties before taking a screenshot:
                - Cascade Count: 4
                - Split Automatic: True
                - Split Ratio: 0.98
            4. Sets the Directional Light component's following properties before taking a screenshot:
                - Shadow Filter Method: 1 (PCF)
                - Softening Boundary Width: 0.07
                - Prediction Sample Count: 2
                - Filtering Sample Count: 4
            5. Sets the Directional Light component's following properties before taking a screenshot:
                - Prediction Sample Count: 16
                - Filtering Sample Count: 64
            6. Sets the Directional Light component's following properties before taking a screenshot:
                - Shadow Filter Method: 2 (ESM)
            7. Creates a second DirectionalLight entity with Directional Light component.
    10. Closes the Editor and the test ends.

    Tests will fail immediately if any of these log lines are found:
    1. Trace::Assert
    2. Trace::Error
    3. Traceback (most recent call last):

    :return: None
    """
    # This is used to create all of the screenshot file names.
    screenshot_filename_base = 'screenshot_atom_directionallight_'

    # Opens the EmptyLevel level, sets up camera, floor, bunny, & light entities with required components.
    base_entity = prepare_level_and_prepare_camera()
    prepare_for_floor_and_bunny(base_entity)
    light_component = prepare_for_directional_light_component(base_entity)

    # Iterates through 7 different component configurations taking a screenshot each time:
    screenshot_helper = ScreenshotHelper(general.idle_wait_frames)
    set_color_light_green(light_component, screenshot_helper, screenshot_filename_base)
    set_manual_cascade(light_component, screenshot_helper, screenshot_filename_base)
    set_automatic_cascade(light_component, screenshot_helper, screenshot_filename_base)
    set_pcf_low_sample_count(light_component, screenshot_helper, screenshot_filename_base)
    set_pcf_high_sample_count(light_component, screenshot_helper, screenshot_filename_base)
    set_esm(light_component, screenshot_helper, screenshot_filename_base)
    add_2nd_light(base_entity, screenshot_helper, screenshot_filename_base)

    # Closes the Editor once finished:
    helper.close_editor()


def rotation_rad(x, y, z):
    return azlmbr.math.Vector3(x / 180.0 * math.pi, y / 180.0 * math.pi, z / 180.0 * math.pi)


def almost_equal(float0, float1):
    return abs(float0 - float1) < abs(float0) / 1000000.0


def prepare_level_and_prepare_camera():
    # Open EmptyLevel level.
    helper.init_idle()
    helper.open_level("EmptyLevel")
    general.idle_wait_frames(1)
    
    # Get Default Atom Environment entity.
    base_entity = helper.find_entities('Default Atom Environment')[0]

    # Place camera to origin relative to Default Atom Environment.
    camera_entity = helper.find_entities('Camera')[0]
    components.TransformBus(bus.Event, 'SetLocalTranslation', camera_entity, azlmbr.math.Vector3(0.0, -3.0, 2.0))
    components.TransformBus(bus.Event, 'SetLocalRotation', camera_entity, rotation_rad(-10.0, 0.0, 0.0))

    return base_entity


def prepare_for_floor_and_bunny(base_entity):
    # Create an entity with a Mesh Component and set plane.azmodel which is used for shadow receiver.
    floor = helper_create_entity_with_mesh('objects/plane.azmodel', azlmbr.math.Vector3(), 'Floor')

    # Create an entity with a Mesh Component and set bunny.azmodel which is used for shadow caster.
    bunny = helper_create_entity_with_mesh('objects/bunny.azmodel', azlmbr.math.Vector3(), 'Bunny')
    components.TransformBus(bus.Event, 'SetLocalTranslation', bunny, azlmbr.math.Vector3(-1.0, 0.0, 1.0))

    # Move the plane to beneath the bunny and scale the plane to be a shadow catcher.
    components.TransformBus(bus.Event, 'SetLocalTranslation', floor, azlmbr.math.Vector3(0.0, 0.0, 0.8))
    components.TransformBus(bus.Event, "SetLocalUniformScale", floor, 20.0)


def prepare_for_directional_light_component(base_entity):
    # Create an entity with a Directional Light Component
    light = editor.ToolsApplicationRequestBus(bus.Broadcast, 'CreateNewEntity', base_entity)
    if light.IsValid():
        general.log('Entity for directional light is successfully created.')
    editor.EditorEntityAPIBus(bus.Event, 'SetName', light, 'DirectionalLight')
    light_component = helper.attach_component_to_entity(light, 'Directional Light')

    # Verify property list of component
    helper.compare_property_list(light_component, COMPONENT_PROPERTIES)

    # Set transform of directional light to lit bunny
    components.TransformBus(
        bus.Event, 'SetLocalRotation', light, azlmbr.math.Vector3(0.0, math.pi / 6, -math.pi * 2 / 3))
    # directional light component ignore the location of itself.

    return light_component


def set_color_light_green(light_component, screenshot_helper, screenshot_filename_base):
    # Set Color light green, Intensity 1.0, to the Light.
    color_path = 'Controller|Configuration|Color'
    intensity_path = 'Controller|Configuration|Intensity'
    color_value = azlmbr.math.Color(0.5, 1.0, 0.5, 1.0)
    intensity_value = 1.0
    helper.set_component_property(light_component, color_path, color_value)
    helper.set_component_property(light_component, intensity_path, intensity_value)
    general.log('Set light color and intensity.')
    screenshot_helper.capture_screenshot_blocking_in_game_mode(screenshot_filename_base + 'nofilter.ppm')

    # Verify component's color and intensity
    color_result = helper.get_component_property(light_component, color_path)
    if color_result.GetValue() == color_value:
        general.log('Color property of light is correctly set.')
    intensity_result = helper.get_component_property(light_component, intensity_path)
    if intensity_result.GetValue() == intensity_value:
        general.log('Intensity of light is correctly set.')


def set_manual_cascade(light_component, screenshot_helper, screenshot_filename_base):
    # Set Cascade Count 3, disable automatic cascade splitting, Far Depth Cascade, and enable Debug Coloring
    cascadeCount_path = 'Controller|Configuration|Shadow|Cascade Count'
    splitAutomatic_path = 'Controller|Configuration|Shadow|Split Automatic'
    farDepthCascade_path = 'Controller|Configuration|Shadow|Far Depth Cascade'
    enableDebugColoring_path = 'Controller|Configuration|Shadow|Enable Debug Coloring?'
    cascadeCount_value = 3
    splitAutomatic_value = False
    farDepthCascade_value = azlmbr.math.Vector4(2.0, 3.0, 4.0, 20.0)
    enableDebugColoring_value = True
    helper.set_component_property(light_component, cascadeCount_path, cascadeCount_value)
    helper.set_component_property(light_component, splitAutomatic_path, splitAutomatic_value)
    helper.set_component_property(light_component, farDepthCascade_path, farDepthCascade_value)
    helper.set_component_property(light_component, enableDebugColoring_path, enableDebugColoring_value)
    general.log('Set light cascade far depth manually and enabled debug coloring.')
    screenshot_helper.capture_screenshot_blocking_in_game_mode(screenshot_filename_base + 'manualcascade.ppm')

    # Verify component's cascade count, automatic flag of cascade splitting, far depth cascade, & flag of debug coloring
    cascadeCount_result = helper.get_component_property(light_component, cascadeCount_path)
    if cascadeCount_result.GetValue() == cascadeCount_value:
        general.log('Cascade Count of light is correctly set.')
    splitAutomatic_result = helper.get_component_property(light_component, splitAutomatic_path)
    if splitAutomatic_result.GetValue() == splitAutomatic_value:
        general.log('Split Automatic of light is correctly set.')
    farDepthCascade_result = helper.get_component_property(light_component, farDepthCascade_path)
    if farDepthCascade_result.GetValue() == farDepthCascade_value:
        general.log('Far Depth Cascade of light is correctly set.')
    enableDebugColoring_result = helper.get_component_property(light_component, enableDebugColoring_path)
    if enableDebugColoring_result.GetValue() == enableDebugColoring_value:
        general.log('Enable Debug Color of light is correctly set.')


def set_automatic_cascade(light_component, screenshot_helper, screenshot_filename_base):
    cascadeCount_path = 'Controller|Configuration|Shadow|Cascade Count'
    splitAutomatic_path = 'Controller|Configuration|Shadow|Split Automatic'
    # Set split ratio 0.98 and cascade count 4 and enable automatic cascade splitting
    splitRatio_path = 'Controller|Configuration|Shadow|Split Ratio'
    splitRatio_value = 0.98
    helper.set_component_property(light_component, splitRatio_path, splitRatio_value)
    helper.set_component_property(light_component, cascadeCount_path, 4)
    helper.set_component_property(light_component, splitAutomatic_path, True)
    general.log('Set split ratio.')
    screenshot_helper.capture_screenshot_blocking_in_game_mode(screenshot_filename_base + 'autocascade.ppm')

    # Verify component's split ratio.
    splitRatio_result = helper.get_component_property(light_component, splitRatio_path)
    if almost_equal(splitRatio_result.GetValue(), splitRatio_value):
        general.log('Split Ratio of light is correctly set.')


def set_pcf_low_sample_count(light_component, screenshot_helper, screenshot_filename_base):
    enableDebugColoring_path = 'Controller|Configuration|Shadow|Enable Debug Coloring?'
    # Disable debug coloring and Set Filter method PCF with boundary width 0.07 and low sample count.
    filterMethod_path = 'Controller|Configuration|Shadow|Shadow Filter Method'
    boundaryWidth_path = 'Controller|Configuration|Shadow|Softening Boundary Width'
    predictionCount_path = 'Controller|Configuration|Shadow|Prediction Sample Count'
    filteringCount_path = 'Controller|Configuration|Shadow|Filtering Sample Count'
    filterMethod_value = 1  # PCF
    boundaryWidth_value = 0.07
    predictionCount_value = 2
    filteringCount_value = 4
    helper.set_component_property(light_component, enableDebugColoring_path, False)
    helper.set_component_property(light_component, filterMethod_path, filterMethod_value)
    helper.set_component_property(light_component, boundaryWidth_path, boundaryWidth_value)
    helper.set_component_property(light_component, predictionCount_path, predictionCount_value)
    helper.set_component_property(light_component, filteringCount_path, filteringCount_value)
    general.log('Set PCF filtering with low sample count.')
    screenshot_helper.capture_screenshot_blocking_in_game_mode(screenshot_filename_base + 'pcflow.ppm')

    # Verify component's PCF parameters.
    filterMethod_result = helper.get_component_property(light_component, filterMethod_path)
    if filterMethod_result.GetValue() == filterMethod_value:
        general.log('Filter Method of light is correctly set.')
    boundaryWidth_result = helper.get_component_property(light_component, boundaryWidth_path)
    if almost_equal(boundaryWidth_result.GetValue(), boundaryWidth_value):
        general.log('Boundary Width of light is correctly set.')
    predictionCount_result = helper.get_component_property(light_component, predictionCount_path)
    if predictionCount_result.GetValue() == predictionCount_value:
        general.log('Prediction Sample Count of light is correctly set.')
    filteringCount_result = helper.get_component_property(light_component, filteringCount_path)
    if filteringCount_result.GetValue() == filteringCount_value:
        general.log('Filtering Sample Count of light is correctly set.')


def set_pcf_high_sample_count(light_component, screenshot_helper, screenshot_filename_base):
    predictionCount_path = 'Controller|Configuration|Shadow|Prediction Sample Count'
    filteringCount_path = 'Controller|Configuration|Shadow|Filtering Sample Count'
    # Set PCF filtering with high sample count.
    helper.set_component_property(light_component, predictionCount_path, 16)
    helper.set_component_property(light_component, filteringCount_path, 64)
    screenshot_helper.capture_screenshot_blocking_in_game_mode(screenshot_filename_base + 'pcfhigh.ppm')


def set_esm(light_component, screenshot_helper, screenshot_filename_base):
    filterMethod_path = 'Controller|Configuration|Shadow|Shadow Filter Method'
    # Set ESM filtering.
    helper.set_component_property(light_component, filterMethod_path, 2) # ESM
    screenshot_helper.capture_screenshot_blocking_in_game_mode(screenshot_filename_base + 'esm.ppm')


def add_2nd_light(base_entity, screenshot_helper, screenshot_filename_base):
    # Add second directional light and confirm non-crashing.
    light2nd = editor.ToolsApplicationRequestBus(bus.Broadcast, 'CreateNewEntity', base_entity)
    if light2nd.IsValid():
        general.log('Entity for second directional light is successfully created.')
    editor.EditorEntityAPIBus(bus.Event, 'SetName', light2nd, 'DirectionalLight 2')
    helper.attach_component_to_entity(light2nd, 'Directional Light')
    components.TransformBus(bus.Event, 'SetLocalRotation', light2nd, rotation_rad(-90.0, 0.0, 0.0))
    screenshot_helper.capture_screenshot_blocking_in_game_mode(screenshot_filename_base + '2ndlight.ppm')


if __name__ == "__main__":
    run()
