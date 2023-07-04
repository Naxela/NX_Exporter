bl_info = {
    "name": "NX-Exporter",
    "description": "NX-Exporter",
    "author": "Alexander Kleemann @ Naxela",
    "version": (0, 0, 2),
    "blender": (3, 50, 0),
    "location": "View3D",
    "category": "3D View"
}

#TODO
#Auto-Lightmap detection, plus json setting
#Tonemapping, exposure, gamma, contrast, saturation
#
#
#Colorgrading pass
#Three.js doesn"t support names with dot (.)? Remove these


import os, sys, bpy, time, threading, socket, json, multiprocessing
from . import threejs

from bpy.utils import ( register_class, unregister_class )
from bpy.props import (
    StringProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    EnumProperty,
    PointerProperty,
)
from bpy.types import (
    Panel,
    AddonPreferences,
    Operator,
    PropertyGroup,
)

#Properties

#Operators

class NX_Preview(bpy.types.Operator):
    bl_idname = "nx.preview"
    bl_label = "Preview in three.js"
    bl_description = "Preview the scene in the browser"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        print("Preview Scene")
        threejs.run(0)

        return {"FINISHED"}
    
class NX_PreviewVR(bpy.types.Operator):
    bl_idname = "nx.previewvr"
    bl_label = "Preview in three.js (VR)"
    bl_description = "Preview the scene in the browser"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        print("Preview Scene VR")
        threejs.run(1)

        return {"FINISHED"}
    
class NX_Normalize_Lightmaps(bpy.types.Operator):
    bl_idname = "nx.normalize_lightmaps"
    bl_label = "Normalize Lightmaps"
    bl_description = "Normalize Lightmaps"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        print("Normalize Lightmaps")

        return {"FINISHED"}
    
class NX_AutoUV(bpy.types.Operator):
    bl_idname = "nx.autouv"
    bl_label = "Auto UV"
    bl_description = "Automatically apply geometry node based auto UV to selection. If nothing is selected, the whole scene get's UV'ed"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        nx_autouv = bpy.data.node_groups.get("AutoUV")

        if nx_autouv == None:

            scriptDir = os.path.dirname(os.path.realpath(__file__))

            if bpy.data.filepath.endswith("autouv.blend"): # Prevent load in library itself
                return

            data_path = os.path.abspath(os.path.join(scriptDir, "autouv.blend"))
            data_names = ["AutoUV"]

            # Import
            data_refs = data_names.copy()
            with bpy.data.libraries.load(data_path, link=False) as (data_from, data_to):
                data_to.node_groups = data_refs

            for ref in data_refs:
                ref.use_fake_user = True

        #For each object in scene, we want to add a geometry node modifier
        for obj in bpy.context.scene.objects:
            if obj.type == "MESH":
                modifier = obj.modifiers.new(name="AutoUV", type="NODES")
                modifier.node_group = bpy.data.node_groups.get("AutoUV")

        print("Auto UV")

        return {"FINISHED"}
    
#UIList

class NX_UL_PostprocessStack(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        ob = data
        slot = item
        ma = slot.material
        # draw_item must handle the three layout types... Usually "DEFAULT" and "COMPACT" can share the same code.
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            # You should always start your row layout by a label (icon + text), or a non-embossed text field,
            # this will also make the row easily selectable in the list! The later also enables ctrl-click rename.
            # We use icon_value of label, as our given icon is an integer value, not an enum ID.
            # Note "data" names should never be translated!
            if ma:
                layout.prop(ma, "name", text="", emboss=False, icon_value=icon)
            else:
                layout.label(text="", translate=False, icon_value=icon)
        # "GRID" layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type == "GRID":
            layout.alignment = "CENTER"
            layout.label(text="", icon_value=icon)
    
#Panel

class SCENE_PT_NX_panel (Panel):
    bl_idname = "SCENE_PT_BM_panel"
    bl_label = "NX Exporter"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "NX Exporter"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row(align=True)
        row.operator("nx.preview")
        row = layout.row(align=True)
        row.operator("nx.previewvr")
        row = layout.row(align=True)
        row.label(text="Lightmap manifest:", icon="LIGHT_SUN")
        row = layout.row(align=True)
        row.prop(scene, "nx_lightmap_file")
        row = layout.row(align=True)
        row.label(text="Environment:", icon="WORLD")
        row = layout.row(align=True)
        row.prop(scene, "nx_environment_file")
        row = layout.row(align=True)
        row.prop(scene, "nx_add_inspector")
        row = layout.row(align=True)
        row.label(text="Postprocess effects:", icon="MATERIAL")
        row = layout.row(align=True)
        row.prop(scene, "nx_add_bloom")
        row = layout.row(align=True)
        row.prop(scene, "nx_add_antialiasing")
        row = layout.row(align=True)
        row.prop(scene, "nx_add_chromaticaberration")
        row = layout.row(align=True)
        row.prop(scene, "nx_add_vignette")
        row = layout.row(align=True)
        row.prop(scene, "nx_exposure")
        row = layout.row(align=True)
        row.prop(scene, "nx_contrast")
        #layout.template_list("NX_UL_PostprocessStack", "", scene, "material_slots", scene, "active_material_index")
        #Types:
            #Bloom
            #ImageProcessing
            #FXAA
            #Sharpen
            #ChromaticAberration
            #DepthOfField
            #Grain
            #Vignette
            #ColorCurves
            #Tonemap
            #LensFlare
            #MotionBlur
            #SSAO2
            #DefaultRenderingPipeline


classes = [NX_Preview, NX_PreviewVR, NX_AutoUV, SCENE_PT_NX_panel, NX_UL_PostprocessStack]

def register():

    bpy.types.Scene.nx_environment_file = StringProperty(
            name="",
            description="Path to environment file",
            default="",
            maxlen=1024,
            subtype="FILE_PATH"
        )

    bpy.types.Scene.nx_lightmap_file = StringProperty(
            name="",
            description="Path to lightmap file",
            default="",
            maxlen=1024,
            subtype="FILE_PATH"
        )

    bpy.types.Scene.nx_add_inspector = BoolProperty(
            name="Add inspector",
            description="Add inspector",
            default=False
        )

    bpy.types.Scene.nx_add_bloom = BoolProperty(
            name="Add bloom",
            description="Add bloom",
            default=False
        )
    
    bpy.types.Scene.nx_add_antialiasing = BoolProperty(
            name="Add antialiasing",
            description="Add antialiasing",
            default=False
        )
    
    bpy.types.Scene.nx_add_chromaticaberration = BoolProperty(
            name="Add chromatic aberration",
            description="Add chromatic aberration",
            default=False
        )
    
    bpy.types.Scene.nx_add_vignette = BoolProperty(
            name="Add vignette",
            description="Add vignette",
            default=False
        )
    
    bpy.types.Scene.nx_exposure = FloatProperty(
            name="Exposure",
            description="Exposure",
            default=1.0
        )

    bpy.types.Scene.nx_contrast = FloatProperty(
            name="Contrast",
            description="Contrast",
            default=1.0
        )


    for cls in classes:
        register_class(cls)

def unregister():
    for cls in reversed(classes):
        unregister_class(cls)
    threejs.end()