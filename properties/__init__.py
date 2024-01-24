import bpy
from bpy.utils import register_class, unregister_class
from . import scene, object

classes = [
    scene.NX_SceneProperties,
    object.NX_ObjectProperties
]

def register():
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.NX_SceneProperties = bpy.props.PointerProperty(type=scene.NX_SceneProperties)
    bpy.types.Object.NX_ObjectProperties = bpy.props.PointerProperty(type=object.NX_ObjectProperties)

def unregister():
    for cls in classes:
        unregister_class(cls)

    del bpy.types.Scene.NX_SceneProperties
    del bpy.types.Object.NX_ObjectProperties