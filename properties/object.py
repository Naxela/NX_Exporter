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

            #print(item.nx_module_type)

        #     amount = 0

        #     for obj in bpy.context.scene.objects:
        #         if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
        #             if obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode == "AtlasGroupA":
        #                 if obj.TLM_ObjectProperties.tlm_atlas_pointer == item.name:
        #                     amount = amount + 1

        #     row = layout.row()
        #     row.prop(item, "name", text="", emboss=False, icon=custom_icon)
        #     col = row.column()
        #     col.label(text=item.tlm_atlas_lightmap_resolution)
        #     col = row.column()
        #     col.alignment = 'RIGHT'
        #     col.label(text=str(amount))

        # elif self.layout_type in {'GRID'}:
        #     layout.alignment = 'CENTER'
        #     layout.label(text="", icon = custom_icon)

class NX_UL_ModuleListItem(bpy.types.PropertyGroup):
    #obj: PointerProperty(type=bpy.types.Object, description="The object to bake")

    nx_module_script: StringProperty(name="Module", description="The module", default="", override={"LIBRARY_OVERRIDABLE"}) #TODO ON UPDATE => FIX PROPS

    nx_module_type : EnumProperty(
        items = [('Bundled', 'Bundled', 'Select a bundled module'),
                 ('JavaScript', 'JavaScript', 'Create a JavaScript module'),],
                name = "Module Type", 
                description="Select the module type",
                default='Bundled')
    
