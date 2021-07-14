"""
Copyright (c) Contributors to the Open 3D Engine Project. For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT

Hydra script that is used to test the Exposure Control component functionality inside the Editor.
Opens the MeshTest level & creates a "Exposure Control" entity containing the PostFX Layer & Exposure Control components
It then selects the "Manual" control type on the Control Type property and takes a screenshot for comparison.
Finally it selects the "Eye Adaptation" control type on the Control Type property and takes a screenshot for comparison.
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

EXPOSURE_COMPONENT_PROPERTIES = [
    'Controller|Configuration|Overrides|EyeAdaptationSpeedDown Override', 
    'Controller|Configuration|Eye Adaptation|Speed Up', 
    'Controller|Configuration|Eye Adaptation|Enable Heatmap', 
    'Controller|Configuration|Overrides|ManualCompensation Override', 
    'Controller|Configuration|Eye Adaptation|Minimum Exposure', 
    'Controller|Configuration|Overrides|EyeAdaptationSpeedUp Override', 
    'Controller|Configuration|Eye Adaptation|Speed Down', 
    'Controller|Configuration|Manual Compensation', 
    'Controller|Configuration|Overrides|EyeAdaptationExposureMin Override', 
    'Controller|Configuration|Eye Adaptation|Maximum Exposure', 
    'Controller|Configuration|Overrides|HeatmapEnabled Override', 
    'Controller|Configuration|Control Type', 
    'Controller|Configuration|Enable', 
    'Controller', 
    'Controller|Configuration', 
    'Controller|Configuration|Overrides|Enabled Override', 
    'Controller|Configuration|Overrides|ExposureControlType Override', 
    'Controller|Configuration|Overrides|EyeAdaptationExposureMax Override'
]

ExposureControlTypes = {"Manual": 0, "Eye Adaptation": 1}


def run():
    """
    Test Case - Exposure Control:
    1. Opens the "MeshTest" level and creates a new "Exposure Control" entity.
    2. Attaches a PostFX Layer component & Exposure Control component to the new entity.
    3. Modifies the Enable property to True for the Exposure Control component.
    4. Modifies the Control Type to Manual and verifies the properties are set correctly.
    5. Enter game mode and take a screenshot for comparison.
    6. Updates the Control Type from Manual to Eye Adaptation.
    7. Enters game mode and takes a screenshot for comparison.
    8. Closes the Editor and ends the test.

    Tests will fail immediately if any of these log lines are found:
    1. Trace::Assert
    2. Trace::Error
    3. Traceback (most recent call last):

    :return: None
    """
    # Open MeshTest level.
    helper.init_idle()
    helper.open_level("MeshTest")

    # Create new entity and attaches an Exposure Control component.
    myEntityId = azlmbr.editor.ToolsApplicationRequestBus(azlmbr.bus.Broadcast, 'CreateNewEntity', EntityId())
    azlmbr.editor.EditorEntityAPIBus(azlmbr.bus.Event, 'SetName', myEntityId, "Exposure control")
    if myEntityId.IsValid():
        general.log("Entity successfully created.")

    # Attach a PostFX Layer component.
    helper.attach_component_to_entity(myEntityId, 'PostFX Layer')

    # Attach an Exposure Control component and verifies all expected properties are present.
    exposure_component = helper.attach_component_to_entity(myEntityId, 'Exposure Control')
    helper.compare_property_list(exposure_component, EXPOSURE_COMPONENT_PROPERTIES)

    # Set the Enable property to True and set the Control Type property to Manual for the Exposure Control component.
    exposureEnabled = 'Controller|Configuration|Enable'
    exposureControlType = 'Controller|Configuration|Control Type'
    helper.set_component_property(exposure_component, exposureEnabled, True)
    helper.set_component_property(exposure_component, exposureControlType, ExposureControlTypes["Manual"])

    # Verify the properties set on the Exposure Control are accurate to what was set.
    enabledProperty = helper.get_component_property(exposure_component, exposureEnabled)
    if enabledProperty.GetValue() == True:
        general.log("Exposure enabled correctly set")
    exposureType = helper.get_component_property(exposure_component, exposureControlType)
    if exposureType.GetValue() == ExposureControlTypes["Manual"]:
        general.log("Manual exposure type enabled correctly set")

    # Capture sceenshot
    screenshot_helper = ScreenshotHelper(general.idle_wait_frames)
    screenshot_helper.capture_screenshot_blocking_in_game_mode('screenshot_atom_ExposureComponent_Manual.ppm')

    # Set the Control Type property to Eye Adaptation for the Exposure Control component.
    azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast,
        'SetComponentProperty',
        exposure_component,
        exposureControlType,
        ExposureControlTypes["Eye Adaptation"])
    
    # Verify the Eye Adaptation option Control Type property was set correctly.
    exposureType = helper.get_component_property(exposure_component, exposureControlType)
    if exposureType.GetValue() == ExposureControlTypes["Eye Adaptation"]:
        general.log("Eye adaptation exposure type enabled correctly set")
        
    # Wait for a while for the eye adaptation to settle
    general.idle_wait_frames(300)

    # Capture screenshot
    screenshot_helper.capture_screenshot_blocking_in_game_mode('screenshot_atom_ExposureComponent_EyeAdaptation.ppm')
    helper.close_editor()


if __name__ == "__main__":
    run()
