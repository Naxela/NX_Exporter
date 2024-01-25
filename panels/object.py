import bpy
from bpy.props import *
from bpy.types import Menu, Panel

class NX_PT_ObjectMenu(bpy.types.Panel):
    bl_label = "NX Engine"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = bpy.context.object
        layout.use_property_split = True
        layout.use_property_decorate = False

        if obj.type == "MESH":
            row = layout.row(align=True)
            row.prop(obj.NX_ObjectProperties, "nx_object_export")
            row = layout.row(align=True)
            row.prop(obj.NX_ObjectProperties, "nx_object_spawn")
            row = layout.row(align=True)
            row.prop(obj.NX_ObjectProperties, "nx_object_object_status")
            row = layout.row(align=True)
            row.prop(obj.NX_ObjectProperties, "nx_object_cast_shadows")
            row = layout.row(align=True)
            row.prop(obj.NX_ObjectProperties, "nx_object_receive_shadows")

class NX_PT_Modules(bpy.types.Panel):
    bl_label = "Modules"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "NX_PT_ObjectMenu"

    def draw(self, context):
        layout = self.layout
        obj = bpy.context.object
        objectProperties = obj.NX_ObjectProperties

        moduleList = obj.NX_UL_ModuleList
        moduleListItem = obj.NX_UL_ModuleListItem

        row = layout.row()
        #layout.label(text="LIST HERE ")
        #row.prop(sceneProperties, "tlm_atlas_mode", expand=True)

        rows = 2
        if len(moduleList) > 1:
            rows = 4
        row.template_list("NX_UL_ModuleList", "Module List", obj, "NX_UL_ModuleList", obj, "NX_UL_ModuleListItem", rows=rows)
        col = row.column(align=True)
        col.operator("nx_modulelist.new_item", icon='ADD', text="")
        col.operator("nx_modulelist.delete_item", icon='REMOVE', text="")

        if moduleListItem >= 0 and len(moduleList) > 0:
            item = moduleList[moduleListItem]

            layout.prop(item, "nx_module_type", expand=True)

            if item.nx_module_type == "Bundled":

                row = layout.row()
                row.label(text="Bundled Module")

            elif item.nx_module_type == "JavaScript":

                row = layout.row()
                row.label(text="JavaScript Module")

        #if sceneProperties.tlm_atlas_mode == "Prepack":



            # rows = 2
            # if len(atlasList) > 1:
            #     rows = 4
            # row = layout.row()
            # row.template_list("TLM_UL_AtlasList", "Atlas List", scene, "TLM_AtlasList", scene, "TLM_AtlasListItem", rows=rows)
            # col = row.column(align=True)
            # col.operator("tlm_atlaslist.new_item", icon='ADD', text="")
            # col.operator("tlm_atlaslist.delete_item", icon='REMOVE', text="")
            # col.menu("TLM_MT_AtlasListSpecials", icon='DOWNARROW_HLT', text="")

            # if atlasListItem >= 0 and len(atlasList) > 0:
            #     item = atlasList[atlasListItem]
            #     layout.prop(item, "tlm_atlas_lightmap_unwrap_mode")
            #     layout.prop(item, "tlm_atlas_lightmap_resolution")
            #     layout.prop(item, "tlm_atlas_unwrap_margin")

            #     amount = 0

            #     for obj in bpy.context.scene.objects:
            #         if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
            #             if obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode == "AtlasGroupA":
            #                 if obj.TLM_ObjectProperties.tlm_atlas_pointer == item.name:
            #                     amount = amount + 1

            #     layout.label(text="Objects: " + str(amount))
            #     layout.prop(item, "tlm_atlas_merge_samemat")

                # layout.prop(item, "tlm_use_uv_packer")
                # layout.prop(item, "tlm_uv_packer_padding")
                # layout.prop(item, "tlm_uv_packer_packing_engine")