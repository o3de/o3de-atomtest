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
# from azlmbr.editor import MaterialSlotAddress
from azlmbr.legacy import general as general
import material_helper as helper

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

_LOG_LONG_FRMT = "[%(name)s][%(levelname)s] >> %(message)s (%(asctime)s; %(filename)s:%(lineno)d)"
_LOG_SHRT_FRMT = '[%(name)s][%(levelname)s] >> %(message)s'

# set up logging to file - see previous section for more details
logging.basicConfig(level=logging.DEBUG,
                    format=_LOG_SHRT_FRMT,
                    datefmt='%m-%d %H:%M')

logging.info('Basic root logger set up')  # root logger

# this module logger
_MODULE = __name__
if _MODULE == '__main__':
    _MODULE = 'multi_material_stingray'

_LOGGER = logging.getLogger(_MODULE)


def assign_mat(_entity):
    _entityId = helper.get_entity_id(_entity)
    _LOGGER.info(str(_entityId))
    _mat_assetIds = helper.get_mat_asset_id(_entity, "objects/characters/peccy/")
    _LOGGER.info(str(helper.get_mat_names(_entity)))
    addresses = azlmbr.editor.EditorMaterialComponentRequestBus(azlmbr.bus.Event, 'GetMaterialSlotAddresses', _entityId)
    for i, address in zip(range(len(addresses)), addresses):
        azlmbr.editor.EditorMaterialComponentRequestBus(azlmbr.bus.Event, 'SetMaterial', _entityId, address,
                                                        _mat_assetIds[i])
        print_str = str('\n\t{0},\n\t{1}').format(_mat_assetIds[i], address.slotName)
        _LOGGER.info(print_str)


if __name__ == "__main__":
    # Assign material from selected entity
    entity_name = helper.get_selected_entity_name()
    _LOGGER.info("\nYou have selected {}".format(str(entity_name)))
    assign_mat(entity_name)
