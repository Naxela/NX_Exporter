import bpy
from bpy.utils import register_class, unregister_class

from . import operators

classes = [
    operators.NX_Start,
    operators.NX_Clean
]

def register():
    for cls in classes:
        register_class(cls)
        
def unregister():
    for cls in classes:
        unregister_class(cls)