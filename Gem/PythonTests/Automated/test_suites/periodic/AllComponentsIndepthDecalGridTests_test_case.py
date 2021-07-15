"""
Copyright (c) Contributors to the Open 3D Engine Project.
For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT

Hydra script to verify basic Atom rendering components after setting up and saving the scene in EmptyLevel.
Loads updated EmptyLevel, manipulates entities with Grid & Decal components and takes screenshots.
Screenshots are diffed against golden images to verify pass/fail results of the test.

See the run() function for more in-depth test info.
"""

import os
import sys

import azlmbr.math as math
import azlmbr.paths
import azlmbr.legacy.general as general

sys.path.append(os.path.join(azlmbr.paths.devassets, "Gem", "PythonTests"))

from Automated.atom_utils import hydra_editor_utils as hydra
from Automated.atom_utils.automated_test_utils import TestHelper as helper

BASIC_LEVEL_NAME = "EmptyLevel"
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720


def run():
    """
    Sets up the tests by making sure the required level is created & setup correctly.
    It then executes 2 test cases:

    Test Case - Grid:
    1. Selects the "default_level" entity.
    2. Select Grid component inside default_entity.
    3. Change the Grid Size value to 64.
    4. Enters game mode to take a screenshot for comparison, then exits game mode.
    5. Change the Axis Color to: 13,255,0
    6. Enters game mode to take a screenshot for comparison, then exits game mode.
    7. Change the Primary Grid Spacing value to: 0.5
    8. Enters game mode to take a screenshot for comparison, then exits game mode.
    9. Change the Primary Color to: 129,96,0
    10. Enters game mode to take a screenshot for comparison, then exits game mode.
    11. Change the Secondary Grid Spacing value to: 0.75
    12. Enters game mode to take a screenshot for comparison, then exits game mode.
    13. Change the Secondary Color to: 0,35,161
    14. Enters game mode to take a screenshot for comparison, then exits game mode.
    15. Change the values back to original values like below
        Grid Size value to 32.
        Axis Color to: 0,0,255.
        Primary Grid Spacing value to: 1.0.
        Primary Color to: 64,64,64.
        Secondary Grid Spacing value to: 1.0.
        Secondary Color to: 128,128,128.

    Test Case - Decal:
    1. Create child entity "decal_1" at position (3.0, 0.0, 1.0) under "default_level" entity.
    2. Find the Material property and set it to "airship_symbol_decal.material"
    3. Enters game mode to take a screenshot for comparison, then exits game mode.
    4. Change the Scale value in Transform component to 3.
    5. Enters game mode to take a screenshot for comparison, then exits game mode.
    6. Set the Attenuation Angle in decal component to: 0.75.
    7. Enters game mode to take a screenshot for comparison, then exits game mode.
    8. Set Opacity to: 0.03.
    9. Enters game mode to take a screenshot for comparison, then exits game mode.
    10. Set Opacity back to 1.
    11. Create child entity "decal_2" at position (5.0, 0.0, 0.5) under "default_level" entity.
    12. Set the material value to "valenaactor_helmetmat.material" and Sort Key value to: 0.
    13. Enters game mode to take a screenshot for comparison, then exits game mode.
    14. Set the Sort Key value to: 50.
    15. Enters game mode to take a screenshot for comparison, then exits game mode.

    Finally prints the string "Component tests completed" after completion

    Tests will fail immediately if any of these log lines are found:
    1. Trace::Assert
    2. Trace::Error
    3. Traceback (most recent call last):

    :return: None
    """
    # NOTE: This step is to ensure we have the expected setup while running the test for each component
    helper.init_idle()
    hydra.create_basic_atom_level(level_name=BASIC_LEVEL_NAME)
    hydra.level_load_save(
        level_name=BASIC_LEVEL_NAME,
        entities_to_search=["default_level", "global_skylight", "ground_plane", "directional_light", "sphere", "camera"]
    )
    hydra.initial_viewport_setup(screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)

    # Run tests.
    decal_component_test()
    grid_component_test()
    general.log("Component tests completed")


def grid_component_test():
    """
    Basic test for the Grid component attached to an entity.
    """
    # Delete entities not required by the test or screenshot comparison will fail.
    entities_to_delete = ["ground_plane", "directional_light", "sphere"]
    for entity_name in entities_to_delete:
        entity_id = hydra.find_entity_by_name(entity_name)
        hydra.delete_entity(entity_id)

    # Get the default_level entity and Grid component object attached to it.
    grid_component_name = "Grid"
    default_level = "default_level"
    search_filter = azlmbr.entity.SearchFilter()
    search_filter.names = [default_level]
    default_level_id = azlmbr.entity.SearchBus(azlmbr.bus.Broadcast, 'SearchEntities', search_filter)[0]
    type_id_list = azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'FindComponentTypeIdsByEntityType', [grid_component_name], 0)
    outcome = azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'GetComponentOfType', default_level_id, type_id_list[0])
    grid_component = outcome.GetValue()

    # Bind the default_level entity and Grid component to a new hydra Entity class object for the test.
    grid_entity_id = hydra.find_entity_by_name(default_level)
    grid_entity_name = "grid_entity"
    grid_entity = hydra.Entity(grid_entity_name, grid_entity_id)
    grid_entity.components = [grid_component]

    # Update grid size of the Grid component of default_level and take screenshot
    hydra.get_set_test(grid_entity, 0, "Controller|Configuration|Grid Size", 64.0)
    general.idle_wait(1.0)
    hydra.take_screenshot_game_mode("Grid_1", grid_entity_name)

    # Update axis color of the Grid component of default_level and take screenshot
    color = math.Color(13.0 / 255.0, 255.0 / 255.0, 0.0 / 255.0, 255.0 / 255.0)
    hydra.get_set_test(grid_entity, 0, "Controller|Configuration|Axis Color", color)
    general.idle_wait(1.0)
    hydra.take_screenshot_game_mode("Grid_2", grid_entity_name)

    # Update Primary Grid Spacing of the Grid component of default_level and take screenshot
    hydra.get_set_test(grid_entity, 0, "Controller|Configuration|Primary Grid Spacing", 0.5)
    general.idle_wait(1.0)
    hydra.take_screenshot_game_mode("Grid_3", grid_entity_name)

    # Update Primary color of the Grid component of default_level and take screenshot
    color = math.Color(129.0 / 255.0, 96.0 / 255.0, 0.0 / 255.0, 255.0 / 255.0)
    hydra.get_set_test(grid_entity, 0, "Controller|Configuration|Primary Color", color)
    general.idle_wait(1.0)
    hydra.take_screenshot_game_mode("Grid_4", grid_entity_name)

    # Update Secondary Grid Spacing of the Grid component of default_level and take screenshot
    hydra.get_set_test(grid_entity, 0, "Controller|Configuration|Secondary Grid Spacing", 0.75)
    general.idle_wait(1.0)
    hydra.take_screenshot_game_mode("Grid_5", grid_entity_name)

    # Update Secondary color of the Grid component of default_level and take screenshot
    hydra.get_set_test(grid_entity, 0, "Controller|Configuration|Secondary Color", color)
    general.idle_wait(1.0)
    hydra.take_screenshot_game_mode("Grid_6", grid_entity_name)

    # Restore default grid values
    helper.set_component_property(grid_component, "Controller|Configuration|Grid Size", 32.0)
    color = math.Color(0.0 / 255.0, 0.0 / 255.0, 255.0 / 255.0, 255.0 / 255.0)
    helper.set_component_property(grid_component, "Controller|Configuration|Axis Color", color)
    helper.set_component_property(grid_component, "Controller|Configuration|Primary Grid Spacing", 1.0)
    color = math.Color(64.0 / 255.0, 64.0 / 255.0, 64.0 / 255.0, 255.0 / 255.0)
    helper.set_component_property(grid_component, "Controller|Configuration|Primary Color", color)
    helper.set_component_property(grid_component, "Controller|Configuration|Secondary Grid Spacing", 1.0)
    color = math.Color(128.0 / 255.0, 128.0 / 255.0, 128.0 / 255.0, 255.0 / 255.0)
    helper.set_component_property(grid_component, "Controller|Configuration|Secondary Color", color)


def decal_component_test():
    """
    Basic test for the Decal(Atom) component attached to an entity.
    """
    # Create child entity 'decal_1' under Default entity and add decal component to it
    component_name = "Decal (Atom)"
    search_filter = azlmbr.entity.SearchFilter()
    search_filter.names = ['default_level']
    default_level_id = azlmbr.entity.SearchBus(azlmbr.bus.Broadcast, 'SearchEntities', search_filter)[0]
    decal_1_entity_name = "decal_1"
    decal_1 = hydra.Entity(decal_1_entity_name)
    decal_1.create_entity(math.Vector3(3.0, 0.0, 1.0), components=[component_name], parent_id=default_level_id)
    # Set the Material Property in decal component to "airship_symbol_decal.material" and take screenshot
    asset_value = hydra.get_asset_by_path(
        os.path.join("Materials", "decal", "airship_symbol_decal.azmaterial")
    )
    hydra.get_set_test(decal_1, 0, "Controller|Configuration|Material", asset_value)
    general.idle_wait(1.0)
    hydra.take_screenshot_game_mode("Decal_1", decal_1_entity_name)

    # Change the Uniform scale value in Transform component to: 3.0 and take screenshot
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetLocalUniformScale", decal_1.id, 3.0)
    general.idle_wait(1.0)
    hydra.take_screenshot_game_mode("Decal_2", decal_1_entity_name)

    # Set the Attenuation Angle to: 0.75 in Decal component and take screenshot
    hydra.get_set_test(decal_1, 0, "Controller|Configuration|Attenuation Angle", 0.75)
    general.idle_wait(1.0)
    hydra.take_screenshot_game_mode("Decal_3", decal_1_entity_name)

    # Set the Set Opacity to: 0.03 in Decal component and take screenshot
    hydra.get_set_test(decal_1, 0, "Controller|Configuration|Opacity", 0.03)
    general.idle_wait(1.0)
    hydra.take_screenshot_game_mode("Decal_4", decal_1_entity_name)

    # Set Opacity back to 1.0
    hydra.get_set_test(decal_1, 0, "Controller|Configuration|Opacity", 1.0)

    # Create another child entity 'decal_2' under Default entity and add decal component to it
    decal_2_entity_name = "decal_2"
    decal_2 = hydra.Entity(decal_2_entity_name)
    decal_2.create_entity(math.Vector3(5.0, 0.0, 0.5), components=[component_name], parent_id=default_level_id)

    # Set the material value to "valenaactor_helmetmat.material", Sort Key value to: 0 and take screenshot
    asset_value = hydra.get_asset_by_path(
        os.path.join("Valena", "valenaactor_helmetmat.azmaterial")
    )
    hydra.get_set_test(decal_2, 0, "Controller|Configuration|Material", asset_value)
    hydra.get_set_test(decal_2, 0, "Controller|Configuration|Sort Key", 0.0)
    general.idle_wait(1.0)
    hydra.take_screenshot_game_mode("Decal_5", decal_2_entity_name)
    # Set the Sort Key value of decal_2 to: 50 and take screenshot
    hydra.get_set_test(decal_2, 0, "Controller|Configuration|Sort Key", 50.0)
    general.idle_wait(1.0)
    hydra.take_screenshot_game_mode("Decal_6", decal_2_entity_name)


if __name__ == "__main__":
    run()
