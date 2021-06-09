"""
All or portions of this file Copyright (c) Amazon.com, Inc. or its affiliates or
its licensors.

For complete copyright and license terms please see the LICENSE at the root of this
distribution (the "License"). All use of this software is governed by the License,
or, if provided, by the license below or the license accompanying this file. Do not
remove or modify any license notices. This file is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

Tests that the transform manipulators work as expected on entities within the Editor.
Utilizes log lines printed from a hydra script to verify test results.
"""

import pytest
import os

from Automated.atom_utils import hydra_test_utils as hydra
from Automated.atom_utils.automated_test_base import TestAutomationBase
from Automated.atom_utils.automated_test_base import DEFAULT_SUBFOLDER_PATH
from Automated.atom_utils import registry_utils

REG_PATH = os.path.join('Software', 'Amazon', 'Open 3D Engine', 'Settings')
TEST_DIRECTORY = os.path.dirname(__file__)
EDITOR_TIMEOUT = 30


@pytest.mark.parametrize("project", ["AtomTest"])
@pytest.mark.parametrize("launcher_platform", ['windows_editor'])
class TestAutomation(TestAutomationBase):
    @classmethod
    def setup_class(cls):
        cls.vim_value = registry_utils.get_ly_registry_value(REG_PATH, 'ViewportInteractionModel')
        if cls.vim_value != 1:
            registry_utils.set_ly_registry_value(REG_PATH, 'ViewportInteractionModel', 1)
        cls.show_grid = registry_utils.get_ly_registry_value(REG_PATH, 'ShowGridGuide')
        if cls.show_grid != 0:
            registry_utils.set_ly_registry_value(REG_PATH, 'ShowGridGuide', 0)

    @classmethod
    def teardown_class(cls):
        registry_utils.set_ly_registry_value(REG_PATH, 'ViewportInteractionModel', cls.vim_value)
        registry_utils.set_ly_registry_value(REG_PATH, 'ShowGridGuide', cls.show_grid)

    def test_TransformManipulators_ScaleCorrectlyBasedOnCamera(
            self, request, workspace, editor, project, launcher_platform, golden_images_directory):
        """
        Please review the hydra script run by this test for more specific test info.
        Tests that the Transform Manipulator functionality is maintained within the Editor.
        """
        golden_screenshots = [
            os.path.join(golden_images_directory, 'Windows', 'TransformManipulators', 'manipulator_rotation_close.ppm'),
            os.path.join(golden_images_directory, 'Windows', 'TransformManipulators', 'manipulator_rotation_far.ppm'),
            os.path.join(golden_images_directory, 'Windows', 'TransformManipulators', 'manipulator_scale_close.ppm'),
            os.path.join(golden_images_directory, 'Windows', 'TransformManipulators', 'manipulator_scale_far.ppm'),
            os.path.join(golden_images_directory, 'Windows', 'TransformManipulators', 'manipulator_translation_close.ppm'),
            os.path.join(golden_images_directory, 'Windows', 'TransformManipulators', 'manipulator_translation_far.ppm')
        ]

        engine_root = workspace.paths.engine_root()
        test_screenshots = [
            os.path.join(engine_root, project, DEFAULT_SUBFOLDER_PATH, 'manipulator_rotation_close.ppm'),
            os.path.join(engine_root, project, DEFAULT_SUBFOLDER_PATH, 'manipulator_rotation_far.ppm'),
            os.path.join(engine_root, project, DEFAULT_SUBFOLDER_PATH, 'manipulator_scale_close.ppm'),
            os.path.join(engine_root, project, DEFAULT_SUBFOLDER_PATH, 'manipulator_scale_far.ppm'),
            os.path.join(engine_root, project, DEFAULT_SUBFOLDER_PATH, 'manipulator_translation_close.ppm'),
            os.path.join(engine_root, project, DEFAULT_SUBFOLDER_PATH, 'manipulator_translation_far.ppm')
        ]

        self.remove_artifacts(test_screenshots)

        expected_lines = [
            "Screenshot taken.",
            "All screenshots finished."
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
            "TransformManipulators_test_case.py",
            timeout=EDITOR_TIMEOUT,
            expected_lines=expected_lines,
            unexpected_lines=unexpected_lines,
            halt_on_unexpected=True,
        )
        for test_screenshot, golden_screenshot in zip(test_screenshots, golden_screenshots):
            self.compare_screenshots(test_screenshot, golden_screenshot)
