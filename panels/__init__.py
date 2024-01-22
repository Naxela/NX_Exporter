import bpy, os
from bpy.utils import register_class, unregister_class
from . import scene

classes = [
    scene.NX_PT_Panel,
    scene.NX_PT_Settings
]

def register():
    for cls in classes:
        register_class(cls)

def unregister():
    for cls in classes:
        unregister_class(cls)