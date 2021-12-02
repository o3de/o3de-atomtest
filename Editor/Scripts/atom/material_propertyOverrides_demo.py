"""
Copyright (c) Contributors to the Open 3D Engine Project.
For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import azlmbr.atom
import azlmbr.math as math
import azlmbr.asset as asset
import azlmbr.bus as bus
import azlmbr.editor
import azlmbr.math as math
import random

from azlmbr.entity import EntityId
from azlmbr.editor import MaterialSlotAddress
from azlmbr.name import Name

materials = [   'materials/pbr1.azmaterial',
                'materials/pbr2.azmaterial',
                'materials/pbr3.azmaterial',
                'materials/pbr4.azmaterial',
                'materials/pbr5.azmaterial',
                'materials/pbr6.azmaterial']

textures = [    'ObjectIcons/elevator.bmp',
                'ObjectIcons/Particles.bmp',
                'ObjectIcons/bug.bmp',
                'ObjectIcons/Clouds.bmp',
                'ObjectIcons/Fish.bmp',
                'ObjectIcons/character.bmp']


def getRandomMaterial():
    material = random.choice(materials)
    assetId = azlmbr.asset.AssetCatalogRequestBus(azlmbr.bus.Broadcast, 'GetAssetIdByPath', material, math.Uuid(), False)
    return assetId

def assetIdToPath(assetId):
    assetPath = azlmbr.asset.AssetCatalogRequestBus(azlmbr.bus.Broadcast, 'GetAssetPathById', assetId)
    return assetPath

# List all slot addresses
def getAddresses(entityId):
    print("Get slot addresses")
    return azlmbr.editor.EditorMaterialComponentRequestBus(azlmbr.bus.Event, 'GetMaterialSlotAddresses', entityId)

def printMaterials(entityId):
    materials = azlmbr.editor.EditorMaterialComponentRequestBus(azlmbr.bus.Event, 'GetMaterials', entityId)
    print(f"Materials: {[(materialPair[0].ToString(), assetIdToPath(materialPair[1])) for materialPair in materials.items()]}")

def setMaterialOverrides(entityId, addresses):
    print("Setting material overrides")
    for address in addresses:
        azlmbr.editor.EditorMaterialComponentRequestBus(azlmbr.bus.Event, 'SetMaterial', entityId, address, getRandomMaterial())

# Sets overrides of 3 types: float, color, and texture
def setPropertyOverrides(entityId, addresses):
    print("Setting property overrides")
    for address in addresses:
        # factor override (float)
        factor = random.random()
        propertyName = Name("baseColor.factor")
        azlmbr.editor.EditorMaterialComponentRequestBus(azlmbr.bus.Event, 'SetPropertyOverride',
                                                        entityId, address, propertyName, factor)
        # color override
        color = math.Color(random.random(), random.random(), random.random(), 1.0)
        propertyName = Name("baseColor.color")
        azlmbr.editor.EditorMaterialComponentRequestBus(azlmbr.bus.Event, 'SetPropertyOverride',
                                                        entityId, address, propertyName, color)

        # texture override
        texturePath = random.choice(textures)
        assetId = azlmbr.asset.AssetCatalogRequestBus(azlmbr.bus.Broadcast, 'GetAssetIdByPath', texturePath, math.Uuid(), False)
        propertyName = Name("baseColor.textureMap")
        azlmbr.editor.EditorMaterialComponentRequestBus(azlmbr.bus.Event, 'SetPropertyOverride',
                                                        entityId, address, propertyName, texturePath)
# Convert property value to string
def propertyValueToString(value):
    if isinstance(value, (int, float, bool, str)):
        return value
    if value.typename == 'Color':
        return 'Color(r={:.2f}, g={:.2f}, b={:.2f}, a={:.2f})'.format(value.r, value.g, value.b, value.a)
    if value.typename == 'ImageBinding':
        return assetIdToPath(value.GetAssetId())
    return value

# print all property overrides on a material component
def printPropertyOverrides(entityId):
    print("Property overrides:")
    propertyOverrides = azlmbr.editor.EditorMaterialComponentRequestBus(azlmbr.bus.Event, 'GetPropertyOverrides', entityId)
    for address in propertyOverrides:
        print(f'{address.ToString()}:')
        propertyOverridesForAddress = propertyOverrides[address]
        print(f"{[(propertyPair[0].ToString(), propertyValueToString(propertyPair[1])) for propertyPair in propertyOverridesForAddress.items()]}")

# Clear property overrides for a single slot
def clearPropertyOverrides(entityId, address):
    print(f"Clearing property overrides for slot <{address.ToString()}>")
    azlmbr.editor.EditorMaterialComponentRequestBus(azlmbr.bus.Event, 'ClearPropertyOverrides', entityId, address)

# Clear all property overrides for the material
def clearAllPropertyOverrides(entityId):
    print("Clearing remaining property overrides")
    azlmbr.editor.EditorMaterialComponentRequestBus(azlmbr.bus.Event, 'ClearAllPropertyOverrides', entityId)

def run():
    searchFilter = azlmbr.entity.SearchFilter()
    searchFilter.names = ["Entity1"]
    matching_entities = azlmbr.entity.SearchBus(bus.Broadcast, 'SearchEntities', searchFilter)
    if matching_entities == 0:
        print('Could not find entity')
        return

    entityId = matching_entities[0]

    # Get addresses
    addresses = getAddresses(entityId)
    print(f"Slots: {[address.ToString() for address in addresses]}")

    # Print current materials
    printMaterials(entityId)

    # Set material overrides
    setMaterialOverrides(entityId, addresses)

    # Print current materials
    printMaterials(entityId)

    # Set property overrides
    setPropertyOverrides(entityId, addresses)

    # Print current property overrides
    printPropertyOverrides(entityId)

    # Clear property overrides for first slot
    clearPropertyOverrides(entityId, addresses[0])

    # Print current property overrides
    printPropertyOverrides(entityId)

    # Clear remaining property overrides
    clearAllPropertyOverrides(entityId)

    # Print current property overrides
    printPropertyOverrides(entityId)

if __name__ == "__main__":
    run()
