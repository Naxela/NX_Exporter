import bpy
from bpy.utils import register_class, unregister_class
#from . import scene, object

classes = [
]

def register():
    for cls in classes:
        register_class(cls)

def unregister():
    for cls in classes:
        unregister_class(cls)