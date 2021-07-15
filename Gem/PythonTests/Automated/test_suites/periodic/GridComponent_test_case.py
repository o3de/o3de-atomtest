"""
Copyright (c) Contributors to the Open 3D Engine Project.
For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT

Hydra script that is used to test the Grid component functionality inside the Editor.
Opens the MeshTest level & creates an entity and attaches the Grid component, modifying its size, spacing, and color.
Results are verified using log messages & screenshot comparisons diffed against golden images.

See the run() function for more in-depth test info.
"""

import os
import sys

import azlmbr.editor
import azlmbr.legacy.general as general
from azlmbr.entity import EntityId

sys.path.append(os.path.join(azlmbr.paths.devassets, "Gem", "PythonTests"))

from Automated.atom_utils.automated_test_utils import TestHelper as helper
from Automated.atom_utils.screenshot_utils import ScreenshotHelper

COMPONENT_PROPERTIES = [
    'Controller|Configuration|Secondary Grid Spacing',
    'Controller|Configuration|Primary Color',
    'Controller|Configuration|Grid Size',
    'Controller|Configuration|Axis Color',
    'Controller|Configuration|Secondary Color',
    'Controller',
    'Controller|Configuration',
    'Controller|Configuration|Primary Grid Spacing'
]


def run():
    """
    Test Case - Grid:
    1. Opens the "MeshTest" level
    2. Creates a new entity and attaches the "Grid" component to it.
    3. Modifies the Grid component's "Grid Size" to 20.0
    4. Modifies the Grid component's "Axis Color" to 1, 1, 1
    5. Modifies the Grid component's "Primary Grid Spacing" to 1.5
    6. Modifies the Grid component's "Primary Color" to 1, 1, 1
    7. Modifies the "Secondary Grid Spacing" to 0.5
    8. Modifies the "Secondary Color" to 1, 1, 1
    9. Enters game mode to take a screenshot for comparison, then exits game mode.
    10. Closes the Editor and the test ends.

    Tests will fail immediately if any of these log lines are found:
    1. Trace::Assert
    2. Trace::Error
    3. Traceback (most recent call last):

    :return: None
    """
    # Open MeshTest level.
    helper.init_idle()
    helper.open_level("MeshTest")

    # Create a new entity and attach a Grid component to it.
    myEntityId = azlmbr.editor.ToolsApplicationRequestBus(azlmbr.bus.Broadcast, 'CreateNewEntity', EntityId())
    azlmbr.editor.EditorEntityAPIBus(azlmbr.bus.Event, 'SetName', myEntityId, "Grid")
    vec3 = azlmbr.math.Vector3(6.0, 5.0, -1.0)
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetWorldTranslation", myEntityId, vec3)
    if myEntityId.IsValid():
        general.log("Entity successfully created.")
    component = helper.attach_component_to_entity(myEntityId, 'Grid')
    helper.compare_property_list(component, COMPONENT_PROPERTIES)

    # Modify the Grid Size.
    new_grid_size = 20.0
    grid_size_property_path = 'Controller|Configuration|Grid Size'
    azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'SetComponentProperty', component, grid_size_property_path, new_grid_size)
    grid_size = azlmbr.editor.EditorComponentAPIBus(azlmbr.bus.Broadcast, 'GetComponentProperty', component, grid_size_property_path)
    if grid_size.GetValue() == new_grid_size:
        general.log("Grid size property of grid is correctly set")

    # Modify the Axis Color.
    new_color = azlmbr.math.Color(0.0, 1.0, 1.0, 1.0)
    axis_color_property_path = 'Controller|Configuration|Axis Color'
    azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'SetComponentProperty', component, axis_color_property_path, new_color)
    color = azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'GetComponentProperty', component, axis_color_property_path)
    if color.GetValue() == new_color:
        general.log("Axis color property of grid is correctly set")

    # Modify the Primary Grid Spacing.
    new_primary_grid_spacing = 1.5
    primary_grid_spacing_property_path = 'Controller|Configuration|Primary Grid Spacing'
    azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'SetComponentProperty', component, primary_grid_spacing_property_path, new_primary_grid_spacing)
    primary_grid_spacing = azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'GetComponentProperty', component, primary_grid_spacing_property_path)
    if primary_grid_spacing.GetValue() == new_primary_grid_spacing:
        general.log("Primary grid spacing property of grid is correctly set")

    # Modify the Primary Color.
    primary_color_property_path = 'Controller|Configuration|Primary Color'
    azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'SetComponentProperty', component, primary_color_property_path, new_color)
    color = azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'GetComponentProperty', component, primary_color_property_path)
    if color.GetValue() == new_color:
        general.log("Primary color property of grid is correctly set")

    # Modify the Secondary Grid Spacing.
    new_secondary_grid_spacing = 0.5
    secondary_grid_spacing_spacing_property_path = 'Controller|Configuration|Secondary Grid Spacing'
    azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'SetComponentProperty', component, secondary_grid_spacing_spacing_property_path, new_secondary_grid_spacing)
    secondary_grid_spacing = azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'GetComponentProperty', component, secondary_grid_spacing_spacing_property_path)
    if secondary_grid_spacing.GetValue() == new_secondary_grid_spacing:
        general.log("Secondary grid spacing property of grid is correctly set")

    # Modify the Secondary Color.
    secondary_color_property_path = 'Controller|Configuration|Secondary Color'
    azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'SetComponentProperty', component, secondary_color_property_path, new_color)
    color = azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'GetComponentProperty', component, secondary_color_property_path)
    if color.GetValue() == new_color:
        general.log("Secondary color property of grid is correctly set")

    # Generate screenshot to compare with golden image, then close the Editor.
    ScreenshotHelper(general.idle_wait_frames).capture_screenshot_blocking_in_game_mode(
        'screenshot_atom_GridComponent.ppm')
    helper.close_editor()


if __name__ == "__main__":
    run()
