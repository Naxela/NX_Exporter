import bpy, os, json, webbrowser, subprocess

from .. operations import compile, clean, filemaker

from .. utility import util

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
    

class NX_Run(bpy.types.Operator):
    bl_idname = "nx.compile_run"
    bl_label = "Run"
    bl_description = "Run"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        compile.build_assets()

        bin_path = os.path.join(util.get_addon_path(),"assets","nx.exe")
        asset_path = util.get_assets_path()

        print(bin_path)
        print(asset_path)

        subprocess.Popen([bin_path, asset_path])
        
        webbrowser.open("http://localhost:3000/")

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
    
class NX_Explore(bpy.types.Operator):
    bl_idname = "nx.explore"
    bl_label = "Explore"
    bl_description = "Explore your project"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        #Open the path in explorer

        path = util.get_project_path()

        os.startfile(path)

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

        util.getProjectJSScripts()
        util.getBundledScripts()

        return{'FINISHED'}
    
class NX_UL_PostprocessListNewItem(bpy.types.Operator):
    # Add a new item to the list
    bl_idname = "nx_postprocesslist.new_item"
    bl_label = "Add a new postprocess"
    bl_description = "Add a new postprocess"

    def execute(self, context):
        scene = context.scene

        scene.NX_UL_PostprocessList.add()

        scene.NX_UL_PostprocessListItem = len(scene.NX_UL_PostprocessList) - 1
        scene.NX_UL_PostprocessList[len(scene.NX_UL_PostprocessList) - 1].name = "Postprocess"

        return{'FINISHED'}
    
class NX_UL_PostprocessListRemoveItem(bpy.types.Operator):
    # Delete the selected item from the list
    bl_idname = "nx_postprocesslist.delete_item"
    bl_label = "Removes the postprocess"
    bl_description = "Delete a postprocess"

    # @classmethod
    # def poll(self, context):
    #     """ Enable if there's something in the list """
    #     obj = context.object
    #     return len(obj.NX_UL_PostprocessList) > 0

    def execute(self, context):
        scene = context.scene
        list = scene.NX_UL_PostprocessList
        index = scene.NX_UL_PostprocessListItem

        list.remove(index)

        if index > 0:
            index = index - 1

        scene.NX_UL_PostprocessListItem = index

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

        util.getProjectJSScripts()
        util.getBundledScripts()

        return{'FINISHED'}
    
class NX_NewJavascriptFile(bpy.types.Operator):
    bl_idname = "nx_modulelist.new_script"
    bl_label = "New Script"

    filename: bpy.props.StringProperty(name="Filename (*.js)")

    def execute(self, context):

        obj = context.object
        list = obj.NX_UL_ModuleList
        index = obj.NX_UL_ModuleListItem

        print("Creating javascript file at sources folder", self.filename)

        if(filemaker.create_javascript_file(self.filename)):

            obj.NX_UL_ModuleList[index].nx_module_script = self.filename

            print("Javascript file created")

        else:
            
            print("TODO: ERROR")

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
class NX_EditJavascriptFile(bpy.types.Operator):
    bl_idname = "nx_modulelist.edit_script"
    bl_label = "Edit Script"

    def execute(self, context):

        obj = context.object
        list = obj.NX_UL_ModuleList
        index = obj.NX_UL_ModuleListItem

        file = os.path.join(util.get_sources_path(),list[index].nx_module_script +".js")

        print(file)

        os.system(file)

        print("Editing javascript file at sources folder: ", list[index].nx_module_script)



        return {'FINISHED'}
    
class NX_RefreshScripts(bpy.types.Operator):
    bl_idname = "nx_modulelist.refresh_scripts"
    bl_label = "Refresh scripts"

    def execute(self, context):

        util.getProjectJSScripts()
        util.getBundledScripts()

        # wrd = bpy.data.worlds['Arm']
        # wrd.arm_bundled_scripts_list.clear()

        # with WorkingDir(get_sdk_path() + '/armory/Sources/armory/trait'):
        #     for file in glob.glob('*.hx'):
        #         wrd.arm_bundled_scripts_list.add().name = file.rsplit('.', 1)[0]

        #Fetch bundled scripts
        #Fetch bundled props
        #Fetch script names
        #Fetch script props

        return {'FINISHED'}
    
class NX_OpenStore(bpy.types.Operator):
    bl_idname = "nx.open_store"
    bl_label = "Open Store"

    def execute(self, context):

        print("TODO: Open Store")
        #store.start_store()

        return {'FINISHED'}