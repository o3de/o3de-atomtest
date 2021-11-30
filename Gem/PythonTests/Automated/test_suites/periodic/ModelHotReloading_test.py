"""
Copyright (c) Contributors to the Open 3D Engine Project.
For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT
"""

import pytest
import os

from Automated.atom_utils import hydra_test_utils as hydra
from Automated.atom_utils.automated_test_base import TestAutomationBase
from Automated.atom_utils.automated_test_base import DEFAULT_SUBFOLDER_PATH

TEST_DIRECTORY = os.path.dirname(__file__)
EDITOR_TIMEOUT = 30


@pytest.mark.parametrize("project", ["AtomTest"])
@pytest.mark.parametrize("launcher_platform", ['windows_editor'])
class TestAutomation(TestAutomationBase):

    def test_ModelHotReloading_DisplaysAttachedMaterials(
            self, request, workspace, editor, project, launcher_platform, golden_images_directory):
        """
        Please review the hydra script run by this test for more specific test info.
        Tests that the Mesh component and Material component functionality is maintained within the Editor while hot-reloading models.
        """
        golden_screenshots = [
            os.path.join(golden_images_directory, 'Windows', 'ModelHotReload_VertexColor.ppm'),
            os.path.join(golden_images_directory, 'Windows', 'ModelHotReload_NoVertexColor.ppm')
        ]

        engine_root = workspace.paths.engine_root()
        test_screenshots = [
            os.path.join(workspace.paths.project(), DEFAULT_SUBFOLDER_PATH, 'screenshot_atom_ModelHotReload_VertexColor.ppm'),
            os.path.join(workspace.paths.project(), DEFAULT_SUBFOLDER_PATH, 'screenshot_atom_ModelHotReload_NoVertexColor.ppm')
        ]

        self.remove_artifacts(test_screenshots)
        test_models = [os.path.join(engine_root, "Gems", "Atom", "TestData", "TestData", "Objects", "ModelHotReload", "hotreload.fbx")]
        self.remove_artifacts(test_models)

        expected_lines = [
            "Entity successfully created.",
            "Component added to entity.",
            "Screenshot taken."
        ]
        unexpected_lines = [
            "Model material asset property of material is not correctly set",
            "LOD material asset property of material is not correctly set",
            "Default material asset property of material is not correctly set",
            "OnModelReady never happened",
            "There is an unexpected lod in the material map",
            "There is an unexpected material slot in the lod",
            "There was an expected material slot/lod combination that was not found",
            "Trace::Assert",
            "Traceback (most recent call last):",
        ]

        hydra.launch_and_validate_results(
            request,
            TEST_DIRECTORY,
            editor,
            "ModelHotReloading_test_case.py",
            timeout=EDITOR_TIMEOUT,
            expected_lines=expected_lines,
            unexpected_lines=unexpected_lines,
            halt_on_unexpected=True,
        )
        
        # clean up after the fact to not pollute future test runs
        self.remove_artifacts(test_models)
        for test_screenshot, golden_screenshot in zip(test_screenshots, golden_screenshots):
            self.compare_screenshots(test_screenshot, golden_screenshot)
