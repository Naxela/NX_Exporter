import bpy

from ..utility import util

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
    bl_label = "NX Exporter"
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
            row.operator("nx.compile_start")
            row.operator("nx.clean")

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
        #row.operator("nx.compile")