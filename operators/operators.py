import bpy, os, json

from .. operations import compile, clean

#SCENE OPERATORS

class NX_Start(bpy.types.Operator):
    bl_idname = "nx.compile_start"
    bl_label = "Start"
    bl_description = "Compile and start your project"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        #TODO: MAKE START/STOP BASED ON A POPEN PROCESS
        #https://github.com/armory3d/armory/blob/main/blender/arm/make.py

        print("Start")

        compile.build_assets()

        #compiled = json.dumps(compile_project_data())
        #print(compiled)

        return {"FINISHED"}
    
class NX_Clean(bpy.types.Operator):
    bl_idname = "nx.clean"
    bl_label = "Clean"
    bl_description = "Clean your project"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        print("Clean")

        clean.clean_soft()

        #compiled = json.dumps(compile_project_data())
        #print(compiled)

        return {"FINISHED"}
    
# OBJECT OPERATORS

class NX_ModuleListNewItem(bpy.types.Operator):
    # Add a new item to the list
    bl_idname = "nx_modulelist.new_item"
    bl_label = "Add a new module"
    bl_description = "Add a new module"

    def execute(self, context):
        obj = context.object

        obj.NX_UL_ModuleList.add()

        obj.NX_UL_ModuleListItem = len(obj.NX_UL_ModuleList) - 1
        obj.NX_UL_ModuleList[len(obj.NX_UL_ModuleList) - 1].name = "Module"

        return{'FINISHED'}
    
class NX_ModuleListRemoveItem(bpy.types.Operator):
    # Delete the selected item from the list
    bl_idname = "nx_modulelist.delete_item"
    bl_label = "Removes the module"
    bl_description = "Delete a module"

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list """
        obj = context.object
        return len(obj.NX_UL_ModuleList) > 0

    def execute(self, context):
        obj = context.object
        list = obj.NX_UL_ModuleList
        index = obj.NX_UL_ModuleListItem

        list.remove(index)

        if index > 0:
            index = index - 1

        obj.NX_UL_ModuleListItem = index

        return{'FINISHED'}
    
class NX_CreateJavascriptFile(bpy.types.Operator):
    bl_idname = "nx_modulelist.add_script"
    bl_label = "Add script"

    #filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    #my_float: bpy.props.FloatProperty(name="Float")
    #my_bool: bpy.props.BoolProperty(name="Toggle Option")
    #my_string: bpy.props.StringProperty(name="String Value")

    filename: bpy.props.StringProperty(name="Filename (*.js)")

    def execute(self, context):
        print("Creating javascript file at sources folder", self)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)