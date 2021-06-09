"""
All or portions of this file Copyright (c) Amazon.com, Inc. or its affiliates or
its licensors.

For complete copyright and license terms please see the LICENSE at the root of this
distribution (the "License"). All use of this software is governed by the License,
or, if provided, by the license below or the license accompanying this file. Do not
remove or modify any license notices. This file is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

WARNING: This script must be run after the "BasicLevelSetup_test_case.py" script in this same directory.

Hydra script that uses the level created by the BasicLevelSetup_test_case.py script to verify rendering.
After loading the level, it manipulates Area Lights & Spot Lights against a sphere object, and takes screenshots.
Screenshots are diffed against golden images are used to verify pass/fail results of the test.

See the run() function for more in-depth test info.
"""

import os
import sys

import azlmbr.math as math
import azlmbr.bus as bus
import azlmbr.paths
import azlmbr.entity as entity
import azlmbr.legacy.general as general
import azlmbr.editor as editor

sys.path.append(os.path.join(azlmbr.paths.devroot, "AtomTest", "Gem", "PythonTests"))

import Automated.atom_utils.hydra_editor_utils as hydra
from Automated.atom_utils.automated_test_utils import TestHelper as helper
from Automated.atom_utils.screenshot_utils import ScreenshotHelper

BASIC_LEVEL_NAME = "all_components_indepth_level"  # Created by BasicLevelSetup_test_case.py
DEGREE_RADIAN_FACTOR = 0.0174533
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720


def run():
    """
    Sets up the tests by making sure the required level is created & setup correctly.
    It then executes 2 test cases:

    Test Case - Area Light:
    1. Creates "area_light" entity w/ an Area Light component that has a Capsule Shape w/ the color set to 255, 0, 0
    2. Enters game mode to take a screenshot for comparison, then exits game mode.
    3. Sets the Area Light component Intensity Mode to Lumens (default).
    4. Ensures the Area Light component Mode is Automatic (default).
    5. Sets the Intensity value of the Area Light component to 0.0
    6. Enters game mode again, takes another  screenshot for comparison, then exits game mode.
    7. Updates the Intensity value of the Area Light component to 1000.0
    8. Enters game mode again, takes another  screenshot for comparison, then exits game mode.
    9. Deletes the Capsule Shape from "area_light" entity and adds a Disk Shape component to "area_light" entity.
    10. Updates "area_light" Transform rotate value to x: 90.0, y:0.0, z:0.0
    11. Enters game mode again, takes another  screenshot for comparison, then exits game mode.
    12. Enables the "Both Directions" field in the Area Light component.
    13. Enters game mode again, takes another  screenshot for comparison, then exits game mode.
    14. Disables the "Both Directions" field in the Area Light component.
    15. Enters game mode again, takes another  screenshot for comparison, then exits game mode.
    16. Deletes Disk Shape component from "area_light" entity & adds a Sphere Shape component to "area_light" entity.
    17. Enters game mode again, takes another  screenshot for comparison, then exits game mode.
    18. Deletes the Area Light component from the "area_light" entity and verifies its successful.

    Test Case - Spot Light:
    1. Creates "spot_light" entity w/ a Spot Light component attached to it.
    2. Selects the "directional_light" entity already present in the level and disables it.
    3. Selects the "global_skylight" entity already present in the level and disables the HDRi Skybox component,
        as well as the Global Skylight (IBL) component.
    4. Enters game mode to take a screenshot for comparison, then exits game mode.
    5. Selects the "ground_plane" entity and changes updates the material to a new material.
    6. Enters game mode to take a screenshot for comparison, then exits game mode.
    7. Selects the "spot_light" entity and increases the Spot Light component Intensity to 800 lm
    8. Enters game mode to take a screenshot for comparison, then exits game mode.
    9. Selects the "spot_light" entity and sets the Spot Light component Color to 47, 75, 37
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
    20. Prints general.log("Component tests completed") when completely finished with the test.

    Tests will fail immediately if any of these log lines are found:
    1. Trace::Assert
    2. Trace::Error
    3. Traceback (most recent call last):

    :return: None
    """
    test_class = TestAllComponentsIndepthTests()
    test_class.level_load_save(level_name=BASIC_LEVEL_NAME)
    test_class.initial_viewport_setup(screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)

    # Run tests.
    test_class.area_light_component_test()
    test_class.spot_light_component_test()
    general.log("Component tests completed")


class AllComponentsIndepthLevelMissing(Exception):
    """
    Raised when the BASIC_LEVEL_NAME level is missing.
    """
    pass


class TestAllComponentsIndepthTests(object):
    """
    Holds shared hydra test functions for this set of tests.
    """

    def atom_component_basic_setup(self):
        if not os.path.exists(
                os.path.join(azlmbr.paths.devroot, "AtomTest", "Levels", BASIC_LEVEL_NAME)):
            raise AllComponentsIndepthLevelMissing(
                f'Missing the level: "{BASIC_LEVEL_NAME}" - '
                f'Please run the BasicLevelSetup_test_case.py script to create this level as the test requires it.')

    def level_load_save(self, level_name):
        general.open_level_no_prompt(level_name)
        helper.wait_for_condition(lambda: level_name in general.get_current_level_name(), 5.0)

        # Ensure the level is saved by checking if all the entities are present
        all_entities = ["default_level", "global_skylight", "ground_plane", "directional_light", "sphere", "camera"]
        search_filter = azlmbr.entity.SearchFilter()
        search_filter.names = all_entities
        result = len(entity.SearchBus(azlmbr.bus.Broadcast, "SearchEntities", search_filter)) == len(all_entities)
        general.log(f"Level is saved successfully: {result}")

        # Create new entity
        temp_entity = hydra.Entity("temp_entity")
        temp_entity.create_entity()
        search_filter = azlmbr.entity.SearchFilter()
        search_filter.names = ["temp_entity"]
        result = len(entity.SearchBus(azlmbr.bus.Broadcast, "SearchEntities", search_filter)) == 1
        general.log(f"New entity created: {result}")

        # Delete the new entity
        editor.ToolsApplicationRequestBus(bus.Broadcast, "DeleteEntityById", temp_entity.id)
        result = len(entity.SearchBus(azlmbr.bus.Broadcast, "SearchEntities", search_filter)) == 0
        general.log(f"New entity deleted: {result}")
        general.save_level()

    def initial_viewport_setup(self, screen_width, screen_height):
        """Initial viewport setup for the test."""
        general.set_viewport_size(screen_width, screen_height)
        general.update_viewport()
        helper.wait_for_condition(
            function=lambda: helper.isclose(a=general.get_viewport_size().x, b=screen_width, rel_tol=0.1)
            and helper.isclose(a=general.get_viewport_size().y, b=screen_height, rel_tol=0.1),
            timeout_in_seconds=4.0
        )
        result = helper.isclose(a=general.get_viewport_size().x, b=screen_width, rel_tol=0.1) and helper.isclose(
            a=general.get_viewport_size().y, b=screen_height, rel_tol=0.1)
        general.log(general.get_viewport_size().x)
        general.log(general.get_viewport_size().y)
        general.log(general.get_viewport_size().z)
        general.log(f"Viewport is set to the expected size: {result}")
        general.log("Basic level created")
        general.run_console("r_DisplayInfo = 0")

    def create_entity_undo_redo_component_addition(self, component_name):
        """
        Create a new entity with required components, then undo/redo those components.
        Returns the entity after creation.
        """
        new_entity = hydra.Entity(f"{component_name}")
        new_entity.create_entity(math.Vector3(512.0, 512.0, 34.0), [component_name])
        general.log(f"{component_name}_test: Component added to the entity: {hydra.has_components(new_entity.id, [component_name])}")

        # undo component addition
        general.undo()
        helper.wait_for_condition(lambda: not hydra.has_components(new_entity.id, [component_name]), 2.0)
        general.log(f"{component_name}_test: Component removed after UNDO: {not hydra.has_components(new_entity.id, [component_name])}")

        # redo component addition
        general.redo()
        helper.wait_for_condition(lambda: hydra.has_components(new_entity.id, [component_name]), 2.0)
        general.log(f"{component_name}_test: Component added after REDO: {hydra.has_components(new_entity.id, [component_name])}")

        return new_entity

    def verify_enter_exit_game_mode(self):
        general.enter_game_mode()
        helper.wait_for_condition(lambda: general.is_in_game_mode(), 1.0)
        general.exit_game_mode()
        helper.wait_for_condition(lambda: not general.is_in_game_mode(), 1.0)

    def verify_required_component_addition(self, component_name, entity_obj, components_to_add):
        """Verify if addition of required components activates entity."""
        general.log(f"{component_name}_test: Entity disabled initially: {not hydra.is_component_enabled(entity_obj.components[0])}")
        for component in components_to_add:
            entity_obj.add_component(component)
        general.idle_wait(1.0)
        helper.wait_for_condition(lambda: hydra.is_component_enabled(entity_obj.components[0]), 1.0)
        general.log(
            f"{component_name}_test: Entity enabled after adding required components: "
            f"{hydra.is_component_enabled(entity_obj.components[0])}")

    def verify_hide_unhide_entity(self, component_name, entity_obj):
        """Verify Hide/Unhide entity with component."""
        hydra.set_visibility_state(entity_obj.id, False)
        general.idle_wait(1.0)
        helper.wait_for_condition(lambda: hydra.is_entity_hidden(entity_obj.id), 1.0)
        general.log(f"{component_name}_test: Entity is hidden: {hydra.is_entity_hidden(entity_obj.id)}")
        hydra.set_visibility_state(entity_obj.id, True)
        helper.wait_for_condition(lambda: not hydra.is_entity_hidden(entity_obj.id), 1.0)
        general.log(f"{component_name}_test: Entity is shown: {not hydra.is_entity_hidden(entity_obj.id)}")

    def verify_deletion_undo_redo(self, component_name, entity_obj):
        """Verify delete/Undo/Redo deletion."""
        hydra.delete_entity(entity_obj.id)
        helper.wait_for_condition(lambda: not hydra.find_entity_by_name(entity_obj.name), 1.0)
        general.log(f"{component_name}_test: Entity deleted: {not hydra.find_entity_by_name(entity_obj.name)}")

        general.undo()
        helper.wait_for_condition(lambda: hydra.find_entity_by_name(entity_obj.name) is not None, 1.0)
        general.log(f"{component_name}_test: UNDO entity deletion works: {hydra.find_entity_by_name(entity_obj.name) is not None}")

        general.redo()
        general.idle_wait(0.5)
        # self.wait_for_condition(lambda: not hydra.find_entity_by_name(entity_obj.name), 1.0)
        general.log(f"{component_name}_test: REDO entity deletion works: {not hydra.find_entity_by_name(entity_obj.name)}")

    def take_screenshot_game_mode(self, screenshot_name):
        general.enter_game_mode()
        general.idle_wait(1.0)
        helper.wait_for_condition(lambda: general.is_in_game_mode())
        ScreenshotHelper(general.idle_wait_frames).capture_screenshot_blocking(f"{screenshot_name}.ppm")
        general.exit_game_mode()
        helper.wait_for_condition(lambda: not general.is_in_game_mode())

    def area_light_component_test(self):
        """
        Basic test for the Area Light component attached to an entity.
        Example: Entity addition/deletion undo/redo, game mode etc. with Area Light component attached.
        """
        # Create entity with Area Light component added.
        component_name = "Area Light"
        entity_obj = self.create_entity_undo_redo_component_addition(component_name)

        # Verify required checks.
        self.verify_enter_exit_game_mode()
        self.verify_required_component_addition(entity_obj, ["Capsule Shape"])
        self.verify_hide_unhide_entity(entity_obj)
        self.verify_deletion_undo_redo(component_name, entity_obj)

        # NOTE: This step is repeated to ensure we have the expected setup while running the test for each component
        self.atom_component_basic_setup()

        # Create entity with Area Light component
        area_light = hydra.Entity("Area Light")
        position = math.Vector3(-1.0, -2.0, 3.0)
        area_light.create_entity(position, ["Area Light", "Capsule Shape"])

        # Update color and take screenshot in game mode
        color = math.Color()
        color.r, color.g, color.b, color.a = 255.0, 0.0, 0.0, 0.0
        area_light.get_set_test(0, "Controller|Configuration|Color", color)
        self.take_screenshot_game_mode("AreaLight_1")

        # Update intensity value to 0.0 and take screenshot in game mode
        area_light.get_set_test(0, "Controller|Configuration|Attenuation Radius|Mode", 1)
        area_light.get_set_test(0, "Controller|Configuration|Intensity", 0.0)
        self.take_screenshot_game_mode("AreaLight_2")

        # Update intensity value to 1000.0 and take screenshot in game mode
        area_light.get_set_test(0, "Controller|Configuration|Intensity", 1000.0)
        self.take_screenshot_game_mode("AreaLight_3")

        # Delete Capsule shape component and add Disk Shape component
        area_light.remove_component("Capsule Shape")
        area_light.add_component("Disk Shape")
        rotation = math.Vector3(DEGREE_RADIAN_FACTOR * 90.0, 0.0, 0.0)
        azlmbr.components.TransformBus(azlmbr.bus.Event, "SetLocalRotation", area_light.id, rotation)
        self.take_screenshot_game_mode("AreaLight_4")

        # Enable Both Directions in Area Light component and take screenshot
        area_light.get_set_test(0, "Controller|Configuration|Both Directions", True)
        self.take_screenshot_game_mode("AreaLight_5")

        # Disable Both Directions in Area Light component and take screenshot
        area_light.get_set_test(0, "Controller|Configuration|Both Directions", False)
        self.take_screenshot_game_mode("AreaLight_6")

        # Delete Disk shape component, add Sphere Shape and take screenshot
        area_light.remove_component("Disk Shape")
        area_light.add_component("Sphere Shape")
        self.take_screenshot_game_mode("AreaLight_7")

        # Delete Area light entity
        hydra.delete_entity(area_light.id)

    def spot_light_component_test(self):
        """
        Basic test for the Spot Light component attached to an entity.
        Example: Entity addition/deletion undo/redo, game mode etc. with Spot Light component attached.
        """
        component_name = "Spot Light"
        entity_obj = self.create_entity_undo_redo_component_addition(component_name)
        self.verify_enter_exit_game_mode()
        self.verify_hide_unhide_entity(entity_obj)
        self.verify_deletion_undo_redo(entity_obj)

        # NOTE: This step is repeated to ensure we have the expected setup while running the test for each component
        self.atom_component_basic_setup()

        # Create entity with Spot Light component
        self.spot_light = hydra.Entity("Spot Light")
        position = math.Vector3(0.7, -2.0, 3.8)
        self.spot_light.create_entity(position, ["Spot Light"])
        rotation = math.Vector3(DEGREE_RADIAN_FACTOR * 300.0, 0.0, 0.0)
        azlmbr.components.TransformBus(azlmbr.bus.Event, "SetLocalRotation", self.spot_light.id, rotation)

        # Disable components in directional_light and global_skylight and take a screenshot in game mode
        hydra.disable_component(self.directional_light.components[0])
        hydra.disable_component(self.global_skylight.components[0])
        hydra.disable_component(self.global_skylight.components[1])
        self.take_screenshot_game_mode("SpotLight_1")

        # Change default material of ground plane entity and take screenshot
        asset_value = hydra.get_asset_by_path(
            os.path.join("Materials", "Presets", "MacBeth", "22_neutral_5-0_0-70d.azmaterial")
        )
        self.ground_plane.get_set_test(0, "Default Material|Material Asset", asset_value)
        self.take_screenshot_game_mode("SpotLight_2")

        # Increase intensity value of the Spot light and take screenshot in game mode
        self.spot_light.get_set_test(0, "Controller|Configuration|Intensity", 800.0)
        self.take_screenshot_game_mode("SpotLight_3")

        # Update the Spot light color and take screenshot in game mode
        color_value = math.Color(47.0 / 255.0, 75.0 / 255.0, 37.0 / 255.0, 255.0 / 255.0)
        self.spot_light.get_set_test(0, "Controller|Configuration|Color", color_value)
        self.take_screenshot_game_mode("SpotLight_4")

        # Update the Cone Configuration controls of spot light and take screenshot
        self.spot_light.get_set_test(0, "Controller|Configuration|Cone Configuration|Outer Cone Angle", 130)
        self.spot_light.get_set_test(0, "Controller|Configuration|Cone Configuration|Inner Cone Angle", 80)
        self.spot_light.get_set_test(0, "Controller|Configuration|Cone Configuration|Penumbra Bias", 0.9)
        self.take_screenshot_game_mode("SpotLight_5")

        # Update the Attenuation Radius controls of spot light and take screenshot
        hydra.get_property_tree(self.spot_light.components[0])
        self.spot_light.get_set_test(0, "Controller|Configuration|Attenuation Radius|Mode", 0)
        self.spot_light.get_set_test(0, "Controller|Configuration|Attenuation Radius|Radius", 8.0)
        self.take_screenshot_game_mode("SpotLight_6")

        # Update the Shadow controls and take screenshot
        self.spot_light.get_set_test(0, "Controller|Configuration|Shadow|ShadowmapSize", 256.0)
        self.spot_light.get_set_test(0, "Controller|Configuration|Shadow|Enable Shadow", True)
        self.take_screenshot_game_mode("SpotLight_7")


if __name__ == "__main__":
    run()
