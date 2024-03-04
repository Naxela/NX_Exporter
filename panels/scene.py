import bpy

from ..utility import util

from .. import globals as gbl

from bpy.types import (
    Panel,
    AddonPreferences,
    Operator,
    PropertyGroup,
)

# class SCENE_PT_NX_panel (Panel):
#     bl_idname = "SCENE_PT_BM_panel"
#     bl_label = "NX Exporter"
#     bl_space_type = "VIEW_3D"
#     bl_region_type = "UI"
#     bl_category = "NX Exporter"

#     def draw(self, context):
#         layout = self.layout
#         scene = context.scene

#         row = layout.row(align=True)
#         row.label(text="Lightmap manifest:", icon="LIGHT_SUN")

class NX_PT_Panel(bpy.types.Panel):
    bl_label = "NX Engine"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.use_property_split = True
        layout.use_property_decorate = False

        file_path = bpy.data.filepath

        # Check if the file has been saved
        if file_path:

            row = layout.row(align=True)
            if gbl.global_dev_server_process:
                row.operator("nx.stop")
            else:
                row.operator("nx.compile_run")
            
            row.operator("nx.clean")
            row.operator("nx.explore")
            row.operator("nx.compile_start")


            #Here we check if 
            # if util.is_generated_project_present():

            #     row.label(text="NX Play")
            #     row = layout.row(align=True)
            #     row.operator("nx.play", text="Play", icon="PLAY")
            #     row = layout.row(align=True)
            #     row.operator("nx.update", text="Update", icon="PLAY")

            # else:

            #     row.label(text="Local project files needs to be generated first")
            #     row = layout.row(align=True)
            #     row.operator("nx.test", text="Generate Project")

        else:
            row = layout.row(align=True)
            row.label(text="Please save your project")

class NX_PT_Settings(bpy.types.Panel):
    bl_label = "Settings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "NX_PT_Panel"

    @classmethod
    def poll(cls, context):
        file_path = bpy.data.filepath

        # Check if the file has been saved
        return bool(file_path)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.use_property_split = True
        layout.use_property_decorate = False

        row = layout.row(align=True)
        row.label(text="Environment:", icon="WORLD")
        row = layout.row(align=True)
        row.prop(scene.NX_SceneProperties, "nx_xr_mode")
        row = layout.row(align=True)
        row.prop(scene.NX_SceneProperties, "nx_debug_mode")
        row = layout.row(align=True)
        row.prop(scene.NX_SceneProperties, "nx_fullscreen")
        row = layout.row(align=True)
        row.prop(scene.NX_SceneProperties, "nx_minify_json")
        row = layout.row(align=True)
        row.prop(scene.NX_SceneProperties, "nx_compilation_mode")
        row = layout.row(align=True)
        row.prop(scene.NX_SceneProperties, "nx_pipeline_mode")
        row = layout.row(align=True)
        row.prop(scene.NX_SceneProperties, "nx_live_link")
        row = layout.row(align=True)
        row.prop(scene.NX_SceneProperties, "nx_http_port")
        row = layout.row(align=True)
        row.prop(scene.NX_SceneProperties, "nx_tcp_port")
        row = layout.row(align=True)
        row.prop(scene.NX_SceneProperties, "nx_texture_quality", slider=True)
        #row.operator("nx.compile")

class NX_PT_Postprocessing(bpy.types.Panel):
    bl_label = "Postprocessing"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "NX_PT_Panel"

    @classmethod
    def poll(cls, context):
        file_path = bpy.data.filepath

        # Check if the file has been saved
        return bool(file_path)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.use_property_split = True
        layout.use_property_decorate = False

        sceneProperties = scene.NX_SceneProperties

        postprocessList = scene.NX_UL_PostprocessList
        postprocessListItem = scene.NX_UL_PostprocessListItem

        if sceneProperties.nx_pipeline_mode == "Standard":

            row = layout.row()
            row.label(text="Standard Pipeline")
            row = layout.row()
            row.prop(sceneProperties, "nx_postprocess_standard_tonemapper")
            row = layout.row()
            row.prop(sceneProperties, "nx_postprocess_standard_ssao")
            row = layout.row()
            row.prop(sceneProperties, "nx_postprocess_standard_bloom")
            row = layout.row()
            row.prop(sceneProperties, "nx_postprocess_standard_antialiasing")
            #row = layout.row()
            #row.prop(scene.NX_SceneProperties, "nx_pipeline_standard")

        if sceneProperties.nx_pipeline_mode == "Performance":

            row = layout.row()
            row.label(text="Performance Pipeline currently has no options.")

        if sceneProperties.nx_pipeline_mode == "Custom":
            row = layout.row()
            row.label(text="Custom Pipeline")

            row = layout.row()

            rows = 2
            if len(postprocessList) > 1:
                rows = 4
            row.template_list("NX_UL_PostprocessList", "Postprocess List", scene, "NX_UL_PostprocessList", scene, "NX_UL_PostprocessListItem", rows=rows)
            col = row.column(align=True)
            col.operator("nx_postprocesslist.new_item", icon='ADD', text="")
            col.operator("nx_postprocesslist.delete_item", icon='REMOVE', text="")

            # objectProperties = obj.NX_ObjectProperties

            # moduleList = obj.NX_UL_ModuleList
            # moduleListItem = obj.NX_UL_ModuleListItem

            # row = layout.row()

            # row.label(text="TODO: CHECK SAVES")

            # row = layout.row()

            # rows = 2
            # if len(moduleList) > 1:
            #     rows = 4
            # row.template_list("NX_UL_ModuleList", "Module List", obj, "NX_UL_ModuleList", obj, "NX_UL_ModuleListItem", rows=rows)
            # col = row.column(align=True)
            # col.operator("nx_modulelist.new_item", icon='ADD', text="")
            # col.operator("nx_modulelist.delete_item", icon='REMOVE', text="")

            if postprocessListItem >= 0 and len(postprocessList) > 0:
                item = postprocessList[postprocessListItem]

                layout.prop(item, "nx_postprocess_type")

                if item.nx_postprocess_type == "Bloom":

                    row = layout.row()
                    row.prop(item, "nx_postprocess_bloom_threshold")
                    row = layout.row()
                    row.prop(item, "nx_postprocess_bloom_radius")
                    row = layout.row()
                    row.prop(item, "nx_postprocess_bloom_intensity")

                if item.nx_postprocess_type == "Bokeh":

                    row = layout.row()
                    row.prop(item, "nx_postprocess_bokeh_focus")
                    row = layout.row()
                    row.prop(item, "nx_postprocess_bokeh_dof")
                    row = layout.row()
                    row.prop(item, "nx_postprocess_bokeh_aperture")

                if item.nx_postprocess_type == "ChromaticAberration":

                    row = layout.row()
                    row.label(text="Chromatic Aberration")

                if item.nx_postprocess_type == "DepthOfField":

                    row = layout.row()
                    row.label(text="Depth of Field")

                if item.nx_postprocess_type == "FXAA":

                    row = layout.row()
                    row.label(text="FXAA")

                if item.nx_postprocess_type == "GodRays":

                    row = layout.row()
                    row.label(text="GodRays")

                if item.nx_postprocess_type == "SMAA":

                    row = layout.row()
                    row.label(text="SMAA")

                if item.nx_postprocess_type == "SSAO":

                    row = layout.row()
                    row.label(text="SSAO")

                if item.nx_postprocess_type == "TiltShift":

                    row = layout.row()
                    row.label(text="TiltShift")

                if item.nx_postprocess_type == "Tonemapping":

                    row = layout.row()
                    row.label(text="Tonemapping")

                if item.nx_postprocess_type == "Vignette":

                    row = layout.row()
                    row.label(text="Vignette")

            #         row = layout.row()
            #         col = row.column(align=True)
            #         row.operator("nx_modulelist.edit_script")
            #         row.operator("nx_modulelist.refresh_scripts")
            #         row = layout.row()
            #         row.prop_search(item, "nx_module_script", bpy.data.worlds['NX'], "NX_bundled_list", text="Class")

            #     elif item.nx_module_type == "JavaScript":

            #         row = layout.row()
            #         row.label(text="JavaScript Component")
            #         row = layout.row()
            #         col = row.column(align=True)
            #         col.operator("nx_modulelist.new_script")
            #         row.operator("nx_modulelist.edit_script")
            #         row.operator("nx_modulelist.refresh_scripts")
            #         row = layout.row()
            #         row.prop_search(item, "nx_module_script", bpy.data.worlds['NX'], "NX_scripts_list", text="Class")

class NX_PT_Modules(bpy.types.Panel):
    bl_label = "Modules"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "NX_PT_Panel"

    @classmethod
    def poll(cls, context):
        file_path = bpy.data.filepath

        # Check if the file has been saved
        return bool(file_path)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.use_property_split = True
        layout.use_property_decorate = False

        row = layout.row(align=True)
        row.label(text="Environment:", icon="WORLD")
        row = layout.row(align=True)
        #row.operator("nx.compile")