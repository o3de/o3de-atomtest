"""
Copyright (c) Contributors to the Open 3D Engine Project. For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT

pytest config file for AtomTest
"""
import os


def pytest_addoption(parser):
    parser.addoption(
        "--open-beyond-compare", action="store_true", default=False,
        help="Open Beyond Compare screenshot comparison tool"
    )


def pytest_generate_tests(metafunc):
    if "open_beyond_compare" in metafunc.fixturenames:
        option_value = metafunc.config.getoption("open_beyond_compare")
        metafunc.parametrize("open_beyond_compare", [option_value])
    if 'golden_images_directory' in metafunc.fixturenames:
        metafunc.parametrize('golden_images_directory', [golden_images_directory()])


def golden_images_directory():
    """
    Uses this conftest.py file location to return the valid location for golden image files.
    :return: The path to the GoldenImages directory, but raises an IOError if the GoldenImages directory is missing.
    """
    golden_images_dir = os.path.join(os.path.dirname(__file__), 'GoldenImages')

    if not os.path.exists(golden_images_dir):
        raise IOError(
            f'AtomTest "GoldenImages" directory was not found at path "{golden_images_dir}"'
            'Please add a "GoldenImages" directory wih golden images for screenshot comparison tests.'
        )

    return golden_images_dir
