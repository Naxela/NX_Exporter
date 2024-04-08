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

    nx_regen_project : BoolProperty(
        name="Regenerate Project",
        description="Regenerate project files every time you press start",
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

    nx_minify_json : BoolProperty(
        name="Minify",
        description="Minify",
        default=False
    )
    
    nx_compilation_mode : EnumProperty(
        items = [('Combined', 'Combined', 'Everything is combined into one file per scene. Can be more RAM costly, but good for single-scene projects.'),
                ('Separate', 'Separate', 'All assets are separate files. Allows for streaming gradually, and more RAM conserving but larger disk size')],
                name = "Compilation mode",
                description="Compilation mode",
                default='Combined'
        )
    
    nx_runtime : EnumProperty(
        items = [('PNPM', 'PNPM', 'Use a bundled PNPM binary to setup and run your Vite and ThreejS'),
                ('Electron', 'Electron', 'Use a bundled Electron binary to setup and run your Vite and ThreejS'),],
                name = "Runtime",
                description="Select which runtime to use",
                default='PNPM'
        )
    
    nx_live_link : BoolProperty(
        name="Live Link",
        description="Enable live linking",
        default=False
    )

    nx_http_port : IntProperty(
        name="HTTP Port",
        description="HTTP Port for localhost server",
        default=3000
    )

    nx_tcp_port : IntProperty(
        name="TCP Port",
        description="TCP Port used for live link",
        default=3001
    )

    nx_texture_quality : IntProperty(
        name="Texture Quality",
        description="Texture Quality",
        default=100,
        min=0,
        max=100
    )

    nx_initial_scene : PointerProperty(
        name="Scene", 
        description="Scene to launch",
        type=bpy.types.Scene
    )

    nx_enable_shadows : BoolProperty(
        name="Enable shadows",
        description="Enable live linking",
        default=False
    )

    nx_optimize : BoolProperty(
        name="Optimize and compress",
        description="Optimize and compress during export",
        default=False
    )

    nx_shadows_mode : EnumProperty(
        items = [('Basic', 'Basic', 'Basic gives unfiltered shadow maps - fastest, but lowest quality'),
                 ('PCF', 'PCF', 'PCF filters shadow maps using the Percentage-Closer Filtering (PCF) algorithm (default).'),
                 ('PCFS', 'PCFS', 'PCFfilters shadow maps using the Percentage-Closer Filtering (PCF) algorithm with better soft shadows especially when using low-resolution shadow maps.'),
                ('VSM', 'VSM', 'VSM filters shadow maps using the Variance Shadow Map (VSM) algorithm. When using VSM all shadow receivers will also cast shadows.')],
                name = "Shadow Type",
                description="Select which shadow types to use",
                default='PCF'
        )
    
    nx_shadows_resolution : EnumProperty(
        items = [('256', '256', '256 pixel shadow resolution'),
                 ('512', '512', '512 pixel shadow resolution'),
                 ('1024', '1024', '1024 pixel shadow resolution'),
                 ('2048', '2048', '2048 pixel shadow resolution'),
                 ('4096', '4096', '4096 pixel shadow resolution'),
                ('8192', '8192', '8192 pixel shadow resolution')],
                name = "Shadow map resolution",
                description="Select the resolution to use",
                default='256'
        )

    nx_injection_header : PointerProperty(
            name="Injection header", 
            description="Prepend header to injection file",
            type=bpy.types.Text
        )



    #Option for the background to be:
    #- Just visible
    #- Only reflection
    #- Both irradiance and reflection
    
    # nx_environment_mode : EnumProperty(
    #     items = [('', '', ''),
    #             ('', '', '')],
    #             name = "",
    #             description="",
    #             default=''
    #     )
    
    nx_pipeline_mode : EnumProperty(
        items = [('Standard', 'Standard', 'The default ThreeJS setup'),
                 ('Performance', 'Performance', 'Pipeline optimized for optimal performance'),
                ('Custom', 'Custom', 'Allows for a customizable pipeline. Opens up the postprocessing panel')],
                name = "Pipeline",
                description="Select which pipeline mode to use",
                default='Standard'
        )
    
    nx_export_texture_format_combined : EnumProperty(
        items = [('JPEG/PNG', 'JPEG/PNG', 'Exported textures will be JPEG. Images needing alpha channel will be saved as png'),
                 ('WebP', 'WebP', 'Exported textures will be JPEG')],
                name = "Texture Format",
                description="Select which texture format to use",
                default='WebP'
        )
    
    #STANDARD PIPELINE PROPERTIES

    nx_postprocess_standard_tonemapper : EnumProperty(
        items = [('None', 'None', 'No tonemapping'),
                 ('Linear', 'Linear', 'Linear tonemapping'),
                 ('Reinhard', 'Reinhard', 'Reinhard tonemapping'),
                 ('Cineon', 'Cineon', 'Cineon tonemapping'),
                 ('Filmic', 'Filmic', 'Filmic tonemapping'),
                 ('AgX', 'AgX', 'AgX tonemapping'),
                 ('Neutral', 'Neutral', 'Neutral tonemapping')],
                name = "Tonemapping",
                description="Select the tonemapping",
                default='None'
        )
    
    nx_postprocess_standard_ssao : BoolProperty(
        name="SSAO",
        description="SSAO",
        default=False
    )

    nx_postprocess_standard_bloom : BoolProperty(
        name="Bloom",
        description="Bloom",
        default=False
    )

    nx_postprocess_standard_antialiasing : BoolProperty(
        name="Antialiasing",
        description="Enable antialiasing",
        default=False
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
    
    ############################################
    # BLOOM PROPERTIES
    nx_postprocess_bloom_threshold : FloatProperty(
        name="Threshold",
        description="Threshold",
        default=0.9
    )

    nx_postprocess_bloom_radius : FloatProperty(
        name="Radius",
        description="Radius",
        default=0.85
    )

    nx_postprocess_bloom_intensity : FloatProperty(
        name="Intensity",
        description="Intensity",
        default=1.0
    )

    ############################################
    # BOKEH PROPERTIES

    nx_postprocess_bokeh_focus : FloatProperty(
        name="Focus",
        description="Focus",
        default=0.5
    )

    nx_postprocess_bokeh_dof : FloatProperty(
        name="Distance",
        description="Distance",
        default=1.0
    )

    nx_postprocess_bokeh_aperture : FloatProperty(
        name="Aperture",
        description="Aperture",
        default=0.025
    )

    nx_postprocess_bokeh_maxBlur : FloatProperty(
        name="Max Blur",
        description="Max Blur",
        default=1.0
    )

    ############################################
    # CHROMATIC ABERRATION PROPERTIES

    nx_postprocess_chromatic_aberration_offset : FloatProperty(
        name="Offset",
        description="Offset",
        default=1.0
    )

    ############################################
    # DEPTH OF FIELD PROPERTIES

    nx_postprocess_dof_focus_distance : FloatProperty(
        name="Focus Distance",
        description="Focus Distance",
        default=1.0
    )

    nx_postprocess_dof_focus_range : FloatProperty(
        name="Focus Range",
        description="Focus Range",
        default=1.0
    )

    nx_postprocess_dof_focal_length : FloatProperty(
        name="Focal Length",
        description="Focal Length",
        default=1.0
    )

    nx_postprocess_dof_bokeh_scale : FloatProperty(
        name="Bokeh Scale",
        description="Bokeh Scale",
        default=1.0
    )

    nx_postprocess_dof_resolution_scale : FloatProperty(
        name="Resolution Scale",
        description="Resolution Scale",
        default=1.0
    )

    ############################################
    # FXAA PROPERTIES

    ############################################
    # GOD RAYS PROPERTIES

    ############################################
    # SMAA PROPERTIES

    ############################################
    # SSAO PROPERTIES