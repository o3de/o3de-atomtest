"""
Copyright (c) Contributors to the Open 3D Engine Project.
For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT
"""
import collections.abc
import os
from typing import List
from math import isclose

import azlmbr.bus as bus
import azlmbr.editor as editor
import azlmbr.entity as entity
import azlmbr.legacy.general as general
import azlmbr.math as math
import azlmbr.asset as asset
import azlmbr.camera as camera
import azlmbr.object
from azlmbr.entity import EntityType

from Automated.atom_utils.automated_test_utils import TestHelper as helper
from Automated.atom_utils.screenshot_utils import ScreenshotHelper


def find_entity_by_name(entity_name):
    """
    Gets an entity ID from the entity with the given entity_name
    :param entity_name: String of entity name to search for
    :return entity ID
    """
    search_filter = entity.SearchFilter()
    search_filter.names = [entity_name]
    matching_entity_list = entity.SearchBus(bus.Broadcast, "SearchEntities", search_filter)
    if matching_entity_list:
        matching_entity = matching_entity_list[0]
        if matching_entity.IsValid():
            print(f"{entity_name} entity found with ID {matching_entity.ToString()}")
            return matching_entity
    else:
        return matching_entity_list


def get_component_type_id(component_name, entity_type=entity.EntityType().Game):
    """
    Gets the component_type_id from a given component name
    :param component_name: String of component name to search for
    :return component type ID
    """
    type_ids_list = editor.EditorComponentAPIBus(bus.Broadcast, "FindComponentTypeIdsByEntityType", [component_name], entity_type)
    component_type_id = type_ids_list[0]
    return component_type_id


def add_level_component(component_name):
    """
    Adds the specified component to the Level Inspector
    :param component_name: String of component name to search for
    :return Component object.
    """
    level_component_list = [component_name]
    level_component_type_ids_list = editor.EditorComponentAPIBus(
        bus.Broadcast, "FindComponentTypeIdsByEntityType", level_component_list, EntityType().Level
    )
    level_component_outcome = editor.EditorLevelComponentAPIBus(
        bus.Broadcast, "AddComponentsOfType", [level_component_type_ids_list[0]]
    )
    level_component = level_component_outcome.GetValue()[0]
    return level_component


def add_component(componentName, entityId, entity_type=entity.EntityType().Game):
    """
    Given a component name, finds component TypeId, adds to given entity, and verifies successful add/active state.
    :param componentName: String of component name to add.
    :param entityId: Entity to add component to.
    :return: Component object.
    """
    typeIdsList = editor.EditorComponentAPIBus(bus.Broadcast, "FindComponentTypeIdsByEntityType", [componentName], entity_type)
    typeNamesList = editor.EditorComponentAPIBus(bus.Broadcast, "FindComponentTypeNames", typeIdsList)
    componentOutcome = editor.EditorComponentAPIBus(bus.Broadcast, "AddComponentsOfType", entityId, typeIdsList)
    isActive = editor.EditorComponentAPIBus(bus.Broadcast, "IsComponentEnabled", componentOutcome.GetValue()[0])
    hasComponent = editor.EditorComponentAPIBus(bus.Broadcast, "HasComponentOfType", entityId, typeIdsList[0])
    if componentOutcome.IsSuccess() and isActive:
        print("{} component was added to entity".format(typeNamesList[0]))
    elif componentOutcome.IsSuccess() and not isActive:
        print("{} component was added to entity, but the component is disabled".format(typeNamesList[0]))
    elif not componentOutcome.IsSuccess():
        print("Failed to add {} component to entity".format(typeNamesList[0]))
    if hasComponent:
        print("Entity has a {} component".format(typeNamesList[0]))
    return componentOutcome.GetValue()[0]


def remove_component(component_name, entity_id):
    """
    Removes the specified component from the specified entity.
    :param component_name: String of component name to remove.
    :param entity_id: Entity to remove component from.
    :return: EntityComponentIdPair if removal was successful, else None.
    """
    type_ids_list = [get_component_type_id(component_name)]
    outcome = editor.EditorComponentAPIBus(bus.Broadcast, "GetComponentOfType", entity_id, type_ids_list[0])
    if outcome.IsSuccess():
        component_entity_pair = outcome.GetValue()
        editor.EditorComponentAPIBus(bus.Broadcast, "RemoveComponents", [component_entity_pair])
        has_component = editor.EditorComponentAPIBus(bus.Broadcast, "HasComponentOfType", entity_id, type_ids_list[0])
        if has_component:
            print(f"Failed to remove {component_name}")
            return None
        else:
            print(f"{component_name} was successfully removed")
            return component_entity_pair
    else:
        print(f"{component_name} not found on entity")
        return None


def get_component_property_value(component, component_propertyPath):
    """
    Given a component name and component property path, outputs the property's value.
    :param component: Component object to act on.
    :param component_propertyPath: String of component property. (e.g. 'Settings|Visible')
    :return: Value set in given componentPropertyPath
    """
    componentPropertyObj = editor.EditorComponentAPIBus(
        bus.Broadcast, "GetComponentProperty", component, component_propertyPath
    )
    if componentPropertyObj.IsSuccess():
        componentProperty = componentPropertyObj.GetValue()
        print(f"{component_propertyPath} set to {componentProperty}")
        return componentProperty
    else:
        print(f"FAILURE: Could not get value from {component_propertyPath}")
        return None


def get_property_tree(component):
    """
    Given a configured component object, prints the property tree info from that component
    :param component: Component object to act on.
    """
    pteObj = editor.EditorComponentAPIBus(bus.Broadcast, "BuildComponentPropertyTreeEditor", component)
    pte = pteObj.GetValue()
    print(pte.build_paths_list())
    return pte


def compare_values(first_object: object, second_object: object, name: str) -> bool:
    # Quick case - can we just directly compare the two objects successfully?
    if first_object == second_object:
        result = True
    # No, so get a lot more specific
    elif isinstance(first_object, collections.abc.Container):
        # If they aren't both containers, they're different
        if not isinstance(second_object, collections.abc.Container):
            result = False
        # If they have different lengths, they're different
        elif len(first_object) != len(second_object):
            result = False
        # If they're different strings, they're containers but they failed the == check so
        # we know they're different
        elif isinstance(first_object, str):
            result = False
        else:
            # It's a collection of values, so iterate through them all...
            collection_idx = 0
            result = True
            for val1, val2 in zip(first_object, second_object):
                result = result and compare_values(val1, val2, f"{name} (index [{collection_idx}])")
                collection_idx = collection_idx + 1

    else:
        # Do approximate comparisons for floats
        if isinstance(first_object, float) and isclose(first_object, second_object, rel_tol=0.001):
            result = True
        # We currently don't have a generic way to compare PythonProxyObject contents, so return a
        # false positive result for now.
        elif isinstance(first_object, azlmbr.object.PythonProxyObject):
            print(f"{name}: validation inconclusive, the two objects cannot be directly compared.")
            result = True
        else:
            result = False

    if not result:
        print(
            f"compare_values failed: {first_object} ({type(first_object)}) vs {second_object} ({type(second_object)})"
        )

    print(f"{name}: {'SUCCESS' if result else 'FAILURE'}")
    return result


class Entity:
    """
    Entity class used to create entity objects
    :param name: String for the name of the Entity
    :param id: The ID of the entity
    """

    def __init__(self, name: str, id: object = entity.EntityId()):
        self.name: str = name
        self.id: object = id
        self.components: List[object] = None
        self.parent_id = None
        self.parent_name = None

    def create_entity(self, entity_position=None, components=[], parent_id=entity.EntityId()):
        if entity_position is None:
            self.id = editor.ToolsApplicationRequestBus(bus.Broadcast, 'CreateNewEntity', parent_id)
        else:
            self.id = editor.ToolsApplicationRequestBus(
                bus.Broadcast, "CreateNewEntityAtPosition", entity_position, parent_id
            )
        if self.id.IsValid():
            print(f"{self.name} Entity successfully created")
            editor.EditorEntityAPIBus(bus.Event, "SetName", self.id, self.name)
            self.components = []
            for component in components:
                self.add_component(component)

    def add_component(self, component):
        new_component = add_component(component, self.id)
        self.components.append(new_component)

    def remove_component(self, component):
        removed_component = remove_component(component, self.id)
        if removed_component is not None:
            self.components.remove(removed_component)

    def get_parent_info(self):
        """
        Sets the value for parent_id and parent_name on the entity (self)
        Prints the string for papertrail
        :return: None
        """
        self.parent_id = editor.EditorEntityInfoRequestBus(bus.Event, "GetParent", self.id)
        self.parent_name = editor.EditorEntityInfoRequestBus(bus.Event, "GetName", self.parent_id)
        print(f"The parent entity of {self.name} is {self.parent_name}")

    def set_test_parent_entity(self, parent_entity_obj):
        editor.EditorEntityAPIBus(bus.Event, "SetParent", self.id, parent_entity_obj.id)
        self.get_parent_info()

    def get_set_test(self, component_index: int, path: str, value: object, expected_result: object = None) -> bool:
        """
        Used to set and validate changes in component values
        :param component_index: Index location in the self.components list
        :param path: asset path in the component
        :param value: new value for the variable being changed in the component
        :param expected_result: (optional) check the result against a specific expected value
        """

        if expected_result is None:
            expected_result = value

        # Test Get/Set (get old value, set new value, check that new value was set correctly)
        print(f"Entity {self.name} Path {path} Component Index {component_index} ")

        component = self.components[component_index]
        old_value = get_component_property_value(component, path)

        if old_value is not None:
            print(f"SUCCESS: Retrieved property Value for {self.name}")
        else:
            print(f"FAILURE: Failed to find value in {self.name} {path}")
            return False

        if old_value == expected_result:
            print(
                (
                    f"WARNING: get_set_test on {self.name} is setting the same value that already exists ({old_value})."
                    "The set results will be inconclusive."
                )
            )

        editor.EditorComponentAPIBus(bus.Broadcast, "SetComponentProperty", component, path, value)

        new_value = get_component_property_value(self.components[component_index], path)

        if new_value is not None:
            print(f"SUCCESS: Retrieved new property Value for {self.name}")
        else:
            print(f"FAILURE: Failed to find new value in {self.name}")
            return False

        return compare_values(new_value, expected_result, f"{self.name} {path}")


def get_set_test(entity: object, component_index: int, path: str, value: object) -> bool:
    """
    Used to set and validate changes in component values
    :param component_index: Index location in the entity.components list
    :param path: asset path in the component
    :param value: new value for the variable being changed in the component
    """
    return entity.get_set_test(component_index, path, value)


def get_set_property_test(
    ly_object: object, attribute_name: str, value: object, expected_result: object = None
) -> bool:
    """
    Used to set and validate BehaviorContext property changes in Lumberyard objects
    :param ly_object: The lumberyard object to test
    :param attribute_name: property (attribute) name in the BehaviorContext
    :param value: new value for the variable being changed in the component
    :param expected_result: (optional) check the result against a specific expected value other than the one set
    """

    if expected_result is None:
        expected_result = value

    # Test Get/Set (get old value, set new value, check that new value was set correctly)
    print(f"Attempting to set {ly_object.typename}.{attribute_name} = {value} (expected result is {expected_result})")

    if hasattr(ly_object, attribute_name):
        print(f"SUCCESS: Located attribute {attribute_name} for {ly_object.typename}")
    else:
        print(f"FAILURE: Failed to find attribute {attribute_name} in {ly_object.typename}")
        return False

    old_value = getattr(ly_object, attribute_name)

    if old_value is not None:
        print(f"SUCCESS: Retrieved existing value {old_value} for {attribute_name} in {ly_object.typename}")
    else:
        print(f"FAILURE: Failed to retrieve value for {attribute_name} in {ly_object.typename}")
        return False

    if old_value == expected_result:
        print(
            (
                f"WARNING: get_set_test on {attribute_name} is setting the same value that already exists ({old_value})."
                "The 'set' result for the test will be inconclusive."
            )
        )

    setattr(ly_object, attribute_name, expected_result)

    new_value = getattr(ly_object, attribute_name)

    if new_value is not None:
        print(f"SUCCESS: Retrieved new value {new_value} for {attribute_name} in {ly_object.typename}")
    else:
        print(f"FAILURE: Failed to retrieve value for {attribute_name} in {ly_object.typename}")
        return False

    return compare_values(new_value, expected_result, f"{ly_object.typename}.{attribute_name}")


def has_components(entity_id: object, component_list: list) -> bool:
    """
    Used to verify if a given entity has all the components of components_list. Returns True if all the
    components are present, else False
    :param entity_id: entity id of the entity
    :param component_list: list of component names to be verified
    """
    type_ids_list = editor.EditorComponentAPIBus(bus.Broadcast, "FindComponentTypeIdsByEntityType", component_list, entity.EntityType().Game)
    for type_id in type_ids_list:
        if not editor.EditorComponentAPIBus(bus.Broadcast, "HasComponentOfType", entity_id, type_id):
            return False
    return True

def is_component_enabled(entity_componentid_pair):
    return editor.EditorComponentAPIBus(bus.Broadcast, "IsComponentEnabled", entity_componentid_pair)


def set_visibility_state(entity_id, visibility_state):
    editor.EditorEntityAPIBus(bus.Event, "SetVisibilityState", entity_id, visibility_state)


def is_entity_hidden(entity_id):
    return editor.EditorEntityInfoRequestBus(bus.Event, "IsHidden", entity_id)


def delete_entity(entity_id):
    editor.ToolsApplicationRequestBus(bus.Broadcast, "DeleteEntityById", entity_id)


def get_asset_by_path(path):
    return asset.AssetCatalogRequestBus(bus.Broadcast, "GetAssetIdByPath", path, math.Uuid(), False)


def delete_all_existing_entities():
    search_filter = azlmbr.entity.SearchFilter()
    all_entities = entity.SearchBus(azlmbr.bus.Broadcast, "SearchEntities", search_filter)
    editor.ToolsApplicationRequestBus(bus.Broadcast, "DeleteEntities", all_entities)


def disable_component(component):
    editor.EditorComponentAPIBus(bus.Broadcast, "DisableComponents", [component])


# Be this camera
def be_this_camera(camera_entity_id):
    camera.EditorCameraViewRequestBus(azlmbr.bus.Event, "ToggleCameraAsActiveView", camera_entity_id)


def set_component_property(component, property_path, property_value):
    """
    Given a component returned by 'GetComponentOfType', update its property_path value to property_value
    :param component: The component to target in the Editor to set a property for
    :param property_path: path to the property to set in the component
    :param property_value: the value to set the property to in the property_path
    :return: None
    """
    editor.EditorComponentAPIBus(azlmbr.bus.Broadcast, 'SetComponentProperty', component, property_path, property_value)


class PathNotFoundError(Exception):
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return f'Path "{self.path}" not found in Editor Settings'


def get_editor_settings_path_list():
    """
    Get the list of Editor Settings paths
    """
    paths = editor.EditorSettingsAPIBus(bus.Broadcast, "BuildSettingsList")
    return paths


def get_editor_settings_by_path(path):
    """
    Get the value of Editor Settings based on the path.
    :param path: path to the Editor Settings to get the value
    """
    if path not in get_editor_settings_path_list():
        raise PathNotFoundError(path)
    outcome = editor.EditorSettingsAPIBus(bus.Broadcast, "GetValue", path)
    if outcome.isSuccess():
        return outcome.GetValue()
    raise RuntimeError(f"GetValue for path '{path}' failed")


def set_editor_settings_by_path(path, value, is_bool=False):
    """
    Set the value of Editor Settings based on the path.
    # NOTE: Some Editor Settings may need an Editor restart to apply.
    # Ex: Enabling or disabling New Viewport Interaction Model
    :param path: path to the Editor Settings to get the value
    :param value: value to be set
    :param is_bool: True for Boolean settings (enable/disable), False for other settings
    """
    if path not in get_editor_settings_path_list():
        raise PathNotFoundError(path)
    if is_bool and not isinstance(value, bool):

        def ParseBoolValue(value):
            if value == "0":
                return False
            return True

        value = ParseBoolValue(value)
    outcome = editor.EditorSettingsAPIBus(bus.Broadcast, "SetValue", path, value)
    if not outcome.isSuccess():
        raise RuntimeError(f"SetValue for path '{path}' failed")
    print(f"Value for path '{path}' is set to {value}")


def get_component_type_id_map(component_name_list):
    """
    Given a list of component names, returns a map of component name -> component type id
    :param component_name_list: The lumberyard object to test
    :return: Dictionary of component name -> component type id pairs
    """
    # Remove any duplicates so we don't have to query for the same TypeId
    component_names = list(set(component_name_list))

    type_ids_by_component = {}
    type_ids = editor.EditorComponentAPIBus(bus.Broadcast, "FindComponentTypeIdsByEntityType", component_names, entity.EntityType().Game)
    for i, typeId in enumerate(type_ids):
        type_ids_by_component[component_names[i]] = typeId

    return type_ids_by_component


def helper_create_entity_with_mesh(path_to_mesh, offset=azlmbr.math.Vector3(0.0,0.0,0.0), entity_name='NewEntity'):
    # Create a new Entity at the root level
    myEntityId = editor.ToolsApplicationRequestBus(azlmbr.bus.Broadcast, 'CreateNewEntity', entity.EntityId())
    editor.EditorEntityAPIBus(azlmbr.bus.Event, 'SetName', myEntityId, entity_name)

    vec3 = azlmbr.components.TransformBus(azlmbr.bus.Event, "GetWorldTranslation", myEntityId)
    vec3.x += offset.x
    vec3.y += offset.y
    vec3.z += offset.z
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetWorldTranslation", myEntityId, vec3)

    # Get Component Types for Atom's Mesh
    typeIdsList = [ azlmbr.globals.property.EditorMeshComponentTypeId ]

    # add a Mesh component to the entity
    componentOutcome = editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'AddComponentsOfType', myEntityId, typeIdsList)

    # save a reference to the component
    components = componentOutcome.GetValue()
    component = components[0]

    # an example of checking if the component is there or not
    hasComponent = editor.EditorComponentAPIBus(azlmbr.bus.Broadcast, 'HasComponentOfType', myEntityId, typeIdsList[0])

    meshId = asset.AssetCatalogRequestBus(bus.Broadcast, 'GetAssetIdByPath', path_to_mesh, math.Uuid(), False)

    # set mesh asset
    mesh_property_path = 'Controller|Configuration|Mesh Asset'
    newObj = editor.EditorComponentAPIBus(
        azlmbr.bus.Broadcast, 'SetComponentProperty', component, mesh_property_path, meshId)

    if(newObj.IsSuccess()):
        print('Mesh asset set')
    else:
        print('Failed to set mesh asset property')

    return myEntityId


def initial_viewport_setup(screen_width, screen_height):
    """
    Initial viewport setup for a test to keep screenshots consistent.
    :param screen_width: integer representing the screen resolution width.
    :param screen_height: integer representing the screen resolution height.
    :return: None
    """
    general.set_viewport_size(screen_width, screen_height)
    general.update_viewport()
    helper.wait_for_condition(
        function=lambda: helper.isclose(a=general.get_viewport_size().x, b=screen_width, rel_tol=0.1)
        and helper.isclose(a=general.get_viewport_size().y, b=screen_height, rel_tol=0.1),
        timeout_in_seconds=4.0
    )
    result = helper.isclose(a=general.get_viewport_size().x, b=screen_width, rel_tol=0.1) and helper.isclose(
        a=general.get_viewport_size().y, b=screen_height, rel_tol=0.1)
    general.log(general.get_viewport_size().x)
    general.log(general.get_viewport_size().y)
    general.log(general.get_viewport_size().z)
    general.log(f"Viewport is set to the expected size: {result}")
    general.log("Basic level created")
    general.run_console("r_DisplayInfo = 0")


def after_level_load():
    """Function to call after creating/opening a level to ensure it loads."""
    # Give everything a second to initialize.
    general.idle_enable(True)
    general.idle_wait(1.0)
    general.update_viewport()
    general.idle_wait(0.5)  # half a second is more than enough for updating the viewport.

    # Close out problematic windows, FPS meters, and anti-aliasing.
    if general.is_helpers_shown():  # Turn off the helper gizmos if visible
        general.toggle_helpers()
        general.idle_wait(1.0)
    if general.is_pane_visible("Error Report"):  # Close Error Report windows that block focus.
        general.close_pane("Error Report")
    if general.is_pane_visible("Error Log"):  # Close Error Log windows that block focus.
        general.close_pane("Error Log")
    general.idle_wait(1.0)
    general.run_console("r_displayInfo=0")
    general.run_console("r_antialiasingmode=0")
    general.idle_wait(1.0)

    return True


def create_basic_atom_level(level_name):
    """
    Creates a new level inside the Editor matching level_name & adds the following:
    1. "default_level" entity to hold all other entities.
    2. Adds Grid, Global Skylight (IBL), ground Mesh, Directional Light, Sphere w/ material+mesh, & Camera components.
    3. Each of these components has its settings tweaked slightly to match the ideal scene to test Atom rendering.
    :param level_name: name of the level to create and apply this basic setup to.
    :return: None
    """
    # Create a new level.
    new_level_name = level_name
    heightmap_resolution = 512
    heightmap_meters_per_pixel = 1
    terrain_texture_resolution = 412
    use_terrain = False

    # Return codes are ECreateLevelResult defined in CryEdit.h
    return_code = general.create_level_no_prompt(
        new_level_name, heightmap_resolution, heightmap_meters_per_pixel, terrain_texture_resolution, use_terrain)
    if return_code == 1:
        general.log(f"{new_level_name} level already exists")
    elif return_code == 2:
        general.log("Failed to create directory")
    elif return_code == 3:
        general.log("Directory length is too long")
    elif return_code != 0:
        general.log("Unknown error, failed to create level")
    else:
        general.log(f"{new_level_name} level created successfully")

    # Basic setup for newly created level.
    after_level_load()

    # Create default_level entity
    delete_all_existing_entities()
    default_level = Entity("default_level")
    position = math.Vector3(0.0, 0.0, 0.0)
    default_level.create_entity(position, ["Grid"])
    default_level.get_set_test(0, "Controller|Configuration|Secondary Grid Spacing", 1.0)

    # Set the viewport up correctly after adding the parent default_level entity.
    screen_width = 1280
    screen_height = 720
    degree_radian_factor = 0.0174533  # Used by "Rotation" property for the Transform component.
    initial_viewport_setup(screen_width, screen_height)

    # Create global_skylight entity and set the properties
    global_skylight = Entity("global_skylight")
    global_skylight.create_entity(
        entity_position=None,
        components=["HDRi Skybox", "Global Skylight (IBL)"],
        parent_id=default_level.id)
    global_skylight_asset_path = os.path.join(
        "LightingPresets", "greenwich_park_02_4k_iblskyboxcm_iblspecular.exr.streamingimage")
    global_skylight_asset_value = get_asset_by_path(global_skylight_asset_path)
    global_skylight.get_set_test(0, "Controller|Configuration|Cubemap Texture", global_skylight_asset_value)
    global_skylight.get_set_test(1, "Controller|Configuration|Diffuse Image", global_skylight_asset_value)
    global_skylight.get_set_test(1, "Controller|Configuration|Specular Image", global_skylight_asset_value)

    # Create ground_plane entity and set the properties
    ground_plane = Entity("ground_plane")
    ground_plane.create_entity(
        entity_position=None,
        components=["Material"],
        parent_id=default_level.id)
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetLocalUniformScale", ground_plane.id, 32.0)
    ground_plane_material_asset_path = os.path.join(
        "Materials", "Presets", "PBR", "metal_chrome.azmaterial")
    ground_plane_material_asset_value = get_asset_by_path(ground_plane_material_asset_path)
    ground_plane.get_set_test(0, "Default Material|Material Asset", ground_plane_material_asset_value)
    # Work around to add the correct Atom Mesh component
    mesh_type_id = azlmbr.globals.property.EditorMeshComponentTypeId
    ground_plane.components.append(
        editor.EditorComponentAPIBus(
            bus.Broadcast, "AddComponentsOfType", ground_plane.id, [mesh_type_id]
        ).GetValue()[0]
    )
    ground_plane_mesh_asset_path = os.path.join("Objects", "plane.azmodel")
    ground_plane_mesh_asset_value = get_asset_by_path(ground_plane_mesh_asset_path)
    get_set_test(ground_plane, 1, "Controller|Configuration|Mesh Asset", ground_plane_mesh_asset_value)

    # Create directional_light entity and set the properties
    directional_light = Entity("directional_light")
    directional_light.create_entity(
        entity_position=math.Vector3(0.0, 0.0, 10.0),
        components=["Directional Light"],
        parent_id=default_level.id)
    directional_light_rotation = math.Vector3(degree_radian_factor * -90.0, 0.0, 0.0)
    azlmbr.components.TransformBus(
        azlmbr.bus.Event, "SetLocalRotation", directional_light.id, directional_light_rotation)

    # Create sphere entity and set the properties
    sphere = Entity("sphere")
    sphere.create_entity(
        entity_position=math.Vector3(0.0, 0.0, 1.0),
        components=["Material"],
        parent_id=default_level.id)
    sphere_material_asset_path = os.path.join("Materials", "Presets", "PBR", "metal_brass_polished.azmaterial")
    sphere_material_asset_value = get_asset_by_path(sphere_material_asset_path)
    sphere.get_set_test(0, "Default Material|Material Asset", sphere_material_asset_value)
    # Work around to add the correct Atom Mesh component
    sphere.components.append(
        editor.EditorComponentAPIBus(
            bus.Broadcast, "AddComponentsOfType", sphere.id, [mesh_type_id]
        ).GetValue()[0]
    )
    sphere_mesh_asset_path = os.path.join("Models", "sphere.azmodel")
    sphere_mesh_asset_value = get_asset_by_path(sphere_mesh_asset_path)
    get_set_test(sphere, 1, "Controller|Configuration|Mesh Asset", sphere_mesh_asset_value)

    # Create camera component and set the properties
    camera = Entity("camera")
    camera.create_entity(
        entity_position=math.Vector3(5.5, -12.0, 9.0),
        components=["Camera"],
        parent_id=default_level.id)
    rotation = math.Vector3(
        degree_radian_factor * -27.0, degree_radian_factor * -12.0, degree_radian_factor * 25.0
    )
    azlmbr.components.TransformBus(azlmbr.bus.Event, "SetLocalRotation", camera.id, rotation)
    camera.get_set_test(0, "Controller|Configuration|Field of view", 60.0)
    be_this_camera(camera.id)


def level_load_save(level_name, entities_to_search):
    """
    Opens an existing level matching level_name, then optionally verifies certain expected entities exist in the level.
    :param level_name: name of the level to load and then save, ex. "Emptylevel"
    :param entities_to_search: list of entity names to search for in the level, ex. ["default_level", "sphere"]
    :return:
    """
    general.open_level_no_prompt(level_name)
    helper.wait_for_condition(lambda: level_name in general.get_current_level_name(), 5.0)

    # Ensure the level is saved by checking if all the entities are present
    search_filter = azlmbr.entity.SearchFilter()
    search_filter.names = entities_to_search
    result = len(entity.SearchBus(azlmbr.bus.Broadcast, "SearchEntities", search_filter)) == len(entities_to_search)
    general.log(f"Level is saved successfully: {result}")

    # Create new entity
    temp_entity = Entity("temp_entity")
    temp_entity.create_entity()
    search_filter = azlmbr.entity.SearchFilter()
    search_filter.names = ["temp_entity"]
    result = len(entity.SearchBus(azlmbr.bus.Broadcast, "SearchEntities", search_filter)) == 1
    general.log(f"New entity created: {result}")

    # Delete the new entity
    editor.ToolsApplicationRequestBus(bus.Broadcast, "DeleteEntityById", temp_entity.id)
    result = len(entity.SearchBus(azlmbr.bus.Broadcast, "SearchEntities", search_filter)) == 0
    general.log(f"New entity deleted: {result}")
    general.save_level()


def verify_required_component_property_value(entity_name, component, property_path, expected_property_value):
    """
    Compares the property value of component against the expected_property_value.
    :param entity_name: name of the entity to use (for test verification purposes).
    :param component: component to check on a given entity for its current property value.
    :param property_path: the path to the property inside the component.
    :param expected_property_value: The value expected from the value inside property_path.
    :return: None, but prints to general.log() which the test uses to verify against.
    """
    property_value = editor.EditorComponentAPIBus(
        bus.Broadcast, "GetComponentProperty", component, property_path).GetValue()
    general.log(f"{entity_name}_test: Property value is {property_value} "
                f"which matches {expected_property_value}")


def take_screenshot_game_mode(screenshot_name, entity_name=None):
    """
    Enters game mode & takes a screenshot, then exits game mode after.
    :param screenshot_name: name to give the captured screenshot .ppm file.
    :param entity_name: name of the entity being tested (for generating unique log lines).
    :return:
    """
    general.enter_game_mode()
    helper.wait_for_condition(lambda: general.is_in_game_mode(), 2.0)
    general.log(f"{entity_name}_test: Entered game mode: {general.is_in_game_mode()}")
    ScreenshotHelper(general.idle_wait_frames).capture_screenshot_blocking(f"{screenshot_name}.ppm")
    general.idle_wait(1.0)
    general.exit_game_mode()
    helper.wait_for_condition(lambda: not general.is_in_game_mode(), 2.0)
    general.log(f"{entity_name}_test: Exit game mode: {not general.is_in_game_mode()}")
