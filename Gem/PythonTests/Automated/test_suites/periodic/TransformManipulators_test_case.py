"""
Copyright (c) Contributors to the Open 3D Engine Project.
For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT

Hydra script that is used to test the various transform options on entities.
Opens the EmptyLevel level & creates a new entity with a Mesh component.
Manipulates the camera 6 times to create 6 screenshots of the new entity.
Results are verified using log messages & screenshot comparisons diffed against golden images.

See the run() function for more in-depth test info.
"""


import os
import sys

import azlmbr.editor
import azlmbr.legacy.general as general
import azlmbr.paths

sys.path.append(os.path.join(azlmbr.paths.devassets, "Gem", "PythonTests"))

from Automated.atom_utils.automated_test_utils import TestHelper as helper
from Automated.atom_utils.screenshot_utils import ScreenshotHelper
from Automated.atom_utils.hydra_editor_utils import helper_create_entity_with_mesh


def run():
    """
    Test Case - Transform Manipulators:
    1. Opens the "EmptyLevel" level and creates a new entity with a Mesh component using "objects/sphere.azmodel" mesh.
    2. Selects the camera and manipulates its transform position, then enters game mode and takes a screenshot.
    3. Repeats step 2 a total of 6 times for 6 screenshots for comparison against golden images.
    4. Closes the Editor and ends the test.

    Tests will fail immediately if any of these log lines are found:
    1. Trace::Assert
    2. Trace::Error
    3. Traceback (most recent call last):

    :return: None
    """
    # Open EmptyLevel level.
    helper.init_idle()
    helper.open_level("EmptyLevel")

    screenshotHelper = ScreenshotHelper(general.idle_wait_frames)

    # Create new entity with Mesh component and objects/sphere.azmodel mesh.
    entityId = helper_create_entity_with_mesh('objects/sphere.azmodel')
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetWorldTranslation", entityId,
                                   azlmbr.math.Vector3(0.0, 0.0, 0.0))

    # Find camera for taking screenshots.
    cameraEntityId = helper.find_entities('Camera')[0]
    azlmbr.editor.EditorCameraRequestBus(
        azlmbr.bus.Broadcast, "SetViewAndMovementLockFromEntityPerspective", cameraEntityId, False)

    # Below are the three different camera setups for 6 different screenshots.
    set_manipulator_transform_mode(azlmbr.editor.TransformMode_Translation)
    set_camera_close(cameraEntityId)
    general.idle_wait_frames(5)
    screenshotHelper.capture_screenshot_blocking('manipulator_translation_close.ppm')
    set_camera_far(cameraEntityId)
    general.idle_wait_frames(1)
    screenshotHelper.capture_screenshot_blocking('manipulator_translation_far.ppm')

    set_manipulator_transform_mode(azlmbr.editor.TransformMode_Rotation)
    set_camera_close(cameraEntityId)
    general.idle_wait_frames(1)
    screenshotHelper.capture_screenshot_blocking('manipulator_rotation_close.ppm')
    set_camera_far(cameraEntityId)
    general.idle_wait_frames(1)
    screenshotHelper.capture_screenshot_blocking('manipulator_rotation_far.ppm')

    set_manipulator_transform_mode(azlmbr.editor.TransformMode_Scale)
    set_camera_close(cameraEntityId)
    general.idle_wait_frames(1)
    screenshotHelper.capture_screenshot_blocking('manipulator_scale_close.ppm')
    set_camera_far(cameraEntityId)
    general.idle_wait_frames(1)
    screenshotHelper.capture_screenshot_blocking('manipulator_scale_far.ppm')
    general.log('All screenshots finished.')

    helper.close_editor()


def set_manipulator_transform_mode(mode):
    azlmbr.editor.EditorTransformComponentSelectionRequestBus(azlmbr.bus.Broadcast, "SetTransformMode", mode)


def set_camera_close(cameraEntityId):
    cameraTransform = azlmbr.math.Transform_CreateRotationZ(azlmbr.math.Math_DegToRad(118.0))
    cameraTransform.SetTranslation(azlmbr.math.Vector3(1.5, 1.0, 0.5))
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetWorldTM", cameraEntityId, cameraTransform)


def set_camera_far(cameraEntityId):
    cameraTransform = azlmbr.math.Transform_CreateRotationZ(azlmbr.math.Math_DegToRad(118.0))
    cameraTransform.SetTranslation(azlmbr.math.Vector3(6.0, 4.0, 0.5))
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetWorldTM", cameraEntityId, cameraTransform)


if __name__ == "__main__":
    run()
