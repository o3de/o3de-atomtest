#
# All or portions of this file Copyright (c) Amazon.com, Inc. or its affiliates or
# its licensors.
#
# For complete copyright and license terms please see the LICENSE at the root of this
# distribution (the "License"). All use of this software is governed by the License,
# or, if provided, by the license below or the license accompanying this file. Do not
# remove or modify any license notices. This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#

ly_get_list_relative_pal_filename(pal_dir ${CMAKE_CURRENT_LIST_DIR}/Platform/${PAL_PLATFORM_NAME})

ly_add_target(
    NAME AtomTest ${PAL_TRAIT_MONOLITHIC_DRIVEN_MODULE_TYPE}
    NAMESPACE Gem
    FILES_CMAKE
        atomtest_files.cmake
        ../../atomtest_asset_files.cmake
    INCLUDE_DIRECTORIES
        PUBLIC
            Include
    BUILD_DEPENDENCIES
        PRIVATE
            AZ::AzGameFramework
            Gem::Atom_AtomBridge.Static
)

# if enabled, AtomTest gem is used by the Client and Server Launchers as well as Tools
# But it isn't needed in Builders
ly_create_alias(NAME AtomTest.Clients NAMESPACE Gem TARGETS Gem::AtomTest)
ly_create_alias(NAME AtomTest.Servers NAMESPACE Gem TARGETS Gem::AtomTest)
ly_create_alias(NAME AtomTest.Tools   NAMESPACE Gem TARGETS Gem::AtomTest)

################################################################################
# Gem dependencies
################################################################################
# The GameLauncher uses "Clients" gem variants:
ly_enable_gems(PROJECT_NAME AtomTest GEM_FILE enabled_gems.cmake
    TARGETS AtomTest.GameLauncher
    VARIANTS Clients)

# If we build a server, then apply the gems to the server
if(PAL_TRAIT_BUILD_SERVER_SUPPORTED)
    # if we're making a server, then add the "Server" gem variants to it:
    ly_enable_gems(PROJECT_NAME AtomTest GEM_FILE enabled_gems.cmake
        TARGETS AtomTest.ServerLauncher
        VARIANTS Servers)

    set_property(GLOBAL APPEND PROPERTY LY_LAUNCHER_SERVER_PROJECTS AtomTest)
endif()

if (PAL_TRAIT_BUILD_HOST_TOOLS)
    # The Editor uses "Tools" gem variants:
    ly_enable_gems(PROJECT_NAME AtomTest GEM_FILE enabled_gems.cmake
        TARGETS Editor
        VARIANTS Tools)


    # The pipeline tools use "Builders" gem variants:
    ly_enable_gems(PROJECT_NAME AtomTest GEM_FILE enabled_gems.cmake
        TARGETS AssetBuilder AssetProcessor AssetProcessorBatch
        VARIANTS Builders)
endif()
