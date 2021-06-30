"""
Copyright (c) Contributors to the Open 3D Engine Project. For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT

Tests the AssetCollectionAsyncLoader which handles detecting and loading assets asynchronously.
Utilizes log lines printed from a hydra script to verify test results.
"""

import pytest
import os

from Automated.atom_utils import hydra_test_utils as hydra
from Automated.atom_utils.automated_test_base import TestAutomationBase

TEST_DIRECTORY = os.path.dirname(__file__)
EDITOR_TIMEOUT = 30


@pytest.mark.parametrize("project", ["AtomTest"])
@pytest.mark.parametrize("launcher_platform", ['windows_editor'])
class TestAutomation(TestAutomationBase):
    def test_AssetCollectionAsyncLoader_DetectsAndLoadsAssetsAsynchronously(
            self, request, workspace, editor, project, launcher_platform):
        """
        Please review the hydra script run by this test for more specific test info.
        Tests AssetCollectionAsyncLoader functionaltiy inside the Editor.
        """
        expected_lines = [
            "Entity successfully created.",
            "SUCCESS: Assets were queued for loading.",
            "SUCCESS: Pending list contains the same asset paths as the original list",
            "SUCCESS: No asset was available",
            "SUCCESS: Cancelled an impossible job",
            "SUCCESS: The AssetCollectionAsyncLoader loaded all requested assets.",
            "SUCCESS: The AssetCollectionAsyncLoader PASSED the test"
        ]
        unexpected_lines = [
            "Trace::Assert",
            "Trace::Error",
            "Traceback (most recent call last):",
            "ERROR: Was expecting 0 pending assets",
            "ERROR: Failed to submit assets for asynchronous loading.",
            "ERROR: Was expecting the same list size.",
            "ERROR: Asset is not present in the pending list:",
            "ERROR: Asset should not be available:",
            "ERROR: Failed to copy temp source asset",
            "ERROR: Failed to load assets asynchronously",
            "ERROR: Asset should be available:",
        ]

        hydra.launch_and_validate_results(
            request,
            TEST_DIRECTORY,
            editor,
            "AssetCollectionLoadManager_test_case.py",
            timeout=EDITOR_TIMEOUT,
            expected_lines=expected_lines,
            unexpected_lines=unexpected_lines,
            halt_on_unexpected=True,
        )
