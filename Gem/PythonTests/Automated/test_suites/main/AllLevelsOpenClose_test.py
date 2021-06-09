"""
All or portions of this file Copyright (c) Amazon.com, Inc. or its affiliates or
its licensors.

For complete copyright and license terms please see the LICENSE at the root of this
distribution (the "License"). All use of this software is governed by the License,
or, if provided, by the license below or the license accompanying this file. Do not
remove or modify any license notices. This file is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

Tests for levels inside the AtomTest "Levels" directory.
"""

import logging
import os
from pathlib import PurePath
import pytest

import ly_test_tools.environment.file_system as file_system
from Automated.atom_utils import hydra_test_utils as hydra

logger = logging.getLogger(__name__)


EDITOR_TIMEOUT = 60
TEST_DIRECTORY = os.path.dirname(__file__)
# Go to the project root directory
PROJECT_DIRECTORY = PurePath(TEST_DIRECTORY)
if len(PROJECT_DIRECTORY.parents) > 5:
    for _ in range(5):
        PROJECT_DIRECTORY = PROJECT_DIRECTORY.parent


@pytest.mark.parametrize("project", ["AtomTest"])
@pytest.mark.parametrize("launcher_platform", ['windows_editor'])
@pytest.mark.parametrize("level", ["tmp_level"])
class TestAllLevels(object):
    @pytest.fixture(autouse=True)
    def setup_teardown(self, request, workspace, project, level):
        # Cleanup our temp level
        file_system.delete([os.path.join(workspace.paths.engine_root(), project, "Levels", level)], True, True)

        def teardown():
            # Cleanup our temp level
            file_system.delete([os.path.join(workspace.paths.engine_root(), project, "Levels", level)], True, True)

        request.addfinalizer(teardown)

    def test_OpenCloseAllLevels_FindsExpectedLines(self, request, editor, level, workspace, project, launcher_platform):
        """
        Please review the hydra script run by this test for more specific test info.
        Tests that all levels inside the AtomTest "Levels" directory can be opened & closed without any issues.
        """
        cfg_args = [level]
        test_levels = os.listdir(os.path.join(str(PROJECT_DIRECTORY), "Levels"))
        test_levels.append(level)

        expected_lines = []
        for level in test_levels:
            expected_lines.append(f"Successfully opened {level}")

        unexpected_lines = [
            "The following levels failed to open:",
            "Trace::Assert",
            "Trace::Error",
            "Traceback (most recent call last):",
        ]

        hydra.launch_and_validate_results(
            request,
            TEST_DIRECTORY,
            editor,
            "AllLevelsOpenClose_test_case.py",
            timeout=EDITOR_TIMEOUT,
            expected_lines=expected_lines,
            unexpected_lines=unexpected_lines,
            halt_on_unexpected=True,
            cfg_args=cfg_args,
        )
