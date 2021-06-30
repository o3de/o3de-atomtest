"""
Copyright (c) Contributors to the Open 3D Engine Project

SPDX-License-Identifier: Apache-2.0 OR MIT

import azlmbr.materialeditor will fail with a ModuleNotFound error when using this script with Editor.exe
This is because azlmbr.materialeditor only binds to MaterialEditor.exe and not Editor.exe
You need to launch this script with MaterialEditor.exe in order for azlmbr.materialeditor to appear.
"""

import os
import sys

import azlmbr.bus
import azlmbr.materialeditor
import azlmbr.paths
import azlmbr.atom

sys.path.append(os.path.join(azlmbr.paths.devroot, "AtomTest", "Gem", "PythonTests"))

import Automated.atom_utils.material_editor_utils as material_editor
from Automated.atom_utils.material_editor_utils import MaterialEditorHelper, capture_screenshot

screenshotsFolder = os.path.join(azlmbr.paths.devroot, "AtomTest", "Cache", "pc", "Screenshots")


class TestMaterialEditorEnableGridShadowCatcherLight(MaterialEditorHelper):
    def __init__(self):
        MaterialEditorHelper.__init__(self, log_prefix="MaterialEditorEnableGridShadowCatcherLight")

    def run_test(self):
        """
        Summary:
        Enabling Grid, Shadow Catcher and Changing Background Image/Lighting works as expected

        Expected Result:
        The grid surrounding the model in viewport will toggle on, appearing as a grid under the model in viewport.
        The grid surrounding the model in viewport will toggle off, causing the grid underneath to disappear.
        Shadow Catcher toggles on, causing shadows below the cube to appear and disappear.
        The viewport background shifts from a cityscape to Greenwich Park.
        The mesh appearing in the viewport is set to Shader Ball. The mesh appearing in the viewport shifts
        from the previous model (Shader Ball) to a Cube shape.

        :return: None
        """

        # Toggle on the Grid in Viewport menu and take screenshot
        material_editor.set_grid_enable_disable(True)
        print(f"The grid is toggled ON in viewport: {material_editor.get_grid_enable_disable()}")
        capture_screenshot(os.path.join(screenshotsFolder, "screenshot_materialeditor_gridenable.ppm"))

        # Toggle off the Grid in Viewport menu and take screenshot
        material_editor.set_grid_enable_disable(False)
        print(f"The grid is toggled OFF in viewport: {not material_editor.get_grid_enable_disable()}")
        capture_screenshot(os.path.join(screenshotsFolder, "screenshot_materialeditor_griddisable.ppm"))

        # Toggle on the Shadow Catcher in Viewport menu and take screenshot
        material_editor.set_shadowcatcher_enable_disable(True)
        print(f"Shadow Catcher is toggled ON in viewport: {material_editor.get_shadowcatcher_enable_disable()}")
        capture_screenshot(os.path.join(screenshotsFolder, "screenshot_materialeditor_shadowenable.ppm"))

        # Toggle off the Shadow Catcher in Viewport menu and take screenshot
        material_editor.set_shadowcatcher_enable_disable(False)
        print(f"Shadow Catcher is toggled OFF in viewport: {not material_editor.get_shadowcatcher_enable_disable()}")
        capture_screenshot(os.path.join(screenshotsFolder, "screenshot_materialeditor_shadowdisable.ppm"))

        # Change Lighting dropdown from default (Neutral Urban) to Greenwich Park and take screenshot
        material_editor.select_lighting_config("Greenwich Park")
        capture_screenshot(os.path.join(screenshotsFolder, "screenshot_materialeditor_light.ppm"))

        # Set model as "Shader Ball" in Viewport menu and take screenshot
        material_editor.select_model_config("Shader Ball")
        capture_screenshot(os.path.join(screenshotsFolder, "screenshot_materialeditor_shaderball.ppm"))

        # Set model as "Cube" in Viewport menu and take screenshot
        material_editor.select_model_config("Cube")
        capture_screenshot(os.path.join(screenshotsFolder, "screenshot_materialeditor_cube.ppm"))


test = TestMaterialEditorEnableGridShadowCatcherLight()
test.run()
