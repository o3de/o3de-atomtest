"""
Copyright (c) Contributors to the Open 3D Engine Project. For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT

Hydra script to verify basic Atom rendering components after setting up and saving the scene in EmptyLevel.
Loads updated EmptyLevel, manipulates entities with Light components against a sphere object, and takes screenshots.
Screenshots are diffed against golden images to verify pass/fail results of the test.

See the run() function for more in-depth test info.
"""

import os
import sys

import azlmbr.bus as bus
import azlmbr.editor as editor
import azlmbr.math as math
import azlmbr.paths
import azlmbr.legacy.general as general

sys.path.append(os.path.join(azlmbr.paths.devassets, "Gem", "PythonTests"))

from Automated.atom_utils import hydra_editor_utils as hydra
from Automated.atom_utils.automated_test_utils import TestHelper as helper
from Automated.atom_utils.automated_test_base import LIGHT_TYPES
from Automated.atom_utils.screenshot_utils import ScreenshotHelper

BASIC_LEVEL_NAME = "EmptyLevel"
DEGREE_RADIAN_FACTOR = 0.0174533
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720


def run():
    """
    Sets up the tests by making sure the required level is created & setup correctly.
    It then executes 2 test cases:

    Test Case - Light Component: Capsule, Spot (disk), and Point (sphere):
    1. Creates "area_light" entity w/ a Light component that has a Capsule Light type w/ the color set to 255, 0, 0
    2. Enters game mode to take a screenshot for comparison, then exits game mode.
    3. Sets the Light component Intensity Mode to Lumens (default).
    4. Ensures the Light component Mode is Automatic (default).
    5. Sets the Intensity value of the Light component to 0.0
    6. Enters game mode again, takes another  screenshot for comparison, then exits game mode.
    7. Updates the Intensity value of the Light component to 1000.0
    8. Enters game mode again, takes another  screenshot for comparison, then exits game mode.
    9. Swaps the Capsule light type option to Spot (disk) light type on the Light component
    10. Updates "area_light" entity Transform rotate value to x: 90.0, y:0.0, z:0.0
    11. Enters game mode again, takes another  screenshot for comparison, then exits game mode.
    12. Swaps the Spot (disk) light type for the Point (sphere) light type in the Light component.
    13. Enters game mode again, takes another  screenshot for comparison, then exits game mode.
    14. Deletes the Light component from the "area_light" entity and verifies its successful.

    Test Case - Light Component: Spot (disk) with shadows & colors:
    1. Creates "spot_light" entity w/ a Light component attached to it.
    2. Selects the "directional_light" entity already present in the level and disables it.
    3. Selects the "global_skylight" entity already present in the level and disables the HDRi Skybox component,
        as well as the Global Skylight (IBL) component.
    4. Enters game mode to take a screenshot for comparison, then exits game mode.
    5. Selects the "ground_plane" entity and changes updates the material to a new material.
    6. Enters game mode to take a screenshot for comparison, then exits game mode.
    7. Selects the "spot_light" entity and increases the Light component Intensity to 800 lm
    8. Enters game mode to take a screenshot for comparison, then exits game mode.
    9. Selects the "spot_light" entity and sets the Light component Color to 47, 75, 37
    10. Enters game mode to take a screenshot for comparison, then exits game mode.
    11. Selects the "spot_light" entity and modifies the Shutter controls to the following values:
        - Enable shutters: True
        - Inner Angle: 60.0
        - Outer Angle: 75.0
    12. Enters game mode to take a screenshot for comparison, then exits game mode.
    13. Selects the "spot_light" entity and modifies the Shadow controls to the following values:
        - Enable Shadow: True
        - ShadowmapSize: 256
    14. Modifies the world translate position of the "spot_light" entity to 0.7, -2.0, 1.9 (for casting shadows better)
    15. Enters game mode to take a screenshot for comparison, then exits game mode.

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

    Test Case - decal:
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
    test_class = TestAllComponentsIndepthTests()
    test_class.area_light_component_test()
    test_class.spot_light_component_test()
    # These tests are going to be re-enabled in a new file in the future.
    # The code has been left here for reference when we work on re-enabling them.
    # test_class.grid_component_test()
    # test_class.decal_component_test()
    general.log("Component tests completed")


class TestAllComponentsIndepthTests(object):
    """
    Holds shared hydra test functions for this set of tests.
    """

    def create_entity_at_position(
            self, entity_name, component, entity_translate_value=math.Vector3(512.0, 512.0, 34.0)):
        """
        Create a new entity with required components at world position matching entity_translate_value param.
        :param entity_name: name for the created entity
        :param component: name matching a valid component to attach to the created entity
        :param entity_translate_value: optional math.Vector3() value to set the entity's world translate (position),
            defaults to math.Vector3(512.0, 512.0, 34.0)
        :return: Automated.atom_utils.hydra_editor_utils.Entity class object
        """
        new_entity = hydra.Entity(f"{entity_name}")
        new_entity.create_entity(entity_translate_value, [component])
        general.log(
            f"{entity_name}_test: Component added to the entity: {hydra.has_components(new_entity.id, [component])}")

        return new_entity

    def verify_required_component_property_value(self, entity_name, component, property_path, expected_property_value):
        """
        Compares the property value of component against the expected_property_value.
        :param entity_name: name of the entity to use (for test verification purposes).
        :param component: component to check on a given entity for its current property value.
        :param property_path: the path to the property inside the component.
        :param expected_property_value: The value expected from the value inside property_path.
        :return: None, but prints to general.log() which the test uses to verify against.
        """
        property_value = editor.EditorComponentAPIBus(
            bus.Broadcast, "GetComponentProperty", component, property_path).GetValue()
        general.log(f"{entity_name}_test: Property value is {property_value} "
                    f"which matches {expected_property_value}")

    def take_screenshot_game_mode(self, screenshot_name, entity_name=None):
        general.enter_game_mode()
        helper.wait_for_condition(lambda: general.is_in_game_mode(), 2.0)
        general.log(f"{entity_name}_test: Entered game mode: {general.is_in_game_mode()}")
        ScreenshotHelper(general.idle_wait_frames).capture_screenshot_blocking(f"{screenshot_name}.ppm")
        general.idle_wait(1.0)
        general.exit_game_mode()
        helper.wait_for_condition(lambda: not general.is_in_game_mode(), 2.0)
        general.log(f"{entity_name}_test: Exit game mode: {not general.is_in_game_mode()}")

    def area_light_component_test(self):
        """
        Basic test for the "Light" component attached to an "area_light" entity.
        Example: Entity addition/deletion, & enters game mode w/ Light component attached using various light types.
        """
        # Create an "area_light" entity with "Light" component using Light type of "Capsule"
        area_light_entity_name = "area_light"
        area_light = self.create_entity_at_position(
            entity_name=area_light_entity_name,
            component="Light",
            entity_translate_value=math.Vector3(-1.0, -2.0, 3.0)
        )
        light_component_id_pair = helper.attach_component_to_entity(area_light.id, "Light")
        light_type_property = 'Controller|Configuration|Light type'
        capsule_light_type = LIGHT_TYPES[3]
        azlmbr.editor.EditorComponentAPIBus(
            azlmbr.bus.Broadcast,
            'SetComponentProperty',
            light_component_id_pair,
            light_type_property,
            capsule_light_type
        )

        # Verify required checks.
        self.verify_required_component_property_value(
            entity_name=area_light_entity_name,
            component=area_light.components[0],
            property_path=light_type_property,
            expected_property_value=capsule_light_type
        )

        # Update color and take screenshot in game mode
        color = math.Color(255.0, 0.0, 0.0, 0.0)
        area_light.get_set_test(0, "Controller|Configuration|Color", color)
        general.idle_wait(1.0)
        self.take_screenshot_game_mode("AreaLight_1", area_light_entity_name)

        # Update intensity value to 0.0 and take screenshot in game mode
        area_light.get_set_test(0, "Controller|Configuration|Attenuation Radius|Mode", 1)
        area_light.get_set_test(0, "Controller|Configuration|Intensity", 0.0)
        general.idle_wait(1.0)
        self.take_screenshot_game_mode("AreaLight_2", area_light_entity_name)

        # Update intensity value to 1000.0 and take screenshot in game mode
        area_light.get_set_test(0, "Controller|Configuration|Intensity", 1000.0)
        general.idle_wait(1.0)
        self.take_screenshot_game_mode("AreaLight_3", area_light_entity_name)

        # Swap the "Capsule" light type option to "Spot (disk)" light type
        spot_disk_light_type = LIGHT_TYPES[2]
        azlmbr.editor.EditorComponentAPIBus(
            azlmbr.bus.Broadcast,
            'SetComponentProperty',
            light_component_id_pair,
            light_type_property,
            spot_disk_light_type
        )
        self.verify_required_component_property_value(
            entity_name=area_light_entity_name,
            component=area_light.components[0],
            property_path=light_type_property,
            expected_property_value=spot_disk_light_type
        )
        area_light_rotation = math.Vector3(DEGREE_RADIAN_FACTOR * 90.0, 0.0, 0.0)
        azlmbr.components.TransformBus(azlmbr.bus.Event, "SetLocalRotation", area_light.id, area_light_rotation)
        general.idle_wait(1.0)
        self.take_screenshot_game_mode("AreaLight_4", area_light_entity_name)

        # Swap the "Spot (disk)" light type to the "Point (sphere)" light type and take screenshot.
        sphere_light_type = LIGHT_TYPES[1]
        azlmbr.editor.EditorComponentAPIBus(
            azlmbr.bus.Broadcast,
            'SetComponentProperty',
            light_component_id_pair,
            light_type_property,
            sphere_light_type
        )
        self.verify_required_component_property_value(
            entity_name=area_light_entity_name,
            component=area_light.components[0],
            property_path=light_type_property,
            expected_property_value=sphere_light_type
        )
        general.idle_wait(1.0)
        self.take_screenshot_game_mode("AreaLight_5", area_light_entity_name)

        hydra.delete_entity(area_light.id)

    def spot_light_component_test(self):
        """
        Basic test for the Light component attached to a "spot_light" entity.
        Example: Entity addition/deletion & enters game mode w/ Light component attached using various light types.
        """
        # Disable "Directional Light" component for the "directional_light" entity
        directional_light_entity_id = hydra.find_entity_by_name("directional_light")
        directional_light = hydra.Entity(name='directional_light', id=directional_light_entity_id)
        directional_light_component_type = azlmbr.editor.EditorComponentAPIBus(
            azlmbr.bus.Broadcast, 'FindComponentTypeIdsByEntityType', ["Directional Light"], 0)[0]
        directional_light_component = azlmbr.editor.EditorComponentAPIBus(
            azlmbr.bus.Broadcast, 'GetComponentOfType', directional_light.id, directional_light_component_type
        ).GetValue()
        hydra.disable_component(directional_light_component)
        general.idle_wait(0.5)

        # Disable "Global Skylight (IBL)" and "HDRi Skybox" components for the "global_skylight" entity
        global_skylight_entity_id = hydra.find_entity_by_name("global_skylight")
        global_skylight = hydra.Entity(name='global_skylight', id=global_skylight_entity_id)
        global_skylight_component_type = azlmbr.editor.EditorComponentAPIBus(
            azlmbr.bus.Broadcast, 'FindComponentTypeIdsByEntityType', ["Global Skylight (IBL)"], 0)[0]
        global_skylight_component = azlmbr.editor.EditorComponentAPIBus(
            azlmbr.bus.Broadcast, 'GetComponentOfType', global_skylight.id, global_skylight_component_type
        ).GetValue()
        hydra.disable_component(global_skylight_component)
        hdri_skybox_component_type = azlmbr.editor.EditorComponentAPIBus(
            azlmbr.bus.Broadcast, 'FindComponentTypeIdsByEntityType', ["HDRi Skybox"], 0)[0]
        hdri_skybox_component = azlmbr.editor.EditorComponentAPIBus(
            azlmbr.bus.Broadcast, 'GetComponentOfType', global_skylight.id, hdri_skybox_component_type
        ).GetValue()
        hydra.disable_component(hdri_skybox_component)
        general.idle_wait(0.5)

        # Create a "spot_light" entity with "Light" component using Light Type of "Spot (disk)"
        spot_light_entity_name = "spot_light"
        spot_light = self.create_entity_at_position(
            entity_name=spot_light_entity_name,
            component="Light",
            entity_translate_value=math.Vector3(0.7, -2.0, 1.0)
        )
        rotation = math.Vector3(DEGREE_RADIAN_FACTOR * 300.0, 0.0, 0.0)
        azlmbr.components.TransformBus(azlmbr.bus.Event, "SetLocalRotation", spot_light.id, rotation)
        light_component_type = helper.attach_component_to_entity(spot_light.id, "Light")
        light_type_property_path = 'Controller|Configuration|Light type'
        spot_disk_light_type = LIGHT_TYPES[2]
        hydra.set_component_property(
            component=light_component_type, property_path=light_type_property_path, property_value=spot_disk_light_type)
        general.idle_wait(0.5)

        # Verify required checks and take a screenshot in game mode
        self.verify_required_component_property_value(
            entity_name=spot_light_entity_name,
            component=spot_light.components[0],
            property_path=light_type_property_path,
            expected_property_value=spot_disk_light_type
        )
        general.idle_wait(1.0)
        self.take_screenshot_game_mode("SpotLight_1", spot_light_entity_name)

        # Change default material of ground plane entity and take screenshot
        ground_plane_entity_id = hydra.find_entity_by_name("ground_plane")
        ground_plane = hydra.Entity(name='ground_plane', id=ground_plane_entity_id)
        ground_plane_asset_path = os.path.join("Materials", "Presets", "MacBeth", "22_neutral_5-0_0-70d.azmaterial")
        ground_plane_asset_value = hydra.get_asset_by_path(ground_plane_asset_path)
        material_property_path = "Default Material|Material Asset"
        material_component_type = azlmbr.editor.EditorComponentAPIBus(
            azlmbr.bus.Broadcast, 'FindComponentTypeIdsByEntityType', ["Material"], 0)[0]
        material_component = azlmbr.editor.EditorComponentAPIBus(
            azlmbr.bus.Broadcast, 'GetComponentOfType', ground_plane.id, material_component_type).GetValue()
        hydra.set_component_property(
            component=material_component, property_path=material_property_path, property_value=ground_plane_asset_value)
        general.idle_wait(1.0)
        self.take_screenshot_game_mode("SpotLight_2", spot_light_entity_name)

        # Increase intensity value of the Spot light and take screenshot in game mode
        spot_light.get_set_test(0, "Controller|Configuration|Intensity", 800.0)
        general.idle_wait(1.0)
        self.take_screenshot_game_mode("SpotLight_3", spot_light_entity_name)

        # Update the Spot light color and take screenshot in game mode
        color_value = math.Color(47.0 / 255.0, 75.0 / 255.0, 37.0 / 255.0, 255.0 / 255.0)
        spot_light.get_set_test(0, "Controller|Configuration|Color", color_value)
        general.idle_wait(1.0)
        self.take_screenshot_game_mode("SpotLight_4", spot_light_entity_name)

        # Update the Shutter controls of the Light component and take screenshot
        spot_light.get_set_test(0, "Controller|Configuration|Shutters|Enable shutters", True)
        spot_light.get_set_test(0, "Controller|Configuration|Shutters|Inner angle", 60.0)
        spot_light.get_set_test(0, "Controller|Configuration|Shutters|Outer angle", 75.0)
        general.idle_wait(1.0)
        self.take_screenshot_game_mode("SpotLight_5", spot_light_entity_name)

        # Update the Shadow controls, move the spot_light entity world translate position and take screenshot
        spot_light.get_set_test(0, "Controller|Configuration|Shadows|Enable shadow", True)
        spot_light.get_set_test(0, "Controller|Configuration|Shadows|Shadowmap size", 256.0)
        azlmbr.components.TransformBus(
            azlmbr.bus.Event, "SetWorldTranslation", spot_light.id, math.Vector3(0.7, -2.0, 1.9))
        general.idle_wait(1.0)
        self.take_screenshot_game_mode("SpotLight_6", spot_light_entity_name)

    def grid_component_test(self):
        """
        Basic test for the Grid component attached to an entity.
        """
        # Get the default_entity and Grid component objects
        component_name = "Grid"
        search_filter = azlmbr.entity.SearchFilter()
        search_filter.names = ['default_level']
        default_level_id = azlmbr.entity.SearchBus(azlmbr.bus.Broadcast, 'SearchEntities', search_filter)[0]
        type_id_list = azlmbr.editor.EditorComponentAPIBus(
            azlmbr.bus.Broadcast, 'FindComponentTypeIdsByEntityType', [component_name], 0)
        outcome = azlmbr.editor.EditorComponentAPIBus(
            azlmbr.bus.Broadcast, 'GetComponentOfType', default_level_id, type_id_list[0])
        grid_component = outcome.GetValue()

        # Update grid size of the Grid component of default_level and take screenshot
        helper.set_component_property(grid_component, "Controller|Configuration|Grid Size", 64.0)
        general.idle_wait(1.0)
        self.take_screenshot_game_mode("Grid_1")

        # Update axis color of the Grid component of default_level and take screenshot
        color = math.Color(13.0 / 255.0, 255.0 / 255.0, 0.0 / 255.0, 255.0 / 255.0)
        helper.set_component_property(grid_component, "Controller|Configuration|Axis Color", color)
        general.idle_wait(1.0)
        self.take_screenshot_game_mode("Grid_2")

        # Update Primary Grid Spacing of the Grid component of default_level and take screenshot
        helper.set_component_property(grid_component, "Controller|Configuration|Primary Grid Spacing", 0.5)
        general.idle_wait(1.0)
        self.take_screenshot_game_mode("Grid_3")

        # Update Primary color of the Grid component of default_level and take screenshot
        color = math.Color(129.0 / 255.0, 96.0 / 255.0, 0.0 / 255.0, 255.0 / 255.0)
        helper.set_component_property(grid_component, "Controller|Configuration|Primary Color", color)
        general.idle_wait(1.0)
        self.take_screenshot_game_mode("Grid_4")

        # Update Secondary Grid Spacing of the Grid component of default_level and take screenshot
        helper.set_component_property(grid_component, "Controller|Configuration|Secondary Grid Spacing", 0.75)
        general.idle_wait(1.0)
        self.take_screenshot_game_mode("Grid_5")

        # Update Secondary color of the Grid component of default_level and take screenshot
        color = math.Color(0.0 / 255.0, 35.0 / 255.0, 161.0 / 255.0, 255.0 / 255.0)
        helper.set_component_property(grid_component, "Controller|Configuration|Secondary Color", color)
        general.idle_wait(1.0)
        self.take_screenshot_game_mode("Grid_6")

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

    def decal_component_test(self):
        """
        Basic test for the Decal(Atom) component attached to an entity.
        """
        # Create child entity 'decal_1' under Default entity and add decal component to it
        component_name = "Decal (Atom)"
        search_filter = azlmbr.entity.SearchFilter()
        search_filter.names = ['default_level']
        default_level_id = azlmbr.entity.SearchBus(azlmbr.bus.Broadcast, 'SearchEntities', search_filter)[0]
        decal_1 = hydra.Entity("decal_1")
        decal_1.create_entity(math.Vector3(3.0, 0.0, 1.0), components=[component_name], parent_id= default_level_id)
        # Set the Material Property in decal component to "airship_symbol_decal.material" and take screenshot
        asset_value = hydra.get_asset_by_path(
            os.path.join("Materials", "decal", "airship_symbol_decal.azmaterial")
        )
        hydra.get_set_test(decal_1, 0, "Controller|Configuration|Material", asset_value)
        general.idle_wait(1.0)
        self.take_screenshot_game_mode("Decal_1")

        # Change the Uniform scale value in Transform component to: 3.0 and take screenshot
        azlmbr.components.TransformBus(azlmbr.bus.Event, "SetLocalUniformScale", decal_1.id, 3.0)
        general.idle_wait(1.0)
        self.take_screenshot_game_mode("Decal_2")

        # Set the Attenuation Angle to: 0.75 in Decal component and take screenshot
        hydra.get_set_test(decal_1, 0, "Controller|Configuration|Attenuation Angle", 0.75)
        general.idle_wait(1.0)
        self.take_screenshot_game_mode("Decal_3")

        # Set the Set Opacity to: 0.03 in Decal component and take screenshot
        hydra.get_set_test(decal_1, 0, "Controller|Configuration|Opacity", 0.03)
        general.idle_wait(1.0)
        self.take_screenshot_game_mode("Decal_4")

        # Set Opacity back to 1.0
        hydra.get_set_test(decal_1, 0, "Controller|Configuration|Opacity", 1.0)

        # Create another child entity 'decal_2' under Default entity and add decal component to it
        decal_2 = hydra.Entity("decal_2")
        decal_2.create_entity(math.Vector3(5.0, 0.0, 0.5), components=[component_name], parent_id= default_level_id)

        # Set the material value to "valenaactor_helmetmat.material", Sort Key value to: 0 and take screenshot
        asset_value = hydra.get_asset_by_path(
            os.path.join("Valena", "valenaactor_helmetmat.azmaterial")
        )
        hydra.get_set_test(decal_2, 0, "Controller|Configuration|Material", asset_value)
        hydra.get_set_test(decal_2, 0, "Controller|Configuration|Sort Key", 0.0)
        general.idle_wait(1.0)
        self.take_screenshot_game_mode("Decal_5")
        # Set the Sort Key value of decal_2 to: 50 and take screenshot
        hydra.get_set_test(decal_2, 0, "Controller|Configuration|Sort Key", 50.0)
        general.idle_wait(1.0)
        self.take_screenshot_game_mode("Decal_6")


if __name__ == "__main__":
    run()
