"""
Copyright (c) Contributors to the Open 3D Engine Project.
For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT
"""

import os
import pytest

from Automated.atom_utils import hydra_test_utils as hydra

TEST_DIRECTORY = os.path.dirname(__file__)
LOG_MONITOR_TIMEOUT = 40


@pytest.mark.parametrize("project", ["AtomTest"])
@pytest.mark.parametrize("launcher_platform", ["windows_generic"])
class TestNonMaterialAssetsExcludedInBrowser(object):
    @pytest.mark.parametrize("exe_file_name", ["MaterialEditor"])
    def test_MaterialBrowser_NonMaterialAssets_ExcludedInBrowser(
        self, request, workspace, project, launcher_platform, generic_launcher, exe_file_name
    ):
        """
        Please review the hydra script run by this test for more specific test info.
        Test to verify if Non-Material based assets excluded from Browser
        """
        unexpected_lines = [
            "Trace::Assert",
            "Trace::Error",
            "Traceback (most recent call last):",
            "Expected item not found in folder",
            "Excluded item found in folder",
            "Atom MaterialEditor asset path not found in browser: ",
        ]

        hydra.launch_and_validate_results(
            request,
            TEST_DIRECTORY,
            generic_launcher,
            "NonMaterialAssetsExcludedInBrowser_test_case.py",
            timeout=LOG_MONITOR_TIMEOUT,
            expected_lines=None,
            unexpected_lines=unexpected_lines,
            halt_on_unexpected=True,
            log_file_name="MaterialEditor.log",
        )
