"""
All or portions of this file Copyright (c) Amazon.com, Inc. or its affiliates or
its licensors.

For complete copyright and license terms please see the LICENSE at the root of this
distribution (the "License"). All use of this software is governed by the License,
or, if provided, by the license below or the license accompanying this file. Do not
remove or modify any license notices. This file is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""

import os
import pytest

from Automated.atom_utils import hydra_test_utils as hydra
from Automated.atom_utils.automated_test_base import TestAutomationBase

test_directory = os.path.dirname(__file__)
log_monitor_timeout = 60


@pytest.mark.parametrize("project", ["AtomTest"])
@pytest.mark.parametrize("launcher_platform", ["windows_generic"])
@pytest.mark.system
class TestMaterialBrowser_SearchAssets_Works(TestAutomationBase):
    @pytest.mark.test_case_id("C34448135")
    @pytest.mark.parametrize("exe_file_name", ["MaterialEditor"])
    def test_MaterialBrowser_SearchAssets_Works(
        self, request, launcher_platform, generic_launcher, exe_file_name,
    ):

        expected_lines = [
            "Asset Browser opened: True",
            "All materials with the word 'basic' in their names are filtered in Asset Browser",
            "basic_grey.material asset is filtered in Asset Browser",
        ]

        hydra.launch_and_validate_results(
            request,
            test_directory,
            generic_launcher,
            "MaterialBrowser_SearchAssets_Works.py",
            timeout=log_monitor_timeout,
            expected_lines=expected_lines,
            halt_on_unexpected=True,
            log_file_name="MaterialEditor.log",
        )
