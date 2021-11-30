"""
Copyright (c) Contributors to the Open 3D Engine Project.
For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT

Tests FBX mesh import scaling by modifying the x, y, z scaling on a list of meshes attached to entities.
Utilizes screenshots & log lines printed from a hydra script to verify test results.
"""

import os
import pytest

from Automated.atom_utils import hydra_test_utils as hydra
from Automated.atom_utils.automated_test_base import DEFAULT_SUBFOLDER_PATH, TestAutomationBase

TEST_DIRECTORY = os.path.dirname(__file__)
EDITOR_TIMEOUT = 30


@pytest.mark.parametrize("project", ["AtomTest"])
@pytest.mark.parametrize("launcher_platform", ['windows_editor'])
class TestAutomation(TestAutomationBase):

    def test_MeshScaling_AllMeshesScaleTheSame(
            self, request, workspace, editor, project, launcher_platform, golden_images_directory):
        """
        Please review the hydra script run by this test for more specific test info.
        Tests that FBX meshes scale correctly.
        """
        expected_lines = ["FBX mesh scaling test has completed."]
        unexpected_lines = [
            "Trace::Assert",
            "Trace::Error",
            "Traceback (most recent call last):",
        ]

        hydra.launch_and_validate_results(
            request,
            TEST_DIRECTORY,
            editor,
            "MeshScaling_test_case.py",
            timeout=EDITOR_TIMEOUT,
            expected_lines=expected_lines,
            unexpected_lines=unexpected_lines,
            halt_on_unexpected=True,
        )

        golden_screenshot = os.path.join(golden_images_directory, 'Windows', 'FBXMeshScaling.ppm')
        test_screenshot = os.path.join(
            workspace.paths.project(), DEFAULT_SUBFOLDER_PATH, "screenshot_atom_FBXMeshScaling.dds")
        self.compare_screenshots(test_screenshot, golden_screenshot)
