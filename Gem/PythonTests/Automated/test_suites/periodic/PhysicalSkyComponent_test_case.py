"""
Copyright (c) Contributors to the Open 3D Engine Project

SPDX-License-Identifier: Apache-2.0 OR MIT

Hydra script that is used to test the Physical Sky component functionality inside the Editor.
Opens the MeshTest level and creates a "Skybox" entity and attaches a Physical Sky component.
It then modifies the Intensity Mode, Sky Intensity, Sun Intensity, Turbidity, and Sun Radius Factor propertie.s
A screenshot is taken once all options are set on the Physical Sky component.
Results are verified using log messages & screenshot comparisons diffed against golden images.

See the run() function for more in-depth test info.
"""

import os
import sys
import math

import azlmbr.editor
import azlmbr.legacy.general as general
import azlmbr.paths
from azlmbr.entity import EntityId

sys.path.append(os.path.join(azlmbr.paths.devroot, "AtomTest", "Gem", "PythonTests"))

from Automated.atom_utils.automated_test_utils import TestHelper as helper
from Automated.atom_utils.screenshot_utils import ScreenshotHelper

COMPONENT_PROPERTIES = [
    'Controller',
    'Controller|Configuration',
    'Controller|Configuration|Intensity Mode',
    'Controller|Configuration|Sky Intensity',
    'Controller|Configuration|Sun Intensity',
    'Controller|Configuration|Turbidity',
    'Controller|Configuration|Sun Radius Factor'
]


def run():
    """
    Test Case - Physical Sky:
    1. Opens the "EmptyLevel" level and creates a new "Skybox" entity with Physical Sky component attached.
    2. Sets the Sky Intensity property to 3 (EV100).
    3. Sets the Sun Intensity property to 4.
    4. Sets the Turbidity property to 2.
    5. Sets the Sun Radius Factor to 2.
    6. Verifies all of the above properties were set correctly on the Physical Sky component.
    7. Sets the transform value of the Physical Sky to azlmbr.math.Vector3(math.pi/8.0, 0.0, math.pi)
    8. Enters game mode and takes a screenshot for comparison.
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

    # Create "Skybox" entity and attach Physical Sky component to it, verify properties are valid for component.
    myEntityId = azlmbr.editor.ToolsApplicationRequestBus(azlmbr.bus.Broadcast, 'CreateNewEntity', EntityId())
    azlmbr.editor.EditorEntityAPIBus(azlmbr.bus.Event, 'SetName', myEntityId, "Skybox")
    if myEntityId.IsValid():
        general.log("Entity successfully created.")
    component = helper.attach_component_to_entity(myEntityId, 'Physical Sky')
    helper.compare_property_list(component, COMPONENT_PROPERTIES)

    # Set component properties for Intensity Mode, Sun Intensity,
    skyIntensityPath = COMPONENT_PROPERTIES[3]
    sunIntensityPath = COMPONENT_PROPERTIES[4]
    turbidityPath = COMPONENT_PROPERTIES[5]
    sunRadiusPath = COMPONENT_PROPERTIES[6]

    skyIntensityValue = 3  # in EV100
    sunIntensityValue = 4  # in EV100
    turbidityValue = 2
    sunRadiusValue = 2

    azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'SetComponentProperty', component, skyIntensityPath, skyIntensityValue)
    azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'SetComponentProperty', component, sunIntensityPath, sunIntensityValue)
    azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'SetComponentProperty', component, turbidityPath, turbidityValue)
    azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'SetComponentProperty', component, sunRadiusPath, sunRadiusValue)

    # verify that physical sky component contains the expected values
    componentProperty = azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'GetComponentProperty', component, skyIntensityPath)
    if componentProperty.GetValue() == skyIntensityValue:
        general.log("Sky Intensity is correctly set")
    componentProperty = azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'GetComponentProperty', component, sunIntensityPath)
    if componentProperty.GetValue() == sunIntensityValue:
        general.log("Sun Intensity is correctly set")
    componentProperty = azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'GetComponentProperty', component, turbidityPath)
    if componentProperty.GetValue() == turbidityValue:
        general.log("Turbidity is correctly set")
    componentProperty = azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'GetComponentProperty', component, sunRadiusPath)
    if componentProperty.GetValue() == sunRadiusValue:
        general.log("Sun Radius is correctly set")

    # Set transform of physical sky
    eulerAngle = azlmbr.math.Vector3(math.pi/8.0, 0.0, math.pi)
    azlmbr.components.TransformBus(azlmbr.bus.Event, 'SetLocalRotation', myEntityId, eulerAngle)

    # generate screenshot and compare with golden
    ScreenshotHelper(general.idle_wait_frames).capture_screenshot_blocking_in_game_mode(
        'screenshot_atom_PhysicalSkyComponent.ppm')
    helper.close_editor()


if __name__ == "__main__":
    run()
