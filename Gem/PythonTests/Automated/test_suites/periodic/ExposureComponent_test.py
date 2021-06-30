"""
Copyright (c) Contributors to the Open 3D Engine Project

SPDX-License-Identifier: Apache-2.0 OR MIT

Tests the Exposure Control component inside the Editor.
Utilizes screenshots & log lines printed from a hydra script to verify test results.
"""

import pytest
import os

from Automated.atom_utils import hydra_test_utils as hydra
from Automated.atom_utils.automated_test_base import TestAutomationBase
from Automated.atom_utils.automated_test_base import DEFAULT_SUBFOLDER_PATH

TEST_DIRECTORY = os.path.dirname(__file__)
EDITOR_TIMEOUT = 30


@pytest.mark.parametrize("project", ["AtomTest"])
@pytest.mark.parametrize("launcher_platform", ['windows_editor'])
class TestAutomation(TestAutomationBase):

    def test_ExposureComponent_DisplaysModifiedProperties(
            self, request, workspace, editor, project, launcher_platform, golden_images_directory):
        """
        Please review the hydra script run by this test for more specific test info.
        Tests that the Exposure Control component functionality is maintained within the Editor.
        """
        golden_screenshots = [
            os.path.join(golden_images_directory, 'Windows', 'ExposureComponent_Manual.ppm'),
            os.path.join(golden_images_directory, 'Windows', 'ExposureComponent_EyeAdaptation.ppm'),
        ]

        test_screenshots = [
            os.path.join(workspace.paths.engine_root(), project, DEFAULT_SUBFOLDER_PATH,
                         'screenshot_atom_ExposureComponent_Manual.ppm'),
            os.path.join(workspace.paths.engine_root(), project, DEFAULT_SUBFOLDER_PATH,
                         'screenshot_atom_ExposureComponent_EyeAdaptation.ppm')
        ]

        self.remove_artifacts(test_screenshots)

        expected_lines = [
            "Entity successfully created.",
            "Components found = 1",
            "Component added to entity.",
            "Property list of component is correct.",
            "Exposure enabled correctly set",
            "Manual exposure type enabled correctly set",
            "Eye adaptation exposure type enabled correctly set",
            "Screenshot taken."
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
            "ExposureComponent_test_case.py",
            timeout=EDITOR_TIMEOUT,
            expected_lines=expected_lines,
            unexpected_lines=unexpected_lines,
            halt_on_unexpected=True,
        )
        for test_screenshot, golden_screenshot in zip(test_screenshots, golden_screenshots):
            self.compare_screenshots(test_screenshot, golden_screenshot)
