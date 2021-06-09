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

TEST_DIRECTORY = os.path.dirname(__file__)
EDITOR_TIMEOUT = 30


@pytest.mark.parametrize("project", ["AtomTest"])
class TestLaunchEditorMaterialEditorRHIArgs(object):
    @pytest.mark.parametrize("launcher_platform", ['windows_editor'])
    @pytest.mark.parametrize("cfg_args", ["-rhi=dx12", "-rhi=Vulkan", "-rhi=Null"])
    def test_EditorLaunch(self, request, editor, workspace, project, launcher_platform, cfg_args):
        expected_lines = []
        unexpected_lines = [
            "Trace::Assert",
            "Trace::Error",
            "Traceback (most recent call last):",
        ]

        hydra.launch_and_validate_results(
            request,
            TEST_DIRECTORY,
            editor,
            "",
            timeout=EDITOR_TIMEOUT,
            expected_lines=expected_lines,
            unexpected_lines=unexpected_lines,
            halt_on_unexpected=True,
            cfg_args=[cfg_args],
        )

    @pytest.mark.parametrize("launcher_platform", ['windows_generic'])
    @pytest.mark.parametrize("cfg_args", ["-rhi=dx12", "-rhi=Vulkan", "-rhi=Null"])
    @pytest.mark.parametrize("exe_file_name", ["MaterialEditor"])
    def test_MaterialEditorLaunch(
        self, request, workspace, project, generic_launcher, exe_file_name, launcher_platform, cfg_args
    ):

        expected_lines = []
        unexpected_lines = [
            "Trace::Assert",
            "Trace::Error",
            "Traceback (most recent call last):",
        ]

        hydra.launch_and_validate_results(
            request,
            TEST_DIRECTORY,
            generic_launcher,
            "",
            timeout=EDITOR_TIMEOUT,
            expected_lines=expected_lines,
            unexpected_lines=unexpected_lines,
            halt_on_unexpected=True,
            log_file_name="MaterialEditor.log",
            cfg_args=[cfg_args],
        )
