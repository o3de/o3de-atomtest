"""
Copyright (c) Contributors to the Open 3D Engine Project.
For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT
"""

import os
import pytest

from Automated.atom_utils import hydra_test_utils as hydra
from Automated.atom_utils.automated_test_base import TestAutomationBase

TEST_DIRECTORY = os.path.dirname(__file__)
LOG_MONITOR_TIMEOUT = 60

@pytest.mark.parametrize("project", ["AtomTest"])
@pytest.mark.parametrize("launcher_platform", ["windows_generic"])
class TestMaterialBrowserSearchAssets(TestAutomationBase):
    @pytest.mark.parametrize("exe_file_name", ["MaterialEditor"])
    def test_MaterialBrowser_SearchAssets_FoundSuccessfully(
        self, request, launcher_platform, generic_launcher, exe_file_name,
    ):
        """
        Please review the hydra script run by this test for more specific test info.
        Tests searching for assets in the MaterialBrowser.
        """
        expected_lines = [
            "All materials with the word 'basic' in their names are filtered in Asset Browser: True",
            "basic_grey.material asset is filtered in Asset Browser",
        ]
        unexpected_lines = [
            "Trace::Assert",
            "Trace::Error",
            "Traceback (most recent call last):",
            "All materials with the word 'basic' in their names are filtered in Asset Browser: False",
        ]

        hydra.launch_and_validate_results(
            request,
            TEST_DIRECTORY,
            generic_launcher,
            "MaterialBrowserSearchAssets_test_case.py",
            timeout=LOG_MONITOR_TIMEOUT,
            expected_lines=expected_lines,
            unexpected_lines=unexpected_lines,
            halt_on_unexpected=True,
            log_file_name="MaterialEditor.log",
        )
