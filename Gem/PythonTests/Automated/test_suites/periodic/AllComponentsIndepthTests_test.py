"""
Copyright (c) Contributors to the Open 3D Engine Project.
For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT

Does in-depth component tests for a new level setup, as well as tests for the Atom renderer Light component.
Utilizes screenshots & log lines printed from a hydra script to verify test results.
"""

import os
import pytest

from Automated.atom_utils import hydra_test_utils as hydra
from Automated.atom_utils.automated_test_base import TestAutomationBase, DEFAULT_SUBFOLDER_PATH, LIGHT_TYPES

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
            timeout=180,
            expected_lines=level_creation_expected_lines,
            unexpected_lines=unexpected_lines,
            halt_on_unexpected=True,
            cfg_args=[level],
        )

        for test_screenshot, golden_screenshot in zip(cache_images, golden_images):
            self.compare_screenshots(test_screenshot, golden_screenshot)

    def test_LightComponentsInBasicLevel_ScreenshotsMatchGoldenImages(
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
        expected_lines = [
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
            timeout=120,
            expected_lines=expected_lines,
            unexpected_lines=unexpected_lines,
            halt_on_unexpected=True,
            cfg_args=[level],
        )

        for test_screenshot, golden_screenshot in zip(cache_images, golden_images):
            self.compare_screenshots(test_screenshot, golden_screenshot)

    def test_DecalGridComponentsInBasicLevel_ScreenshotsMatchGoldenImages(
            self, request, editor, workspace, project, launcher_platform, level, golden_images_directory):
        """
        Please review the hydra script run by this test for more specific test info.
        Tests that the Decale & Grid components gives the output we expect when used in a level.
        """
        screenshot_names = [
            "Grid_1.ppm",
            "Grid_2.ppm",
            "Grid_3.ppm",
            "Grid_4.ppm",
            "Grid_5.ppm",
            "Grid_6.ppm",
            "Decal_1.ppm",
            "Decal_2.ppm",
            "Decal_3.ppm",
            "Decal_4.ppm",
            "Decal_5.ppm",
            "Decal_6.ppm",
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

        grid_entity = "grid_entity"
        decal_1 = "decal_1"
        decal_2 = "decal_2"
        expected_lines = [
            f"{grid_entity}_test: Entered game mode: True",
            f"{grid_entity}_test: Exit game mode: True",
            f"SUCCESS: Retrieved property Value for {grid_entity}",
            f"{grid_entity} Controller|Configuration|Grid Size: SUCCESS",
            f"{grid_entity} Controller|Configuration|Axis Color: SUCCESS",
            f"{grid_entity} Controller|Configuration|Primary Grid Spacing: SUCCESS",
            f"{grid_entity} Controller|Configuration|Primary Color: SUCCESS",
            f"{grid_entity} Controller|Configuration|Secondary Color: SUCCESS",
            f"{grid_entity} Controller|Configuration|Secondary Grid Spacing: SUCCESS",
            f"{decal_1} Entity successfully created",
            "Decal (Atom) component was added to entity",
            f"{decal_1}_test: Entered game mode: True",
            f"{decal_1}_test: Exit game mode: True",
            f"SUCCESS: Retrieved new property Value for {decal_1}",
            f"{decal_1} Controller|Configuration|Opacity: SUCCESS",
            f"{decal_1} Controller|Configuration|Attenuation Angle: SUCCESS",
            f"{decal_2}_test: Entered game mode: True",
            f"{decal_2}_test: Exit game mode: True",
            f"SUCCESS: Retrieved new property Value for {decal_2}",
            f"{decal_2} Controller|Configuration|Material: SUCCESS",
            f"{decal_2} Controller|Configuration|Sort Key: SUCCESS",
            "Component tests completed",
        ]
        unexpected_lines = [
            "Trace::Assert",
            "Trace::Error",
            "Traceback (most recent call last):",
            "screenshot failed",
            f"FAILURE: Failed to find value in {grid_entity}",
            f"FAILURE: Failed to find value in {decal_1}",
            f"FAILURE: Failed to find value in {decal_2}"
        ]

        hydra.launch_and_validate_results(
            request,
            TEST_DIRECTORY,
            editor,
            "AllComponentsIndepthDecalGridTests_test_case.py",
            timeout=120,
            expected_lines=expected_lines,
            unexpected_lines=unexpected_lines,
            halt_on_unexpected=True,
            cfg_args=[level],
        )

        for test_screenshot, golden_screenshot in zip(cache_images, golden_images):
            self.compare_screenshots(test_screenshot, golden_screenshot)
