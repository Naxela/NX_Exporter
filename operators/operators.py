import bpy, os, json

from .. operations import compile

class NX_Start(bpy.types.Operator):
    bl_idname = "nx.compile_start"
    bl_label = "Start"
    bl_description = "Compile and start your project"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

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
        #compiled = json.dumps(compile_project_data())
        #print(compiled)

        return {"FINISHED"}