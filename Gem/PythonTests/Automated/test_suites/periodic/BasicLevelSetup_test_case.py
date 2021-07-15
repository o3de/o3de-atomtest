"""
Copyright (c) Contributors to the Open 3D Engine Project.
For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT

Hydra script that is used to create a new level with a default rendering setup.
After the level is setup, screenshots are diffed against golden images are used to verify pass/fail results of the test.

See the run() function for more in-depth test info.
"""

import os
import sys

import azlmbr.paths
import azlmbr.legacy.general as general

sys.path.append(os.path.join(azlmbr.paths.devassets, "Gem", "PythonTests"))

import Automated.atom_utils.hydra_editor_utils as hydra
from Automated.atom_utils.automated_test_utils import TestHelper as helper
from Automated.atom_utils.screenshot_utils import ScreenshotHelper

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
DEGREE_RADIAN_FACTOR = 0.0174533


def run():
    """
    1. View -> Layouts -> Restore Default Layout, sets the viewport to ratio 16:9 @ 1280 x 720
    2. Runs console command r_DisplayInfo = 0
    3. Deletes all entities currently present in the level.
    4. Creates a "default_level" entity to hold all other entities, setting the translate values to x:0, y:0, z:0
    5. Adds a Grid component to the "default_level" & updates its Grid Spacing to 1.0m
    6. Adds a "global_skylight" entity to "default_level", attaching an HDRi Skybox w/ a Cubemap Texture.
    7. Adds a Global Skylight (IBL) component w/ diffuse image and specular image to "global_skylight" entity.
    8. Adds a "ground_plane" entity to "default_level", attaching a Mesh component & Material component.
    9. Adds a "directional_light" entity to "default_level" & adds a Directional Light component.
    10. Adds a "sphere" entity to "default_level" & adds a Mesh component with a Material component to it.
    11. Adds a "camera" entity to "default_level" & adds a Camera component with 80 degree FOV and Transform values:
        Translate - x:5.5m, y:-12.0m, z:9.0m
        Rotate - x:-27.0, y:-12.0, z:25.0
    12. Finally enters game mode, takes a screenshot, exits game mode, & saves the level.
    :return: None
    """
    # Save level, enter game mode, take screenshot, & exit game mode.
    hydra.create_basic_atom_level("EmptyLevel")
    general.save_level()
    general.idle_wait(0.5)
    general.enter_game_mode()
    general.idle_wait(1.0)
    helper.wait_for_condition(function=lambda: general.is_in_game_mode(), timeout_in_seconds=2.0)
    ScreenshotHelper(general.idle_wait_frames).capture_screenshot_blocking(f"{'AtomBasicLevelSetup'}.ppm")
    general.exit_game_mode()
    helper.wait_for_condition(function=lambda: not general.is_in_game_mode(), timeout_in_seconds=2.0)
    general.log("Basic level created")


if __name__ == "__main__":
    run()
