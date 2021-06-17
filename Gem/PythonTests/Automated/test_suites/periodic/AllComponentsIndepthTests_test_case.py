"""
All or portions of this file Copyright (c) Amazon.com, Inc. or its affiliates or
its licensors.

For complete copyright and license terms please see the LICENSE at the root of this
distribution (the "License"). All use of this software is governed by the License,
or, if provided, by the license below or the license accompanying this file. Do not
remove or modify any license notices. This file is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

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

sys.path.append(os.path.join(azlmbr.paths.devroot, "AtomTest", "Gem", "PythonTests"))

from Automated.atom_utils import hydra_editor_utils as hydra
from Automated.atom_utils.automated_test_utils import TestHelper as helper
from Automated.atom_utils.automated_test_utils import LIGHT_TYPES
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

    # TODO: Update this test case similar to how the above was updated:
    Test Case - Spot Light:
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
    11. Selects the "spot_light" entity and modifies the Cone Configuration controls to the following values:
        - Outer Cone Angle: 130
        - Inner Cone Angle: 80
        - Penumbra Bias: 0.9
    12. Enters game mode to take a screenshot for comparison, then exits game mode.
    13. Selects the "spot_light" entity and modifies the Attenuation Radius controls to the following values:
        - Mode: Explicit
        - Radius: 8
    14. Enters game mode to take a screenshot for comparison, then exits game mode.
    15. Selects the "spot_light" entity and modifies the Shadow controls to the following values:
        - Enable Shadow: On
        - ShadowmapSize: 256
    16. Enters game mode to take a screenshot for comparison, then exits game mode.
    17. Deletes the "spotlight_entity" and selects the "ground_plane" entity, updating the Material component to a new
        material.
    18. Selects the "directional_light" entity and enables the Directional Light component.
    19. Selects the "global_skylight" entity and enables the HDRi Skybox component & Global Skylight (IBL) component.
    
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
    test_class.grid_component_test()
    general.log("Component tests completed")


class TestAllComponentsIndepthTests(object):
    """
    Holds shared hydra test functions for this set of tests.
    """

    def create_entity_undo_redo_component_addition(
            self, entity_name, component, entity_translate_value=math.Vector3(512.0, 512.0, 34.0)):
        """
        Create a new entity with required components, then undo/redo those components.
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

        # undo component addition
        general.undo()
        helper.wait_for_condition(lambda: not hydra.has_components(new_entity.id, [component]), 2.0)
        general.log(
            f"{entity_name}_test: Component removed after UNDO: {not hydra.has_components(new_entity.id, [component])}")

        # redo component addition
        general.redo()
        helper.wait_for_condition(lambda: hydra.has_components(new_entity.id, [component]), 2.0)
        general.log(
            f"{entity_name}_test: Component added after REDO: {hydra.has_components(new_entity.id, [component])}")

        return new_entity

    def verify_enter_exit_game_mode(self, entity_name):
        general.enter_game_mode()
        helper.wait_for_condition(lambda: general.is_in_game_mode(), 1.0)
        general.log(f"{entity_name}_test: Entered game mode: {general.is_in_game_mode()}")
        general.exit_game_mode()
        helper.wait_for_condition(lambda: not general.is_in_game_mode(), 1.0)
        general.log(f"{entity_name}_test: Exit game mode: {not general.is_in_game_mode()}")

    def verify_required_component_addition(self, entity_name, entity_obj, components_to_add):
        """Verify if addition of required components activates entity."""
        general.log(f"Entity disabled initially: {not hydra.is_component_enabled(entity_obj.components[0])}")
        for component in components_to_add:
            entity_obj.add_component(component)
        general.idle_wait(1.0)
        helper.wait_for_condition(lambda: hydra.is_component_enabled(entity_obj.components[0]), 1.0)
        general.log(
            f"{entity_name}_test: Entity enabled after adding required components: "
            f"{hydra.is_component_enabled(entity_obj.components[0])}"
        )

    def verify_hide_unhide_entity(self, entity_name, entity_obj):
        """Verify Hide/Unhide entity with component."""
        hydra.set_visibility_state(entity_obj.id, False)
        general.idle_wait(1.0)
        helper.wait_for_condition(lambda: hydra.is_entity_hidden(entity_obj.id), 1.0)
        general.log(f"{entity_name}_test: Entity is hidden: {hydra.is_entity_hidden(entity_obj.id)}")
        hydra.set_visibility_state(entity_obj.id, True)
        helper.wait_for_condition(lambda: not hydra.is_entity_hidden(entity_obj.id), 1.0)
        general.log(f"{entity_name}_test: Entity is shown: {not hydra.is_entity_hidden(entity_obj.id)}")

    def verify_deletion_undo_redo(self, entity_name, entity_obj):
        """Verify delete/Undo/Redo deletion."""
        hydra.delete_entity(entity_obj.id)
        helper.wait_for_condition(lambda: not hydra.find_entity_by_name(entity_obj.name), 1.0)
        general.log(f"{entity_name}_test: Entity deleted: {not hydra.find_entity_by_name(entity_obj.name)}")

        general.undo()
        helper.wait_for_condition(lambda: hydra.find_entity_by_name(entity_obj.name) is not None, 1.0)
        general.log(
            f"{entity_name}_test: UNDO entity deletion works: {hydra.find_entity_by_name(entity_obj.name) is not None}"
        )

        general.redo()
        general.idle_wait(0.5)
        helper.wait_for_condition(lambda: not hydra.find_entity_by_name(entity_obj.name), 1.0)
        general.log(f"{entity_name}_test: REDO entity deletion works: {not hydra.find_entity_by_name(entity_obj.name)}")

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

    def take_screenshot_game_mode(self, screenshot_name):
        general.enter_game_mode()
        general.idle_wait(1.0)
        helper.wait_for_condition(lambda: general.is_in_game_mode())
        ScreenshotHelper(general.idle_wait_frames).capture_screenshot_blocking(f"{screenshot_name}.ppm")
        general.exit_game_mode()
        helper.wait_for_condition(lambda: not general.is_in_game_mode())

    def area_light_component_test(self):
        """
        Basic test for the "Light" component attached to an "area_light" entity.
        Example: Entity addition/deletion, undo/redo, game mode w/ Light component attached using various light types.
        """
        # Create an "area_light" entity with "Light" component using Light type of "Capsule"
        area_light_entity_name = "area_light"
        area_light_entity = self.create_entity_undo_redo_component_addition(
            entity_name=area_light_entity_name,
            component="Light",
            entity_translate_value=math.Vector3(-1.0, -2.0, 3.0)
        )
        light_component_id_pair = helper.attach_component_to_entity(area_light_entity.id, "Light")
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
        self.verify_enter_exit_game_mode(entity_name=area_light_entity_name)
        self.verify_required_component_property_value(
            entity_name=area_light_entity_name,
            component=area_light_entity.components[0],
            property_path=light_type_property,
            expected_property_value=capsule_light_type
        )
        # Update color and take screenshot in game mode
        color = math.Color(255.0, 0.0, 0.0, 0.0)
        area_light_entity.get_set_test(0, "Controller|Configuration|Color", color)
        self.take_screenshot_game_mode("AreaLight_1")

        # Update intensity value to 0.0 and take screenshot in game mode
        area_light_entity.get_set_test(0, "Controller|Configuration|Attenuation Radius|Mode", 1)
        area_light_entity.get_set_test(0, "Controller|Configuration|Intensity", 0.0)
        self.take_screenshot_game_mode("AreaLight_2")

        # Update intensity value to 1000.0 and take screenshot in game mode
        area_light_entity.get_set_test(0, "Controller|Configuration|Intensity", 1000.0)
        self.take_screenshot_game_mode("AreaLight_3")

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
            component=area_light_entity.components[0],
            property_path=light_type_property,
            expected_property_value=spot_disk_light_type
        )
        rotation = math.Vector3(DEGREE_RADIAN_FACTOR * 90.0, 0.0, 0.0)
        azlmbr.components.TransformBus(azlmbr.bus.Event, "SetLocalRotation", area_light_entity.id, rotation)
        self.take_screenshot_game_mode("AreaLight_4")

        # Swap the "Spot (disk)" light type to the "Point (sphere)" light type and take screenshot.
        point_sphere_light_type = LIGHT_TYPES[1]
        azlmbr.editor.EditorComponentAPIBus(
            azlmbr.bus.Broadcast,
            'SetComponentProperty',
            light_component_id_pair,
            light_type_property,
            point_sphere_light_type
        )
        self.verify_required_component_property_value(
            entity_name=area_light_entity_name,
            component=area_light_entity.components[0],
            property_path=light_type_property,
            expected_property_value=point_sphere_light_type
        )
        self.take_screenshot_game_mode("AreaLight_5")

        hydra.delete_entity(area_light_entity.id)

    def spot_light_component_test(self):
        """
        Basic test for the Light component attached to a "spot_light" entity.
        Example: Entity addition/deletion, undo/redo, game mode w/ Light component attached using various light types.
        """
        # Create a "spot_light" entity with "Light" component using Light Type of "Capsule"
        spot_light_entity_name = "spot_light"
        spot_light_entity = self.create_entity_undo_redo_component_addition(
            entity_name=spot_light_entity_name,
            component="Light",
            entity_translate_value=math.Vector3(0.7, -2.0, 3.8)
        )
        rotation = math.Vector3(DEGREE_RADIAN_FACTOR * 300.0, 0.0, 0.0)
        azlmbr.components.TransformBus(azlmbr.bus.Event, "SetLocalRotation", spot_light_entity.id, rotation)
        light_component_id_pair = helper.attach_component_to_entity(spot_light_entity.id, "Light")
        light_type_property = 'Controller|Configuration|Light type'
        spot_disk_light_type = LIGHT_TYPES[2]
        azlmbr.editor.EditorComponentAPIBus(
            azlmbr.bus.Broadcast,
            'SetComponentProperty',
            light_component_id_pair,
            light_type_property,
            spot_disk_light_type
        )

        # Verify required checks.
        self.verify_enter_exit_game_mode(entity_name=spot_light_entity_name)
        self.verify_required_component_property_value(
            entity_name=spot_light_entity_name,
            component=spot_light_entity.components[0],
            property_path=light_type_property,
            expected_property_value=spot_disk_light_type
        )

        # Disable components in directional_light and global_skylight and take a screenshot in game mode
        directional_light_entity = hydra.find_entity_by_name("directional_light")
        global_skylight_entity = hydra.find_entity_by_name("global_skylight")
        hydra.disable_component(directional_light_entity.components[0])
        hydra.disable_component(global_skylight_entity.components[0])
        hydra.disable_component(global_skylight_entity.components[1])
        self.take_screenshot_game_mode("SpotLight_1")

        # Change default material of ground plane entity and take screenshot
        asset_value = hydra.get_asset_by_path(
            os.path.join("Materials", "Presets", "MacBeth", "22_neutral_5-0_0-70d.azmaterial")
        )
        ground_plane_entity = hydra.find_entity_by_name("ground_plane")
        ground_plane_entity.get_set_test(0, "Default Material|Material Asset", asset_value)
        self.take_screenshot_game_mode("SpotLight_2")

        # Increase intensity value of the Spot light and take screenshot in game mode
        spot_light_entity.get_set_test(0, "Controller|Configuration|Intensity", 800.0)
        self.take_screenshot_game_mode("SpotLight_3")

        # Update the Spot light color and take screenshot in game mode
        color_value = math.Color(47.0 / 255.0, 75.0 / 255.0, 37.0 / 255.0, 255.0 / 255.0)
        spot_light_entity.get_set_test(0, "Controller|Configuration|Color", color_value)
        self.take_screenshot_game_mode("SpotLight_4")

        # # Update the Cone Configuration controls of spot light and take screenshot
        # self.spot_light.get_set_test(0, "Controller|Configuration|Cone Configuration|Outer Cone Angle", 130)
        # self.spot_light.get_set_test(0, "Controller|Configuration|Cone Configuration|Inner Cone Angle", 80)
        # self.spot_light.get_set_test(0, "Controller|Configuration|Cone Configuration|Penumbra Bias", 0.9)
        # self.take_screenshot_game_mode("SpotLight_5")
        #
        # # Update the Attenuation Radius controls of spot light and take screenshot
        # hydra.get_property_tree(self.spot_light.components[0])
        # self.spot_light.get_set_test(0, "Controller|Configuration|Attenuation Radius|Mode", 0)
        # self.spot_light.get_set_test(0, "Controller|Configuration|Attenuation Radius|Radius", 8.0)
        # self.take_screenshot_game_mode("SpotLight_6")
        #
        # # Update the Shadow controls and take screenshot
        # self.spot_light.get_set_test(0, "Controller|Configuration|Shadow|ShadowmapSize", 256.0)
        # self.spot_light.get_set_test(0, "Controller|Configuration|Shadow|Enable Shadow", True)
        # self.take_screenshot_game_mode("SpotLight_7")

    def grid_component_test(self):
        """
        Basic test for the Grid component attached to an entity.
        """
        # Get the default_entity and Grid component objects
        component_name = "Grid"
        search_filter = azlmbr.entity.SearchFilter()
        search_filter.names = ['default_level']
        default_level_id = azlmbr.entity.SearchBus(azlmbr.bus.Broadcast, 'SearchEntities', search_filter)[0]
        type_id_list = azlmbr.editor.EditorComponentAPIBus(azlmbr.bus.Broadcast, 'FindComponentTypeIdsByEntityType', [component_name], 0)
        outcome = azlmbr.editor.EditorComponentAPIBus(azlmbr.bus.Broadcast, 'GetComponentOfType', default_level_id, type_id_list[0])
        grid_component = outcome.GetValue()

        # Update grid size of the Grid component of default_level and take screenshot
        helper.set_component_property(grid_component, "Controller|Configuration|Grid Size", 64.0)
        self.take_screenshot_game_mode("Grid_1")

        # Update axis color of the Grid component of default_level and take screenshot
        color = math.Color(13.0 / 255.0, 255.0 / 255.0, 0.0 / 255.0, 255.0 / 255.0)
        helper.set_component_property(grid_component, "Controller|Configuration|Axis Color", color)
        self.take_screenshot_game_mode("Grid_2")
        
        # Update Primary Grid Spacing of the Grid component of default_level and take screenshot
        helper.set_component_property(grid_component, "Controller|Configuration|Primary Grid Spacing", 0.5)
        self.take_screenshot_game_mode("Grid_3")

        # Update Primary color of the Grid component of default_level and take screenshot
        color = math.Color(129.0 / 255.0, 96.0 / 255.0, 0.0 / 255.0, 255.0 / 255.0)
        helper.set_component_property(grid_component, "Controller|Configuration|Primary Color", color)
        self.take_screenshot_game_mode("Grid_4")
        
        # Update Secondary Grid Spacing of the Grid component of default_level and take screenshot
        helper.set_component_property(grid_component, "Controller|Configuration|Secondary Grid Spacing", 0.75)
        self.take_screenshot_game_mode("Grid_5")

        # Update Secondary color of the Grid component of default_level and take screenshot
        color = math.Color(0.0 / 255.0, 35.0 / 255.0, 161.0 / 255.0, 255.0 / 255.0)
        helper.set_component_property(grid_component, "Controller|Configuration|Secondary Color", color)
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


if __name__ == "__main__":
    run()
