import bpy, os
from bpy.props import *

class NX_SceneProperties(bpy.types.PropertyGroup):
    nx_setting_clean_option : EnumProperty(
        items = [('Clean', 'Full Clean', 'Clean lightmap directory and revert all materials'),
                ('CleanMarked', 'Clean marked', 'Clean only the objects marked for lightmapping')],
                name = "Clean mode", 
                description="The cleaning mode, either full or partial clean. Be careful that you don't delete lightmaps you don't intend to delete.", 
                default='Clean')
    
    nx_xr_mode : BoolProperty(
        name="Enable XR",
        description="Enable XR",
        default=False
    )

    nx_debug_mode : BoolProperty(
        name="Enable debug",
        description="Enable debug",
        default=False
    )

    nx_fullscreen : BoolProperty(
        name="Fullscreen",
        description="Fullscreen",
        default=False
    )
    
    nx_compilation_mode : EnumProperty(
        items = [('Combined', 'Combined', 'Everything is combined into one file per scene. Can be more RAM costly, but good for single-scene projects.'),
                ('Separate', 'Separate', 'All assets are separate files. Allows for streaming gradually, and more RAM conserving but larger disk size')],
                name = "Combined",
                description="Compilation mode",
                default='Combined'
        )
    
    
class NX_UL_PostprocessList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'OBJECT_DATAMODE'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            row = layout.row()
            row.label(text=item.nx_postprocess_type)
            row.separator(factor=0.1)
            row.prop(item, "nx_module_enabled")
            # col = row.column()

            # if(item.nx_module_script != ""):
            #     #row.label(text=item.name if item.name != "" else " ", icon=custom_icon, icon_value=custom_icon_value)
            #     col.label(text=item.nx_module_script)
            # else:
            #     col.label(text="Create script")

class NX_UL_PostprocessListItem(bpy.types.PropertyGroup):

    nx_postprocess_type : EnumProperty(
        items = [('Bloom', 'Bloom', 'Bloom'),
                 ('Bokeh', 'Bokeh', 'Bokeh'),
                 ('ChromaticAberration', 'Chromatic Aberration', 'Chromatic Aberration'),
                 ('DepthOfField', 'Depth of Field', 'Depth of Field'),
                 ('FXAA', 'FXAA', 'FXAA'),
                 ('GodRays', 'God Rays', 'God Rays'),
                 ('SMAA', 'SMAA', 'SMAA'),
                 ('SSAO', 'SSAO', 'SSAO'),
                 ('TiltShift', 'Tilt Shift', 'Tilt Shift'),
                 ('Tonemapping', 'Tonemapping', 'Tonemapping'),
                 ('Vignette', 'Vignette', 'Vignette')],
                name = "Postprocessing Type",
                description="Select the postprocessing type",
                default='Bloom'
        )

    nx_module_enabled : BoolProperty(name="", description="Whether this trait is enabled", default=True, override={"LIBRARY_OVERRIDABLE"})

    nx_module_script: StringProperty(name="Module", description="The module", default="", override={"LIBRARY_OVERRIDABLE"}) #TODO ON UPDATE => FIX PROPS

    nx_module_type : EnumProperty(
        items = [('Bundled', 'Bundled', 'Select a bundled module'),
                 ('JavaScript', 'JavaScript', 'Create a JavaScript module'),],
                name = "Module Type", 
                description="Select the module type",
                default='Bundled')
    
