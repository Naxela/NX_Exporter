import bpy
from bpy.utils import register_class, unregister_class
from . import scene, object
from bpy.app.handlers import persistent

@persistent
def ensure_nx_world_exists(scene):
    if not bpy.data.worlds.get("NX"):
        nx_world = bpy.data.worlds.new("NX")
        nx_world.name = "NX"
        nx_world.use_fake_user = True

classes = [
    scene.NX_SceneProperties,
    object.NX_ObjectProperties,
    object.NX_UL_ModuleListItem,
    object.NX_UL_ModuleList,
    scene.NX_UL_PostprocessListItem,
    scene.NX_UL_PostprocessList
]

def register():
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.NX_SceneProperties = bpy.props.PointerProperty(type=scene.NX_SceneProperties)
    bpy.types.Object.NX_ObjectProperties = bpy.props.PointerProperty(type=object.NX_ObjectProperties)

    bpy.types.Scene.NX_UL_PostprocessListItem = bpy.props.IntProperty(name="Index for postprocesslist", default=0)
    bpy.types.Scene.NX_UL_PostprocessList = bpy.props.CollectionProperty(type=scene.NX_UL_PostprocessListItem)

    bpy.types.Object.NX_UL_ModuleListItem = bpy.props.IntProperty(name="Index for modulelist", default=0)
    bpy.types.Object.NX_UL_ModuleList = bpy.props.CollectionProperty(type=object.NX_UL_ModuleListItem) #MODULELIST => MODULELIST ITEM

    bpy.types.World.NX_scripts_list = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.World.NX_bundled_list = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    bpy.app.handlers.load_post.append(ensure_nx_world_exists)

def unregister():
    for cls in classes:
        unregister_class(cls)

    del bpy.types.Scene.NX_SceneProperties
    del bpy.types.Object.NX_ObjectProperties

    bpy.app.handlers.load_post.remove(ensure_nx_world_exists)