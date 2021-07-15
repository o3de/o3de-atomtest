"""
Copyright (c) Contributors to the Open 3D Engine Project.
For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT
"""

import os
import pytest

from Automated.atom_utils import hydra_test_utils as hydra
from Automated.atom_utils.automated_test_base import TestAutomationBase

TEST_DIRECTORY = os.path.dirname(__file__)
log_monitor_timeout = 60


@pytest.mark.parametrize("project", ["AtomTest"])
@pytest.mark.parametrize("launcher_platform", ["windows_generic"])
@pytest.mark.system
class TestMaterialEditorEnableGridShadowCatcherLight(TestAutomationBase):

    @pytest.mark.parametrize("exe_file_name", ["MaterialEditor"])
    def test_MaterialEditorEnableGridShadowCatcherLight(
            self, request, workspace, project, launcher_platform, generic_launcher, exe_file_name, golden_images_directory):
        golden_screenshots = [
            os.path.join(golden_images_directory, 'Windows', 'MaterialEditorCube.ppm'),
            os.path.join(golden_images_directory, 'Windows', 'MaterialEditorGridDisable.ppm'),
            os.path.join(golden_images_directory, 'Windows', 'MaterialEditorGridEnable.ppm'),
            os.path.join(golden_images_directory, 'Windows', 'MaterialEditorLight.ppm'),
            os.path.join(golden_images_directory, 'Windows', 'MaterialEditorShaderBall.ppm'),
            os.path.join(golden_images_directory, 'Windows', 'MaterialEditorShadowDisable.ppm'),
            os.path.join(golden_images_directory, 'Windows', 'MaterialEditorShadowEnable.ppm'),
        ]

        test_screenshots = [
            os.path.join(workspace.paths.project(), 'Cache', 'pc', 'Screenshots', 'screenshot_materialeditor_cube.ppm'),
            os.path.join(workspace.paths.project(), 'Cache', 'pc', 'Screenshots', 'screenshot_materialeditor_griddisable.ppm'),
            os.path.join(workspace.paths.project(), 'Cache', 'pc', 'Screenshots', 'screenshot_materialeditor_gridenable.ppm'),
            os.path.join(workspace.paths.project(), 'Cache', 'pc', 'Screenshots', 'screenshot_materialeditor_light.ppm'),
            os.path.join(workspace.paths.project(), 'Cache', 'pc', 'Screenshots', 'screenshot_materialeditor_shaderball.ppm'),
            os.path.join(workspace.paths.project(), 'Cache', 'pc', 'Screenshots', 'screenshot_materialeditor_shadowdisable.ppm'),
            os.path.join(workspace.paths.project(), 'Cache', 'pc', 'Screenshots', 'screenshot_materialeditor_shadowenable.ppm'),
        ]

        self.remove_artifacts(test_screenshots)
       
        expected_lines = [
            "The grid is toggled ON in viewport: True",
            "The grid is toggled OFF in viewport: True",
            "Shadow Catcher is toggled ON in viewport: True",
            "Shadow Catcher is toggled OFF in viewport: True",
        ]
        unexpected_lines = [
            "The grid is toggled ON in viewport: False",
            "The grid is toggled OFF in viewport: False",
            "Shadow Catcher is toggled ON in viewport: False",
            "Shadow Catcher is toggled OFF in viewport: False",
            "Trace::Assert",
            "Trace::Error",
            "Traceback (most recent call last):",
        ]

        hydra.launch_and_validate_results(
            request,
            TEST_DIRECTORY,
            generic_launcher,
            "MaterialEditor_EnableGridShadowCatcherLight_test_case.py",
            timeout=log_monitor_timeout,
            expected_lines=expected_lines,
            unexpected_lines=unexpected_lines,
            halt_on_unexpected=True,
            log_file_name="MaterialEditor.log",
        )

        for test_screenshot, golden_screenshot in zip(test_screenshots, golden_screenshots):
            self.compare_screenshots(test_screenshot, golden_screenshot)
