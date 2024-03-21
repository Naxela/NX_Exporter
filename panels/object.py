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
        obj = bpy.context.object
        layout.use_property_split = True
        layout.use_property_decorate = False

        row = layout.row(align=True)
        row.label(text="Object settings")
        row = layout.row(align=True)
        row.prop(obj.NX_ObjectProperties, "nx_object_export")
        row = layout.row(align=True)
        
        if "NX_InjectionComponent" in obj:
            row.prop(obj.NX_ObjectProperties, "nx_object_injection")
            row = layout.row(align=True)
        else:
            row.prop(obj.NX_ObjectProperties, "nx_object_spawn")
            row = layout.row(align=True)
            row.prop(obj.NX_ObjectProperties, "nx_object_object_status")
            row = layout.row(align=True)

        if obj.type == "MESH":

            row = layout.row(align=True)
            row.label(text="Mesh type settings")
            row = layout.row(align=True)
            row.prop(obj.NX_ObjectProperties, "nx_object_cast_shadows")
            row = layout.row(align=True)
            row.prop(obj.NX_ObjectProperties, "nx_object_receive_shadows")
            row = layout.row(align=True)
            row.prop(obj.NX_ObjectProperties, "nx_object_tags")

        if obj.type == "LIGHT":

            row.label(text="Light type settings")
            row = layout.row(align=True)
            row.label(text="Decay?")
            row = layout.row(align=True)
            row.label(text="Shadow Bias?")
            row = layout.row(align=True)
            row.label(text="VSM? Blur Samples")
            row = layout.row(align=True)
            row.label(text="Normal bias")
            row = layout.row(align=True)
            row.label(text="PCF!? Radius")
            row = layout.row(align=True)
            row.label(text="Spot light stuff")

        if obj.type == "SPEAKER":

            row.label(text="Speaker type settings")
            row = layout.row(align=True)
            row.prop(obj.NX_ObjectProperties, "nx_speaker_autoplay")
            row = layout.row(align=True)
            row.prop(obj.NX_ObjectProperties, "nx_speaker_loop")
            row = layout.row(align=True)
            row.prop(obj.NX_ObjectProperties, "nx_speaker_stream")

class NX_PT_Modules(bpy.types.Panel):
    bl_label = "Components"
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

        row.label(text="TODO: CHECK SAVES")

        row = layout.row()

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
                row = layout.row()
                col = row.column(align=True)
                row.operator("nx_modulelist.edit_script")
                row.operator("nx_modulelist.refresh_scripts")
                row = layout.row()
                row.prop_search(item, "nx_module_script", bpy.data.worlds['NX'], "NX_bundled_list", text="Class")

            elif item.nx_module_type == "JavaScript":

                row = layout.row()
                row.label(text="JavaScript Component")
                row = layout.row()
                col = row.column(align=True)
                col.operator("nx_modulelist.new_script")
                row.operator("nx_modulelist.edit_script")
                row.operator("nx_modulelist.refresh_scripts")
                row = layout.row()
                row.prop_search(item, "nx_module_script", bpy.data.worlds['NX'], "NX_scripts_list", text="Class")

    #bpy.data.objects["Superconduction_Movement"].NX_UL_ModuleList[0].nx_module_script

    # if obj.arm_traitlist_index >= 0 and len(obj.arm_traitlist) > 0:
    #     item = obj.arm_traitlist[obj.arm_traitlist_index]

    #     row = layout.row(align=True)
    #     row.alignment = 'EXPAND'
    #     row.scale_y = 1.2

    #     if item.type_prop == 'Haxe Script' or item.type_prop == 'Bundled Script':
    #         if item.type_prop == 'Haxe Script':
    #             row.operator("arm.new_script", icon="FILE_NEW").is_object = is_object
    #             column = row.column(align=True)
    #             column.enabled = item.class_name_prop != ''
    #             column.operator("arm.edit_script", icon_value=ICON_HAXE).is_object = is_object

    #         # Bundled scripts
    #         else:
    #             row.enabled = item.class_name_prop != ''
    #             row.operator("arm.edit_bundled_script", icon_value=ICON_HAXE).is_object = is_object

    #         refresh_op = "arm.refresh_object_scripts" if is_object else "arm.refresh_scripts"
    #         row.operator(refresh_op, text="Refresh", icon="FILE_REFRESH")

    #         # Default props
    #         row = layout.row()
    #         if item.type_prop == 'Haxe Script':
    #             row.prop_search(item, "class_name_prop", bpy.data.worlds['Arm'], "arm_scripts_list", text="Class")
    #         else:
    #             row.prop_search(item, "class_name_prop", bpy.data.worlds['Arm'], "arm_bundled_scripts_list", text="Class")