"""
Copyright (c) Contributors to the Open 3D Engine Project.
For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT
"""

import os
import pytest

from Automated.atom_utils import hydra_test_utils as hydra

TEST_DIRECTORY = os.path.dirname(__file__)
LOG_MONITOR_TIMEOUT = 30


@pytest.mark.parametrize("project", ["AtomTest"])
@pytest.mark.parametrize("launcher_platform", ["windows_generic"])
class TestSelectingInBrowserViaViewportTab(object):
    @pytest.mark.parametrize("exe_file_name", ["MaterialEditor"])
    def test_SelectingMaterial_OnViewportTab_SelectsMaterialInBrowser(
        self, request, workspace, project, launcher_platform, generic_launcher, exe_file_name
    ):
        """
        Please review the hydra script run by this test for more specific test info.
        Test for material selectiion in Browser via Viewport Tab
        """
        expected_lines = [
            "Material 1 opened: True",
            "Material 2 opened: True",
            "Second tab is selected: True",
            "First material is reselected in Browser: True",
        ]
        unexpected_lines = [
            "Trace::Assert",
            "Trace::Error",
            "Traceback (most recent call last):",
        ]

        hydra.launch_and_validate_results(
            request,
            TEST_DIRECTORY,
            generic_launcher,
            "SelectingInBrowserViaViewportTab_test_case.py",
            timeout=LOG_MONITOR_TIMEOUT,
            expected_lines=expected_lines,
            unexpected_lines=unexpected_lines,
            halt_on_unexpected=True,
            log_file_name="MaterialEditor.log",
        )
