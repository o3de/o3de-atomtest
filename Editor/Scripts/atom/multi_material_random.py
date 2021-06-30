"""
Copyright (c) Contributors to the Open 3D Engine Project. For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT
"""

import os
import sys
import logging
import azlmbr.atom
import azlmbr.math as math
import azlmbr.bus as bus
import azlmbr.editor
import azlmbr.object
import random
import glob
import material_helper as helper

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
logger = logging.getLogger(__name__)

# ToDo: make random material source configurable.
materials = glob.glob("C:/atom/dev/Cache/atomtest/pc/atomtest/substance/**/*.azmaterial", recursive=True)


def getRandomMaterial():
    material = random.choice(materials)
    assetId = azlmbr.asset.AssetCatalogRequestBus(azlmbr.bus.Broadcast, 'GetAssetIdByPath', material, math.Uuid(), False)
    return assetId


def assign_random_mat(_entity):
    _entityId = helper.get_entity_id(_entity)
    print(_entityId)
    _mat_assetIds = helper.get_mat_asset_id(_entity)
    print(helper.get_mat_names(_entity))
    addresses = azlmbr.editor.EditorMaterialComponentRequestBus(azlmbr.bus.Event, 'GetMaterialSlotAddresses', _entityId)
    for i, address in zip(range(len(addresses)), addresses):
        azlmbr.editor.EditorMaterialComponentRequestBus(azlmbr.bus.Event, 'SetMaterial', _entityId, address,
                                                        getRandomMaterial())


if __name__ == "__main__":
    entity_name = helper.get_selected_entity_name()
    print("\nYou have selected {}".format(entity_name))
    assign_random_mat(entity_name)

