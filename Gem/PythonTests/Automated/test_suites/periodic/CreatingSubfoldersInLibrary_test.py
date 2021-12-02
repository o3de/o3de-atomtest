"""
Copyright (c) Contributors to the Open 3D Engine Project.
For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT
"""

import os
import pytest

import ly_test_tools.environment.file_system as file_system
from Automated.atom_utils import hydra_test_utils as hydra


TEST_DIRECTORY = os.path.dirname(__file__)
LOG_MONITOR_TIMEOUT = 30


@pytest.mark.parametrize("project", ["AtomTest"])
@pytest.mark.parametrize("launcher_platform", ["windows_generic"])
class TestCreatingSubfoldersInLibrary(object):
    @pytest.fixture(autouse=True)
    def setup_teardown(self, request, workspace, project):
        def delete_files():
            file_system.delete(
                [os.path.join(workspace.paths.engine_root(), "Gems", "Atom", "TestData", "New Sub Folder")],
                True,
                True,
            )

        # Cleanup test folders created
        delete_files()

        def teardown():
            # Cleanup test folders created
            delete_files()

        request.addfinalizer(teardown)

    @pytest.mark.parametrize("exe_file_name", ["MaterialEditor"])
    def test_SubFolderCreation_InLibrary_CreatedSuccessfully(
        self, request, workspace, project, launcher_platform, generic_launcher, exe_file_name
    ):
        """
        Please review the hydra script run by this test for more specific test info.
        Test for creating Subfolders within Library.
        """
        expected_lines = [
            "New sub folder created: True",
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
            "CreatingSubfoldersInLibrary_test_case.py",
            timeout=LOG_MONITOR_TIMEOUT,
            expected_lines=expected_lines,
            unexpected_lines=unexpected_lines,
            halt_on_unexpected=True,
            log_file_name="MaterialEditor.log",
        )
