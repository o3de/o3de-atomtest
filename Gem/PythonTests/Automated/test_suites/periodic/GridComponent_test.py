"""
All or portions of this file Copyright (c) Amazon.com, Inc. or its affiliates or
its licensors.

For complete copyright and license terms please see the LICENSE at the root of this
distribution (the "License"). All use of this software is governed by the License,
or, if provided, by the license below or the license accompanying this file. Do not
remove or modify any license notices. This file is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

Tests the Grid component inside the Editor.
Utilizes screenshots & log lines printed from a hydra script to verify test results.
"""

import os
import pytest

from Automated.atom_utils import hydra_test_utils as hydra
from Automated.atom_utils.automated_test_base import TestAutomationBase
from Automated.atom_utils.automated_test_base import DEFAULT_SUBFOLDER_PATH

TEST_DIRECTORY = os.path.dirname(__file__)
EDITOR_TIMEOUT = 30


@pytest.mark.parametrize("project", ["AtomTest"])
@pytest.mark.parametrize("launcher_platform", ['windows_editor'])
class TestAutomation(TestAutomationBase):

    def test_GridComponent_HasEditorFunctionality(
            self, request, workspace, editor, project, launcher_platform, golden_images_directory):
        """
        Please review the hydra script run by this test for more specific test info.
        Tests that the Grid component functionality is maintained within the Editor.
        """
        golden_screenshot = os.path.join(golden_images_directory, 'Windows', "GridComponent.ppm")
        test_screenshot = os.path.join(
            workspace.paths.engine_root(), project, DEFAULT_SUBFOLDER_PATH, "screenshot_atom_GridComponent.ppm")
        self.remove_artifacts([test_screenshot])

        expected_lines = [
            "Entity successfully created.",
            "Components found = 1",
            "Component added to entity.",
            "Property list of component is correct.",
            "Grid size property of grid is correctly set",
            "Axis color property of grid is correctly set",
            "Primary grid spacing property of grid is correctly set",
            "Primary color property of grid is correctly set",
            "Secondary grid spacing property of grid is correctly set",
            "Secondary color property of grid is correctly set",
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
            "GridComponent_test_case.py",
            timeout=EDITOR_TIMEOUT,
            expected_lines=expected_lines,
            unexpected_lines=unexpected_lines,
            halt_on_unexpected=True,
        )
        self.compare_screenshots(test_screenshot, golden_screenshot)
