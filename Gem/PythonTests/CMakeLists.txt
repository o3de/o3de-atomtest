#
# Copyright (c) Contributors to the Open 3D Engine Project
# 
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
#

################################################################################
# Automated Tests
################################################################################

if(PAL_TRAIT_BUILD_HOST_TOOLS AND PAL_TRAIT_BUILD_TESTS_SUPPORTED AND AtomTest IN_LIST LY_PROJECTS)
    ly_add_pytest(
        NAME AtomTest::HydraPythonTestsMain
        TEST_REQUIRES gpu
        TEST_SUITE main
        PATH ${CMAKE_CURRENT_LIST_DIR}/Automated/test_suites/main/
        TEST_SERIAL
        TIMEOUT 300
        RUNTIME_DEPENDENCIES
            AssetProcessor
            AtomTest
            AtomTest.Assets
            Editor
    )
    ly_add_pytest(
        NAME AtomTest::HydraPythonTestsPeriodic
        TEST_REQUIRES gpu
        TEST_SUITE periodic
        PATH ${CMAKE_CURRENT_LIST_DIR}/Automated/test_suites/periodic/
        TEST_SERIAL
        TIMEOUT 1200
        RUNTIME_DEPENDENCIES
            AssetProcessor
            AtomTest
            AtomTest.Assets
            AtomTest.GameLauncher
            Editor
    )
endif()
