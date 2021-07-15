"""
Copyright (c) Contributors to the Open 3D Engine Project.
For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT
"""

import os
import pytest

from Automated.atom_utils import hydra_test_utils as hydra

TEST_DIRECTORY = os.path.dirname(__file__)
LOG_MONITER_TIMEOUT = 60


@pytest.mark.parametrize("project", ["AtomTest"])
@pytest.mark.parametrize("launcher_platform", ["windows_generic"])
class TestMaterialEditorExitFromFileMenu(object):
    @pytest.mark.parametrize("exe_file_name", ["MaterialEditor"])
    def test_MaterialEditorExitFromFileMenu(
        self, request, workspace, project, launcher_platform, generic_launcher, exe_file_name
    ):
        """
        Please review the hydra script run by this test for more specific test info.
        Test for Exiting Material Editor using File menu -> Exit.
        """
        hydra.launch_and_validate_results(
            request,
            TEST_DIRECTORY,
            generic_launcher,
            "MaterialEditorExitFromFileMenu_test_case.py",
            timeout=LOG_MONITER_TIMEOUT,
            expected_lines=["Material Editor main window is visible", "Material Editor exited from File menu"],
            unexpected_lines=["Trace::Assert", "Trace::Error", "Traceback (most recent call last):"],
            halt_on_unexpected=True,
            log_file_name="MaterialEditor.log",
        )
