"""
All or portions of this file Copyright (c) Amazon.com, Inc. or its affiliates or
its licensors.

For complete copyright and license terms please see the LICENSE at the root of this
distribution (the "License"). All use of this software is governed by the License,
or, if provided, by the license below or the license accompanying this file. Do not
remove or modify any license notices. This file is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

Hydra script that is used to test the AssetCollectionAsyncLoader class inside the Editor.
This class detects when assets have been processed and loads them in memory - all loading is done asynchronously.
If this test fails be sure to review asset logs for asset failures.

See the run() function for more in-depth test info.
There are also in-line comments for each function detailing specific interactions as well as docstrings.
"""

import os
import sys
import shutil
from functools import partial

import azlmbr.bus as bus
import azlmbr.editor as editor
import azlmbr.test as aztest
import azlmbr.legacy.general as general
import azlmbr.math as math
import azlmbr.paths
import azlmbr.asset as asset
from azlmbr.entity import EntityId

sys.path.append(os.path.join(azlmbr.paths.devroot, "AtomTest", "Gem", "PythonTests"))

from Automated.atom_utils.automated_test_utils import TestHelper as helper


def GetAssetsLists():
    """
    Returns a tuple that contains three lists
    1. The first list is TXT source assets list.
          File paths in this list end in ".txt" to avoid being processed.
          These assets come from the code repository.
    2. The second list is the TEMP source assets list. These represent
       temporary assets that will live for the duration of this test suite.
       The Asset Processor will be able to detect that these assets
       exist and will proceed to generate product assets from them.
    3. The third list is the products list.
    """
    srcNames = (
        ("ShaderBlendingOn.azsl.txt", "ShaderBlendingOn.azsl"),
        ("azshader-ShaderBlendingOn.shader.txt", "ShaderBlendingOn.shader"),
        ("streamingimage-checker8x8_512.png.txt", "checker8x8_512.png"),
        ("azmodel-cube_multimat_no_textures.fbx.txt", "cube_multimat_no_textures.fbx"),
        ("azmodel-cube.fbx.txt", "cube.fbx"),
    )
    productNames = (
        "ShaderBlendingOn.azshader",
        "checker8x8_512.png.streamingimage",
        "cube_multimat_no_textures.azmodel",
        "cube.azmodel",
    )
    gameRootPath = general.get_game_folder()
    srcTextFolder = os.path.normpath("Gem/PythonTests/Automated/TestData/AsyncAssetLoadTest") # Relative to gameRootPath
    dstSourceAssetFolder = os.path.normpath("TempData/AsyncAssetLoadTest") #relative to gameRootPath folder AND asset cache.
    
    sourceTxtList = []
    sourceTempList = []
    for sourceNameTxt, sourceName in srcNames:
        sourceTxtList.append(os.path.join(gameRootPath, srcTextFolder, sourceNameTxt))
        sourceTempList.append(os.path.join(gameRootPath, dstSourceAssetFolder, sourceName))
        
    productList = []
    for productName in productNames:
        productList.append(os.path.join(dstSourceAssetFolder, productName))
        
    return sourceTxtList, sourceTempList, productList


def CreateEntityWithComponent(entityName, componentClassName):
    """
    Creates an entity with the given name if it doesn't exist.
    Proceeds to attach a component with the given class name if not attached already to the entity.
    Returns the EntityId
    """
    #See if an entity with such name exists.
    entityList = helper.find_entities(entityName)
    if len(entityList) < 1:
        # Create new entity
        myEntityId = editor.ToolsApplicationRequestBus(bus.Broadcast, 'CreateNewEntity', EntityId())
        editor.EditorEntityAPIBus(bus.Event, 'SetName', myEntityId, entityName)
        if myEntityId.IsValid():
            general.log("Entity successfully created.")
        else:
            general.log(f"Failed to create entity with name {entityName}.")
            return None
    else:
        myEntityId = entityList[0]
        general.log(f"Found entity with name {entityName}.")
    
    # Add the component if not added already.
    if helper.attach_component_to_entity(myEntityId, componentClassName) is None:
        general.log(f"ERROR: Failed to add component [{componentClassName}] to entity named [{entityName}]")
        return None
    
    return myEntityId


def DeleteFilesInList(sourceTempList):
    for filePath in sourceTempList:
        try:
            os.remove(filePath)
        except:
            pass


def path_is_valid_asset(asset_path):
    asset_id = asset.AssetCatalogRequestBus(bus.Broadcast, "GetAssetIdByPath", asset_path, math.Uuid(), False)
    return asset_id.invoke("IsValid")


def areAllProductAssetsInvalid(assetList):
    """
    Returns true if all asset paths in @assetList are NOT valid assets.
    """
    for assetPath in assetList:
        if path_is_valid_asset(assetPath):
            return False
    return True


def WaitUntilProductAssetsAreRemoved(assetList, waitTimeSeconds = 30):
    """
    Given a list of asset paths, this function waits at most @waitTimeSeconds
    or returns earlier if none of those asset paths exist in the Asset Cache.
    """
    boundFunction = partial(areAllProductAssetsInvalid, assetList)
    return helper.wait_for_condition(boundFunction, waitTimeSeconds)


def CopyFile(srcPath, dstPath):
    dstDir = os.path.dirname(dstPath)
    if not os.path.isdir(dstDir):
        os.makedirs(dstDir)
    try:
        shutil.copyfile(srcPath, dstPath)
        return True
    except BaseException as error:
        general.log(f"ERROR: {error}")
        return False


def AllAssetsAreReadyPredicate(entityIdWithAsyncLoadTestComponent):
    """
    A predicate function what will be used in wait_for_condition.
    """
    pendingCount = aztest.AssetCollectionAsyncLoaderTestBus(bus.Event, "GetCountOfPendingAssets", entityIdWithAsyncLoadTestComponent)
    return pendingCount == 0


def run():
    # Define the source and product assets we will work with:
    sourceTxtList, sourceTempList, productList = GetAssetsLists()

    #Before we start we must delete the temporary source assets.
    DeleteFilesInList(sourceTempList)

    helper.init_idle()
    helper.open_level("EmptyLevel")

    myEntityId = CreateEntityWithComponent("TheAssetLoader", "AssetCollectionAsyncLoaderTest")
    if myEntityId is None:
        return

    if not WaitUntilProductAssetsAreRemoved(productList):
        general.log("ERROR: The AP did not removed the producs")
        return

    #Start with a clean slate, cancel any pending jobs.
    aztest.AssetCollectionAsyncLoaderTestBus(bus.Event, "CancelLoadingAssets", myEntityId)
    expectedEmptyList = aztest.AssetCollectionAsyncLoaderTestBus(bus.Event, "GetPendingAssetsList", myEntityId)
    if len(expectedEmptyList) != 0:
        general.log(f"ERROR: Was expecting 0 pending assets, instead got {len(expectedEmptyList)} pending assets")
        return

    # Let's submit a list of asset that don't exist yet, the AssetCollectionAsyncLoader should
    # accept and start a background job to load the assets. Because the assets don't exist in
    # the asset processor cache, the list of pending assets should be identical to the input list.
    if not aztest.AssetCollectionAsyncLoaderTestBus(bus.Event, "StartLoadingAssetsFromAssetList", myEntityId, productList):
        general.log(f"ERROR: Failed to submit assets for asynchronous loading. Tried to submit {len(productList)} assets for loading.")
        return
    general.log(f"SUCCESS: Assets were queued for loading. Total count: {len(productList)}")

    # Wait 1 second. In theory we could wait here forever, but for the sake of expedience 1 second is enough
    # to prove the point.
    general.idle_wait(1.0)

    # Because the input list has assets that will never exist, We expected the pending asset list to have the same
    # items as original asset list.
    pendingAssetList = aztest.AssetCollectionAsyncLoaderTestBus(bus.Event, "GetPendingAssetsList", myEntityId)
    if len(productList) != len(pendingAssetList):
        general.log(f"ERROR: Was expecting the same list size. original list size={len(productList)}, pending list size={len(pendingAssetList)}")
        return
    # Also make sure lists content are identical
    for assetPath in productList:
        if not assetPath in pendingAssetList:
            general.log(f"ERROR: Asset is not present in the pending list: {assetPath}")
            return
    general.log("SUCCESS: Pending list contains the same asset paths as the original list")

    # Expect error when tying to validate if a given asset was loaded.
    for assetPath in productList:
        if aztest.AssetCollectionAsyncLoaderTestBus(bus.Event, "ValidateAssetWasLoaded", myEntityId, assetPath):
            general.log(f"ERROR: Asset should not be available: {assetPath}")
            return
    general.log("SUCCESS: No asset was available")

    # Cancel the load operation and make sure there are no pending assets to load.
    aztest.AssetCollectionAsyncLoaderTestBus(bus.Event, "CancelLoadingAssets", myEntityId)
    expectedEmptyList = aztest.AssetCollectionAsyncLoaderTestBus(bus.Event, "GetPendingAssetsList", myEntityId)
    if len(expectedEmptyList) != 0:
        general.log(f"ERROR: Was expecting 0 pending assets, instead got {len(expectedEmptyList)} pending assets")
        return
    general.log("SUCCESS: Cancelled an impossible job")

    # Now we are going to create a request for the same assets as before,
    # But this time around the source assets will eventually exist.
    if not aztest.AssetCollectionAsyncLoaderTestBus(bus.Event, "StartLoadingAssetsFromAssetList", myEntityId, productList):
        general.log(f"ERROR: Failed to submit assets for asynchronous loading. Tried to submit {len(productList)} assets for loading.")
        return
    general.log(f"SUCCESS: Assets were queued for loading. Total count: {len(productList)}")

    #Let's create the source assets.
    for src, dst in zip(sourceTxtList, sourceTempList):
        if not CopyFile(src, dst):
            general.log(f"ERROR: Failed to copy temp source asset [{src}] as [{dst}]")
            return
    general.log("SUCCESS: created the temporary source assets. Waiting for assets to be processed...")
    boundFunction = partial(AllAssetsAreReadyPredicate, myEntityId)
    if not helper.wait_for_condition(boundFunction, 3600.0):
        general.log("ERROR: Failed to load assets asynchronously")
        return
    general.log("SUCCESS: The AssetCollectionAsyncLoader loaded all requested assets. One more final verification...")
    for assetPath in productList:
        if not aztest.AssetCollectionAsyncLoaderTestBus(bus.Event, "ValidateAssetWasLoaded", myEntityId, assetPath):
            general.log(f"ERROR: Asset should be available: {assetPath}")
            return
    general.log("SUCCESS: The AssetCollectionAsyncLoader PASSED the test")

    #Cleanup
    aztest.AssetCollectionAsyncLoaderTestBus(bus.Event, "CancelLoadingAssets", myEntityId)
    DeleteFilesInList(sourceTempList)


if __name__ == "__main__":
    run()
