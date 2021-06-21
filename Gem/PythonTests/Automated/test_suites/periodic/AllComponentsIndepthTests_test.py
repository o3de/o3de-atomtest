"""
All or portions of this file Copyright (c) Amazon.com, Inc. or its affiliates or
its licensors.

For complete copyright and license terms please see the LICENSE at the root of this
distribution (the "License"). All use of this software is governed by the License,
or, if provided, by the license below or the license accompanying this file. Do not
remove or modify any license notices. This file is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

Does in-depth component tests for a new level setup, as well as the Light component with "Area" and "Spot" options.
Utilizes screenshots & log lines printed from a hydra script to verify test results.
"""

import os
import pytest

import ly_test_tools.environment.file_system as file_system

from Automated.atom_utils import hydra_test_utils as hydra
from Automated.atom_utils.automated_test_base import TestAutomationBase
from Automated.atom_utils.automated_test_base import DEFAULT_SUBFOLDER_PATH

EDITOR_TIMEOUT = 60
TEST_DIRECTORY = os.path.dirname(__file__)


class AllComponentsIndepthTestsException(Exception):
    """Custom exception class for this test."""
    pass


@pytest.mark.parametrize("project", ["AtomTest"])
@pytest.mark.parametrize("launcher_platform", ["windows_editor"])
@pytest.mark.parametrize("level", ["all_components_indepth_level"])
class TestAllComponentsIndepthTests(TestAutomationBase):

    @pytest.mark.parametrize("screenshot_name", ["AtomBasicLevelSetup.ppm"])
    def test_BasicLevelSetup_SetsUpLevel(
            self, request, editor, workspace, project, launcher_platform, level, screenshot_name,
            golden_images_directory):
        """
        Please review the hydra script run by this test for more specific test info.
        Tests that a basic rendering level setup can be created (lighting, meshes, materials, etc.).
        """
        # Clear the test level to start the test.
        file_system.delete([os.path.join(workspace.paths.engine_root(), project, "Levels", level)], True, True)

        cache_images = [os.path.join(
            workspace.paths.engine_root(), project, DEFAULT_SUBFOLDER_PATH, screenshot_name)]
        self.remove_artifacts(cache_images)

        golden_images = [os.path.join(golden_images_directory, "Windows", "AllComponentsIndepthTests", screenshot_name)]

        level_creation_expected_lines = [
            "Viewport is set to the expected size: True",
            "Basic level created"
        ]
        unexpected_lines = [
            "Trace::Assert",
            "Trace::Error",
            "Traceback (most recent call last):",
        ]

        hydra.launch_and_validate_results(
            request,
            TEST_DIRECTORY,
            editor,
            "BasicLevelSetup_test_case.py",
            timeout=EDITOR_TIMEOUT,
            expected_lines=level_creation_expected_lines,
            unexpected_lines=unexpected_lines,
            halt_on_unexpected=True,
            cfg_args=[level],
        )

        for test_screenshot, golden_screenshot in zip(cache_images, golden_images):
            self.compare_screenshots(test_screenshot, golden_screenshot)

    def test_ComponentsInBasicLevel_ScreenshotsMatchGoldenImages(
            self, request, editor, workspace, project, launcher_platform, level, golden_images_directory):
        basic_level = os.path.join(workspace.paths.engine_root(), project, "Levels", level)
        if not os.path.exists(basic_level):
            raise AllComponentsIndepthTestsException(
                f'Level "{level}" does not exist at path: "{basic_level}"\n'
                'Please run the "BasicLevelSetup_SetsUpLevel()" test first. '
                'You may also run the hydra script "BasicLevelSetup_test_case.py" directly to create the level.')

        def teardown():
            file_system.delete([os.path.join(workspace.paths.engine_root(), project, "Levels", level)], True, True)
        request.addfinalizer(teardown)

        screenshot_names = [
            "AreaLight_1.ppm",
            "AreaLight_2.ppm",
            "AreaLight_3.ppm",
            "AreaLight_4.ppm",
            "AreaLight_5.ppm",
            "AreaLight_6.ppm",
            "AreaLight_7.ppm",
            "SpotLight_1.ppm",
            "SpotLight_2.ppm",
            "SpotLight_3.ppm",
            "SpotLight_4.ppm",
            "SpotLight_5.ppm",
            "SpotLight_6.ppm",
            "SpotLight_7.ppm",
        ]

        cache_images = []
        for cache_image in screenshot_names:
            screenshot_path = os.path.join(workspace.paths.engine_root(), project, DEFAULT_SUBFOLDER_PATH, cache_image)
            cache_images.append(screenshot_path)
        self.remove_artifacts(cache_images)

        golden_images = []
        for golden_image in screenshot_names:
            golden_image_path = os.path.join(
                golden_images_directory, "Windows", "AllComponentsIndepthTests", golden_image)
            golden_images.append(golden_image_path)

        component_test_expected_lines = [
            # Level save/load
            "Level is saved successfully: True",
            "New entity created: True",
            "New entity deleted: True",
            # Area Light Component
            "Area Light Entity successfully created",
            "Area Light_test: Component added to the entity: True",
            "Area Light_test: Component removed after UNDO: True",
            "Area Light_test: Component added after REDO: True",
            "Area Light_test: Entered game mode: True",
            "Area Light_test: Exit game mode: True",
            "Area Light_test: Entity disabled initially: True",
            "Area Light_test: Entity enabled after adding required components: True",
            "Area Light_test: Entity is hidden: True",
            "Area Light_test: Entity is shown: True",
            "Area Light_test: Entity deleted: True",
            "Area Light_test: UNDO entity deletion works: True",
            "Area Light_test: REDO entity deletion works: True",
            # Spot Light Component
            "Spot Light Entity successfully created",
            "Spot Light_test: Component added to the entity: True",
            "Spot Light_test: Component removed after UNDO: True",
            "Spot Light_test: Component added after REDO: True",
            "Spot Light_test: Entered game mode: True",
            "Spot Light_test: Exit game mode: True",
            "Spot Light_test: Entity is hidden: True",
            "Spot Light_test: Entity is shown: True",
            "Spot Light_test: Entity deleted: True",
            "Spot Light_test: UNDO entity deletion works: True",
            "Spot Light_test: REDO entity deletion works: True",
            "Component tests completed",
        ]
        unexpected_lines = [
            "Trace::Assert",
            "Trace::Error",
            "Traceback (most recent call last):",
        ]

        hydra.launch_and_validate_results(
            request,
            TEST_DIRECTORY,
            editor,
            "AllComponentsIndepthTests_test_case.py",
            timeout=EDITOR_TIMEOUT,
            expected_lines=component_test_expected_lines,
            unexpected_lines=unexpected_lines,
            halt_on_unexpected=True,
            cfg_args=[level],
        )

        for test_screenshot, golden_screenshot in zip(self.cache_images, self.golden_images):
            self.compare_screenshots(test_screenshot, golden_screenshot)
