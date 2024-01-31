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

class NX_UL_ModuleList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'OBJECT_DATAMODE'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            row = layout.row()
            row.label(text=item.nx_module_type)
            col = row.column()

            if(item.nx_module_script != ""):
                col.label(text=item.nx_module_script)
            else:
                col.label(text="Create script")

class NX_UL_ModuleListItem(bpy.types.PropertyGroup):

    nx_module_script: StringProperty(name="Module", description="The module", default="", override={"LIBRARY_OVERRIDABLE"}) #TODO ON UPDATE => FIX PROPS

    nx_module_type : EnumProperty(
        items = [('Bundled', 'Bundled', 'Select a bundled module'),
                 ('JavaScript', 'JavaScript', 'Create a JavaScript module'),],
                name = "Module Type", 
                description="Select the module type",
                default='Bundled')
    
