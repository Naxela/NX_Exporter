import bpy
from bpy.utils import register_class, unregister_class

from . import operators
from .. operations import clean

classes = [
    operators.NX_Start,
    operators.NX_Clean,
    operators.NX_Explore,
    operators.NX_Run,
    operators.NX_Stop,
    operators.NX_ModuleListNewItem,
    operators.NX_ModuleListRemoveItem,
    operators.NX_NewJavascriptFile,
    operators.NX_EditJavascriptFile,
    operators.NX_RefreshScripts,
    operators.NX_UL_PostprocessListNewItem,
    operators.NX_UL_PostprocessListRemoveItem,
    operators.VIEW3D_MT_nax_menu,
    operators.OBJECT_OT_injection_component
]

def add_nax_menu(self, context):
    self.layout.menu(operators.VIEW3D_MT_nax_menu.bl_idname, icon='INFO')

def register():
    for cls in classes:
        register_class(cls)

    bpy.types.VIEW3D_MT_add.append(add_nax_menu)
        
def unregister():
    for cls in classes:
        unregister_class(cls)

    operators.stop_server(bpy.context.scene.NX_SceneProperties.nx_live_link)
    clean.clean_soft()
    bpy.types.VIEW3D_MT_add.remove(add_nax_menu)