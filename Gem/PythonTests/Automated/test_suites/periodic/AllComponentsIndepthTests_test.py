"""
Copyright (c) Contributors to the Open 3D Engine Project. For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT

Does in-depth component tests for a new level setup, as well as tests for the Atom renderer Light component.
Utilizes screenshots & log lines printed from a hydra script to verify test results.
"""

import os
import pytest

from Automated.atom_utils import hydra_test_utils as hydra
from Automated.atom_utils.automated_test_base import TestAutomationBase, DEFAULT_SUBFOLDER_PATH, LIGHT_TYPES

EDITOR_TIMEOUT = 180
TEST_DIRECTORY = os.path.dirname(__file__)


class AllComponentsIndepthTestsException(Exception):
    """Custom exception class for this test."""
    pass


@pytest.mark.parametrize("project", ["AtomTest"])
@pytest.mark.parametrize("launcher_platform", ["windows_editor"])
@pytest.mark.parametrize("level", ["EmptyLevel"])
class TestAllComponentsIndepthTests(TestAutomationBase):

    @pytest.mark.parametrize("screenshot_name", ["AtomBasicLevelSetup.ppm"])
    def test_BasicLevelSetup_SetsUpLevel(
            self, request, editor, workspace, project, launcher_platform, level, screenshot_name,
            golden_images_directory):
        """
        Please review the hydra script run by this test for more specific test info.
        Tests that a basic rendering level setup can be created (lighting, meshes, materials, etc.).
        """
        cache_images = [os.path.join(
            workspace.paths.project(), DEFAULT_SUBFOLDER_PATH, screenshot_name)]
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
        """
        Please review the hydra script run by this test for more specific test info.
        Tests that the Light component gives the output we expect when used in a level.
        """
        screenshot_names = [
            "AreaLight_1.ppm",
            "AreaLight_2.ppm",
            "AreaLight_3.ppm",
            "AreaLight_4.ppm",
            "AreaLight_5.ppm",
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
            screenshot_path = os.path.join(workspace.paths.project(), DEFAULT_SUBFOLDER_PATH, cache_image)
            cache_images.append(screenshot_path)
        self.remove_artifacts(cache_images)

        golden_images = []
        for golden_image in screenshot_names:
            golden_image_path = os.path.join(
                golden_images_directory, "Windows", "AllComponentsIndepthTests", golden_image)
            golden_images.append(golden_image_path)

        sphere_light_type = LIGHT_TYPES[1]
        spot_disk_light_type = LIGHT_TYPES[2]
        capsule_light_type = LIGHT_TYPES[3]
        component_test_expected_lines = [
            # Level save/load
            "Level is saved successfully: True",
            "New entity created: True",
            "New entity deleted: True",
            # Area Light Component
            "area_light Entity successfully created",
            "area_light_test: Component added to the entity: True",
            "area_light_test: Entered game mode: True",
            "area_light_test: Exit game mode: True",
            f"area_light_test: Property value is {capsule_light_type} which matches {capsule_light_type}",
            f"area_light_test: Property value is {spot_disk_light_type} which matches {spot_disk_light_type}",
            f"area_light_test: Property value is {sphere_light_type} which matches {sphere_light_type}",
            # Spot Light Component
            "spot_light Entity successfully created",
            "spot_light_test: Component added to the entity: True",
            "spot_light_test: Entered game mode: True",
            "spot_light_test: Exit game mode: True",
            f"spot_light_test: Property value is {spot_disk_light_type} which matches {spot_disk_light_type}",
            "Component tests completed",
        ]
        unexpected_lines = [
            "Trace::Assert",
            "Trace::Error",
            "Traceback (most recent call last):",
            "screenshot failed",
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

        for test_screenshot, golden_screenshot in zip(cache_images, golden_images):
            self.compare_screenshots(test_screenshot, golden_screenshot)
