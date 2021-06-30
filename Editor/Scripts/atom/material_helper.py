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
from pathlib import Path
# from azlmbr.editor import MaterialSlotAddress
from azlmbr.legacy import general as general

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------------
def returnStubDir(stub, start_path):
    _DIRtoLastFile = None
    '''Take a file name (stub) and returns the directory of the file (stub)'''
    if _DIRtoLastFile is None:
        path = os.path.abspath(start_path)
        while 1:
            path, tail = os.path.split(path)
            if (os.path.isfile(os.path.join(path, stub))):
                break
            if (len(tail) == 0):
                path = ""
                if _G_DEBUG:
                    print('~ Debug Message:  I was not able to find the '
                          'path to that file (stub) in a walk-up from currnet path')
                break
        _DIRtoLastFile = path

    return _DIRtoLastFile
# --------------------------------------------------------------------------

_DEV_ROOT = Path(returnStubDir('engineroot.txt', __file__)).resolve()  # hopefully safe
_REL_ROOT = Path(_DEV_ROOT, 'AtomTest').resolve()

def get_entity_id(_entity):
    searchFilter = azlmbr.entity.SearchFilter()
    searchFilter.names = [_entity]
    matching_entities = azlmbr.entity.SearchBus(bus.Broadcast, 'SearchEntities', searchFilter)
    # print("This is entity id from searchFilter: {}".format(matching_entities[0]))
    return matching_entities[0]


def get_selected_entity_id():
    selected_entity_id = azlmbr.editor.ToolsApplicationRequestBus(azlmbr.bus.Broadcast, "GetSelectedEntities")
    # print("This is entity id from selected entity: {}".format(selected_entity_id[0]))
    return selected_entity_id[0]


def get_selected_entity_name():
    # Get entity name from selected entity
    entity_name = general.get_names_of_selected_objects()
    return entity_name[0]


def get_mat_names(_entity):
    _entityId = get_entity_id(_entity)
    # Get material names
    material_names = []
    mat_addresses = azlmbr.editor.EditorMaterialComponentRequestBus(azlmbr.bus.Event, 'GetMaterialSlotAddresses', _entityId)
    for mat_address in mat_addresses:
        mat_name = mat_address.slotName
        material_names.append(mat_name)
    return material_names


def get_mat_asset_id(_entity, material_dir_path):
    # Get all material asset path.
    _materials = get_mat_names(_entity)
    _mat_assets = []
    for _mat_asset in range(len(_materials)):
        _mat_path = material_dir_path + _materials[_mat_asset] + ".azmaterial"
        _mat_assets.append(_mat_path)

    assetIds = []
    for i in range(len(_materials)):
        _assetId = azlmbr.asset.AssetCatalogRequestBus(azlmbr.bus.Broadcast, 'GetAssetIdByPath', _mat_assets[i],
                                                       math.Uuid(), False)
        assetIds.append(_assetId)
    return assetIds
