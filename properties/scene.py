import bpy, os
from bpy.props import *

class NX_SceneProperties(bpy.types.PropertyGroup):
    nx_setting_clean_option : EnumProperty(
        items = [('Clean', 'Full Clean', 'Clean lightmap directory and revert all materials'),
                ('CleanMarked', 'Clean marked', 'Clean only the objects marked for lightmapping')],
                name = "Clean mode", 
                description="The cleaning mode, either full or partial clean. Be careful that you don't delete lightmaps you don't intend to delete.", 
                default='Clean')
    
    nx_xr_mode : EnumProperty(
        items = [('None', 'None', 'No XR'),
                 ('XR', 'XR', 'Available for both VR/AR'),
                 ('VR', 'VR', 'Virtual Reality'),
                ('AR', 'AR', 'Augmented Reality')],
                name = "XR mode",
                description="The XR mode",
                default='None'
        )
    
    nx_compilation_mode : EnumProperty(
        items = [('Combined', 'Combined', 'Everything is combined into one file per scene. Can be more RAM costly, but good for single-scene projects.'),
                ('Separate', 'Separate', 'All assets are separate files. Allows for streaming gradually, and more RAM conserving but larger disk size')],
                name = "Combined",
                description="Compilation mode",
                default='Combined'
        )
    
    