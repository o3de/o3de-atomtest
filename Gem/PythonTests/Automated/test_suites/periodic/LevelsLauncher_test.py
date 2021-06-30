"""
Copyright (c) Contributors to the Open 3D Engine Project. For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT
"""

import pytest

from Automated.atom_utils import hydra_test_utils as hydra
from ly_remote_console.remote_console_commands import RemoteConsole as RemoteConsole

log_monitor_timeout = 30


@pytest.mark.parametrize("project", ["AtomTest"])
class TestLevelsLauncher(object):
    @pytest.fixture
    def remote_console_instance(self, request):
        console = RemoteConsole()

        def teardown():
            if console.connected:
                console.stop()

        request.addfinalizer(teardown)
        return console

    @pytest.mark.parametrize(
        "level",
        [
            "ActorTest_100Actors",
            "ActorTest_MultipleActors",
            "ActorTest_SingleActor",
            "ColorSpaceTest",
            "EmptyLevel",
            "Lucy",
            "lucy_high",
            "macbeth_shaderballs",
            "MeshTest",
            "NormalMapping",
            "PbrMaterialChart",
            "ShadowTest",
            "Sponza",
            "SponzaDiffuseGI"
        ],
    )
    def test_LevelsLauncher(
        self, request, launcher, workspace, project, level, remote_console_instance
    ):
        expected_lines = []
        unexpected_lines = [
            "Trace::Assert",
            "Trace::Error",
            "Traceback (most recent call last):",
        ]

        hydra.launch_and_validate_results_launcher(
            launcher,
            level,
            remote_console_instance,
            expected_lines,
            unexpected_lines=unexpected_lines,
            log_monitor_timeout=log_monitor_timeout,
            halt_on_unexpected=True,
        )
