"""
Copyright (c) Contributors to the Open 3D Engine Project. For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT

Hydra script that is used to test the Decal (Atom) component functionality inside the Editor.
Opens the EmptyLevel level and creates a "Point light" entity and attaches a Point Light component.
Modifies the Opacity, Attenuation Angle, & Sort Key properties for the Point Light component.
Results are verified using log messages & screenshot comparisons diffed against golden images.

See the run() function for more in-depth test info.
"""

import os
import sys

import azlmbr.editor
import azlmbr.legacy.general as general
import azlmbr.paths
from azlmbr.entity import EntityId

sys.path.append(os.path.join(azlmbr.paths.devroot, "AtomTest", "Gem", "PythonTests"))

from Automated.atom_utils.automated_test_utils import TestHelper as helper
from Automated.atom_utils.hydra_editor_utils import helper_create_entity_with_mesh
from Automated.atom_utils.screenshot_utils import ScreenshotHelper


def run():
    """
    Test Case - Decal (Atom):
    1. Opens the "EmptyLevel" level and creates a new entity with a Mesh component and "objects/plane.azmodel" mesh.
    2. Creates a new "Point light" entity and attaches a Point Light component to it.
    3. Modifies each Decal property in CreateAngleAttenuationTestDecal(), CreateOpacityTestDecal(),
       CreateSortTestDecalTop(), & CreateSortTestDecalBottom().
    4. Specific properties modified on the Point Light component are Opacity, Attenuation Angle, & Sort Key.
    5. Enters game mode and takes a screenshot for comparison.
    6. Closes the Editor and the test ends.

    Tests will fail immediately if any of these log lines are found:
    1. Trace::Assert
    2. Trace::Error
    3. Traceback (most recent call last):

    :return: None
    """
    helper.init_idle()
    helper.open_level("EmptyLevel")

    CreatePlane()
    CreateLight()
    MoveCamera()
    CreateAngleAttenuationTestDecal()
    CreateOpacityTestDecal()
    CreateSortTestDecalTop()
    CreateSortTestDecalBottom()

    # generate screenshot and compare with golden
    ScreenshotHelper(general.idle_wait_frames).capture_screenshot_blocking_in_game_mode(
        'screenshot_atom_DecalComponent.ppm')
    helper.close_editor()


def SetEntityPosition(entity, x, y, z):
    position = azlmbr.math.Vector3(x, y, z)
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetWorldTranslation", entity, position)


def SetEntityScale(entity, scale):
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetLocalUniformScale", entity, scale)


def SetRotationX(entity, degrees):
    radians = degrees * 3.141927 / 180.0
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetRotationX", entity, radians)    


def SetDecalMaterial(decalComponent, filePath):
    decalAssetId = azlmbr.asset.AssetCatalogRequestBus(
        azlmbr.bus.Broadcast, 'GetAssetIdByPath', filePath, azlmbr.math.Uuid(), False)
    azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'SetComponentProperty', decalComponent, 'Controller|Configuration|Material', decalAssetId)


def SetComponentProperty(decalComponent, path, value):
    azlmbr.editor.EditorComponentAPIBus(azlmbr.bus.Broadcast, 'SetComponentProperty', decalComponent, path, value)


def CreateEntity(name):
    myEntityId = azlmbr.editor.ToolsApplicationRequestBus(azlmbr.bus.Broadcast, 'CreateNewEntity', EntityId())
    azlmbr.editor.EditorEntityAPIBus(azlmbr.bus.Event, 'SetName', myEntityId, name)
    return myEntityId


def CreateDecalComponentOnEntity(myEntityId):
    from Automated.atom_utils.automated_test_utils import TestHelper as helper
    decalComponent = helper.attach_component_to_entity(myEntityId, 'Decal (Atom)') 
    return decalComponent


def CreateSortTestDecalTop():
    myEntityId = CreateEntity('Airship Nose Number Decal')
    SetEntityPosition(myEntityId, 2.0, -2.0, 0.0)
    decalComponent = CreateDecalComponentOnEntity(myEntityId)

    SetDecalMaterial(decalComponent, 'materials/decal/airship_nose_number_decal.azmaterial')
    SetComponentProperty(decalComponent, 'Controller|Configuration|Opacity', 1.0)
    SetComponentProperty(decalComponent, 'Controller|Configuration|Attenuation Angle', 0.567)
    SetComponentProperty(decalComponent, 'Controller|Configuration|Sort Key', 0.0)
    return myEntityId


def CreateSortTestDecalBottom():
    myEntityId = CreateEntity('Airship Symbol Decal')
    SetEntityPosition(myEntityId, 2.0, -2.0, 0.0)
    decalComponent = CreateDecalComponentOnEntity(myEntityId)

    SetDecalMaterial(decalComponent, 'materials/decal/airship_symbol_decal.azmaterial')
    SetComponentProperty(decalComponent, 'Controller|Configuration|Opacity', 1.0)
    SetComponentProperty(decalComponent, 'Controller|Configuration|Attenuation Angle', 0.567)
    SetComponentProperty(decalComponent, 'Controller|Configuration|Sort Key', 255.0)
    return myEntityId


def CreateOpacityTestDecal():
    myEntityId = CreateEntity('Scorch Decal')
    SetEntityPosition(myEntityId, -2.0, 2.0, 0.0)
    decalComponent = CreateDecalComponentOnEntity(myEntityId)

    SetDecalMaterial(decalComponent, 'materials/decal/scorch_01_decal.azmaterial')
    SetComponentProperty(decalComponent, 'Controller|Configuration|Opacity', 0.5)
    SetComponentProperty(decalComponent, 'Controller|Configuration|Attenuation Angle', 0.0)
    SetComponentProperty(decalComponent, 'Controller|Configuration|Sort Key', 16.0)
    return myEntityId


def CreateAngleAttenuationTestDecal():
    myEntityId = CreateEntity('Airship Tail Decal')

    SetEntityPosition(myEntityId, 2.0, 2.0, 0.0)
    SetRotationX(myEntityId, 66.0)

    decalComponent = CreateDecalComponentOnEntity(myEntityId)

    SetDecalMaterial(decalComponent, 'materials/decal/airship_tail_01_decal.azmaterial')
    SetComponentProperty(decalComponent, 'Controller|Configuration|Opacity', 1.0)
    SetComponentProperty(decalComponent, 'Controller|Configuration|Attenuation Angle', 0.8)
    SetComponentProperty(decalComponent, 'Controller|Configuration|Sort Key', 12.0)
    return myEntityId


def CreatePlane():
    planeId = helper_create_entity_with_mesh('objects/plane.azmodel')
    SetEntityPosition(planeId, 0.0, 0.0, 0.0)
    SetEntityScale(planeId, 10.0)


def MoveCamera():
    cameraEntityId = helper.find_entities('Camera')[0]
    azlmbr.editor.EditorCameraRequestBus(
        azlmbr.bus.Broadcast, "SetViewAndMovementLockFromEntityPerspective", cameraEntityId, False)
    SetEntityPosition(cameraEntityId, 0.0, 0.0, 4.5)
    SetRotationX(cameraEntityId, -90.0)


def CreateLight():
    lightId = CreateEntity("Point light")
    SetEntityPosition(lightId, 0.0, 0.0, 2.0)
    SetRotationX(lightId, -90.0)
    typeIdsList = azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'FindComponentTypeIdsByEntityType', ["Point Light"], 0)
    componentOutcome = azlmbr.editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'AddComponentsOfType', lightId, typeIdsList)


if __name__ == "__main__":
    run()
