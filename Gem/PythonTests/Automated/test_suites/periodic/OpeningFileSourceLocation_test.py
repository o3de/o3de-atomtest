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
class TestOpeningFileSourceLocation(TestAutomationBase):
    @pytest.fixture(autouse=True)
    def setup_teardown(self, request):
        def teardown():
            # Close the beach_parking_1k_iblglobalcm.exr material opened in WindowsExplorer
            os.system('TASKKILL /F /FI "WINDOWTITLE eq LightingPresets" /IM explorer.exe')

        request.addfinalizer(teardown)

    @pytest.mark.parametrize("exe_file_name", ["MaterialEditor"])
    def test_OpeningMaterial_InAssetBrowser_OpenedSuccessfully(
        self, request, launcher_platform, generic_launcher, exe_file_name
    ):
        """
        Please review the hydra script run by this test for more specific test info.
        Tests for Opening File Source Location.
        """
        expected_lines = [
            "beach_parking_1k_iblglobalcm.exr opened with relative path: \dev\Gems\Atom\TestData\TestData\LightingPresets in WindowsExplorer",
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
            "OpeningFileSourceLocation_test_case.py",
            timeout=LOG_MONITOR_TIMEOUT,
            expected_lines=expected_lines,
            unexpected_lines=unexpected_lines,
            halt_on_unexpected=True,
            log_file_name="MaterialEditor.log",
        )
