import bpy, os
from bpy.props import *

class NX_ObjectProperties(bpy.types.PropertyGroup):

    nx_object_object_status : EnumProperty(
        items = [('Static', 'Static', 'Mark the object as static for performance optimization'),
                ('Dynamic', 'Dynamic', 'Mark the object as dynamic, for animation or physics')],
                name = "Object type", 
                description="Mark the object as static or dynamic", 
                default='Dynamic')
    
    nx_object_export : BoolProperty(
        name="Export",
        description="Export the model when compiling scene",
        default=True
    )

    nx_object_spawn : BoolProperty(
        name="Spawn",
        description="Spawn with scene (on scene initialization)",
        default=True
    )

    nx_object_visible : BoolProperty(
        name="Visible",
        description="Visible in scene",
        default=True
    )

    nx_object_cast_shadows : BoolProperty(
        name="Cast Shadows",
        description="Set whether the object should cast shadows",
        default=True
    )

    nx_object_receive_shadows : BoolProperty(
        name="Receive Shadows",
        description="Set whether the object should receive shadows",
        default=True
    )