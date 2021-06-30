"""
Copyright (c) Contributors to the Open 3D Engine Project. For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT

Hydra script that is used to test FBX mesh group import scaling.
Creates a new level and uses a list of .azmodel meshes to test creating new entities with these group meshes.
It then modifies the x, y, z scaling values for each mesh that was attached to the entity.
Results are verified using log messages & screenshot comparisons diffed against golden images.

See the run() function for more in-depth test info.
"""

import os
import sys

import azlmbr.legacy.general as general
import azlmbr.math as math
import azlmbr.editor

sys.path.append(os.path.join(azlmbr.paths.devroot, "AtomTest", "Gem", "PythonTests"))

from Automated.atom_utils.automated_test_utils import TestHelper as helper
from Automated.atom_utils.hydra_editor_utils import helper_create_entity_with_mesh
from Automated.atom_utils.screenshot_utils import ScreenshotHelper


def run():
    """
    Test Case - Fbx mesh group Import scaling in Atom:
    1. Creates a new level called MeshScalingTemporaryLevel
    2. Has a list of 12 meshes, which it will do the following for each one:
        - Create an entity and attach the mesh to it.
        - Sets it with an initial offset of x:-15, y:0, z:0
        - For each additional mesh the x offset is modified by +3.0
    3. Enters game mode to take a screenshot for comparison, then exits game mode.
    4. Prints general.log("FBX mesh group scaling test has completed.")
    5. Exit the Editor and ends the test.

    Tests will fail immediately if any of these log lines are found:
    1. Trace::Assert
    2. Trace::Error
    3. Traceback (most recent call last):

    :return: None
    """

    def after_level_load():
        """Function to call after creating/opening a level to ensure it loads."""
        # Give everything a second to initialize.
        general.idle_enable(True)
        general.update_viewport()
        general.idle_wait(0.5)  # half a second is more than enough for updating the viewport.

        # Close out problematic windows, FPS meters, and anti-aliasing.
        if general.is_helpers_shown():  # Turn off the helper gizmos if visible
            general.toggle_helpers()
        if general.is_pane_visible("Error Report"):  # Close Error Report windows that block focus.
            general.close_pane("Error Report")
        if general.is_pane_visible("Error Log"):  # Close Error Log windows that block focus.
            general.close_pane("Error Log")
        general.run_console("r_displayInfo=0")
        general.run_console("r_antialiasingmode=0")

        return True

    # Create a new test level
    test_level_name = 'MeshGroupingTemporaryLevel'
    heightmap_resolution = 128
    heightmap_meters_per_pixel = 1
    terrain_texture_resolution = 128
    use_terrain = False

    # Return codes are ECreateLevelResult defined in CryEdit.h
    return_code = general.create_level_no_prompt(
        test_level_name, heightmap_resolution, heightmap_meters_per_pixel, terrain_texture_resolution, use_terrain)
    if return_code == 1:
        general.log(f"{test_level_name} level already exists")
    elif return_code == 2:
        general.log("Failed to create directory")
    elif return_code == 3:
        general.log("Directory length is too long")
    elif return_code != 0:
        general.log("Unknown error, failed to create level")
    else:
        general.log(f"{test_level_name} level created successfully")
    after_level_load()

    helper.init_idle()
    helper.open_level(test_level_name)
    general.idle_wait_frames(1)

    # These are the meshes that are used to test FBX mesh import scaling.
    meshes = [
        "cube_group.azmodel",
        "cube_parent.azmodel",
        "cube_parent_plus_locator.azmodel",
        "cube_parent_plus_locator_rotatez_90.azmodel",
        "cube_parent__rotatez_90_locator.azmodel",
        "cube_parent__scaley_2_locator.azmodel",
        "cube_parent__transx_100_locator.azmodel"
    ]

    # Initial offset values to iterate off of for mesh scaling of meshes.
    offset = math.Vector3()
    offset.x = -15.0
    offset.y = 0.0
    offset.z = 0.0

    # For each mesh, create an entity and attach the mesh to it, then scale it using the values in offset.
    meshIndex = 0
    for mesh in meshes:
        meshIndex = meshIndex + 1
        offset.x += 3.0
        entityName = "TestEntity{}".format(meshIndex)
        helper_create_entity_with_mesh("dag_hierarchy/" + mesh, offset, entityName)

    helper.enter_game_mode(["", ""])
    # Example: how to capture a screenshot
    general.set_viewport_size(1280, 720)
    general.set_cvar_integer('r_DisplayInfo', 0)
    general.idle_wait_frames(1)

    ScreenshotHelper(general.idle_wait_frames).capture_screenshot_blocking(
        "screenshot_atom_FBXMeshGroupImportScaling.dds")
    helper.exit_game_mode(["", ""])
    general.log("FBX mesh group scaling test has completed.")
    helper.close_editor()


if __name__ == "__main__":
    run()
