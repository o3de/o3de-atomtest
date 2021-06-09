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
import logging
import subprocess
import time

import pytest

import ly_test_tools.log.log_monitor as log_monitor

SIMILARITY_THRESHOLD = 0.99
DEFAULT_SUBFOLDER_PATH = 'user/PythonTests/Automated/Screenshots'
logger = logging.getLogger(__name__)


@pytest.mark.usefixtures('automatic_process_killer')
class TestAutomationBase:
    """
    Base class for writing automated tests for Atom.
    Various useful helper methods go here.
    """

    @pytest.fixture(autouse=True)
    def fixture_open_beyond_compare(self, open_beyond_compare):
        self.enable_open_beyond_compare = open_beyond_compare

    def _run_test(self, request, workspace, editor, testcase_module, expected_lines, unexpected_lines, extra_cmdline_args=[]):
        def teardown():
            editor.ensure_stopped()

        request.addfinalizer(teardown)

        for name in testcase_module.Tests.__dict__:
            value = testcase_module.Tests.__dict__[name]
            if not name.startswith("_") and type(value) == tuple:
                expected_lines.append("Success: %s" % value[0])
                unexpected_lines.append("Failure: %s" % value[1])
        logger.debug("Running automated test")
        testscase_module_filepath = self._get_testcase_module_filepath(testcase_module)
        pycmd = ["-exec_line", "pyRunFile %s" % testscase_module_filepath, "-autotest_mode"] + extra_cmdline_args
        # args are added to the WinLauncher launch command
        editor.args.extend(pycmd)
        editor.start()
        assert editor.is_alive(), "Editor failed to launch for the current Lumberyard build."
        editorlog_file = os.path.join(workspace.paths.project_log(), "Editor.log")
        time.sleep(5)
        new_log_monitor = log_monitor.LogMonitor(editor, editorlog_file)
        new_log_monitor.monitor_log_for_lines(expected_lines, unexpected_lines)
        editor.stop()

    def _get_project_path(self, workspace):
        """
        return the full path of the project in this workspace
        """
        return os.path.join(workspace.paths.engine_root(), workspace.project)

    def _capture_screenshot(self):
        """
        Captures a screenshot from Atom
        """
        import azlmbr.bus
        import azlmbr.atom
        azlmbr.atom.AtomScreenshotRequestBus(azlmbr.bus.Broadcast, 'CaptureScreenshot')

    def _get_testcase_module_filepath(self, testcase_module):
        """
        return the full path of the test module
        """
        return os.path.splitext(testcase_module.__file__)[0] + ".py"

    def remove_artifacts(self, artifact_filepaths):
        for artifact in artifact_filepaths:
            if os.path.isfile(artifact):
                os.remove(artifact)

    def delete_level(self, workspace, level_dir, timeout=120):
        """
        Attempts to delete an entire level folder from the project.
        :param workspace: The workspace instance to delete the level from.
        :param level_dir: The level folder to delete
        """
        logger = logging.getLogger(__name__)

        if (not level_dir):
            logger.warning("level_dir is empty, nothing to delete.")
            return

        full_level_dir = os.path.join(self._get_project_path(workspace), 'Levels', level_dir)
        if (not os.path.isdir(full_level_dir)):
            if (os.path.exists(full_level_dir)):
                logger.error("level '{}' isn't a directory, it won't be deleted.".format(full_level_dir))
            else:
                logger.info("level '{}' doesn't exist, nothing to delete.".format(full_level_dir))
            return

        import shutil
        try:
            shutil.rmtree(full_level_dir)
        except OSError as e:
            logger.debug("Delete for '{}' failed: {}".format(full_level_dir, e))

    def open_beyond_compare(self, left_screenshot, right_screenshot):
        try:
            subprocess.Popen(["bcompare", left_screenshot, right_screenshot])
        except FileNotFoundError as err:
            return str(err)

    def compare_screenshots(self, test_screenshot, golden_screenshot):
        import ly_test_tools.image.screenshot_compare_qssim as screenshot_compare
        
        assert os.path.isfile(test_screenshot), f"test screenshot {test_screenshot} was not found, did the test run?"
        # compare test screenshot with the golden screenshot
        try:
            similarity = screenshot_compare.qssim(golden_screenshot, test_screenshot)
        except ValueError as err:
            raise ValueError(f"Resolutions of screenshots are incompatible. Try setting your display scaling to 100%: {str(err)}") from err
            
        logger.info("----- Screenshot Result -----")
        logger.info("    Expected Screenshot: '{}'".format(golden_screenshot))
        logger.info("        Test Screenshot: '{}'".format(test_screenshot))
        logger.info("                  Score: '{}'".format(similarity))

        if similarity < SIMILARITY_THRESHOLD:
            res = None
            if self.enable_open_beyond_compare:
                res = self.open_beyond_compare(test_screenshot, golden_screenshot)
            exception_msg = f"Screenshot similarity = {similarity}, below the threshold of {SIMILARITY_THRESHOLD}.\n"  \
                            f"Test Screenshot Filepath: {test_screenshot}\n"                                           \
                            f"Golden Screenshot Filepath: {golden_screenshot}\n\n"                                     \
                            f"NOTE: HDR-enabled monitors are currently not supported. Please disable HDR first.\n"
            if res:
                exception_msg += "\nAttempted to run Beyond Compare but no executable was found. Try adding it to your path."
            raise Exception(exception_msg)
        print("Screenshots match")