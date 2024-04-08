import bpy, os, json, webbrowser, subprocess, shutil

from .. operations import compile, clean, filemaker, live_link

from .. utility import util, projectMaker, componentInjection

from .. import globals as gbl

#SCENE OPERATORS


def start_server(bin_path, out_path, livelink, production):  # Changed parameter to out_path for clarity
    print("Starting server, current global_dev_server_process:", gbl.global_dev_server_process)

    if not production:
        print("Production!")
        cmd_run_dev = [bin_path, "run", "preview"]  # Make sure this path is correctly pointing to pnpm
    else:
        print("Development!")
        if bpy.data.scenes["Scene"].NX_SceneProperties.nx_optimize:
            cmd_run_dev = [bin_path, "run", "dev3"]
        else:
            cmd_run_dev = [bin_path, "run", "dev"]

    with open('server_output.log', 'w') as f:
        gbl.global_dev_server_process = subprocess.Popen(cmd_run_dev, cwd=out_path)
        #gbl.global_dev_server_process = subprocess.Popen(cmd_run_dev, cwd=out_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if livelink:
        live_link.start()

    print("Server starting...")

def stop_server(livelink):
    print("Stopping server, current global_dev_server_process:", gbl.global_dev_server_process)
    if gbl.global_dev_server_process:
        #IF WINDOWS:
        subprocess.call(['taskkill', '/F', '/T', '/PID', str(gbl.global_dev_server_process.pid)])
        gbl.global_dev_server_process = None
        #FIND WAY TO DO IT ON *NIX TOO

        if live_link:
            live_link.stop()

        print("Server stopped.")
    else:
        print("Server is not running.")

class NX_Start(bpy.types.Operator):
    bl_idname = "nx.compile_start"
    bl_label = "Export"
    bl_description = "Compile and start your project"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        clean.clean_soft()
        compile.build_assets()

        global global_dev_server_process

        # Your setup
        bin_path = os.path.join(util.get_addon_path(), "assets", "pnpm-win-x64.exe")
        project_path = util.get_project_path()
        out_dir = "out"
        out_path = os.path.join(project_path, out_dir)

        # Ensure the 'out' directory exists
        #if not os.path.exists(out_path):
        #    os.mkdir(out_path)

        # Copy files in folder addon/assets/template to out folder
        # TODO - CHECK IF IT EXISTS FIRST!

        if not os.path.exists(out_path):
            shutil.copytree(os.path.join(util.get_addon_path(), "assets", "template"), out_path)
        else:
            print("IT ALREADY EXISTS!")
            pass

        # Copy assets folder to out folder (nx-build/assets) to out/assets
        shutil.copytree(os.path.join(util.get_build_path()), os.path.join(out_path, "assets"))

        package_json_path = os.path.join(out_path, "package.json")
        package_json_content = projectMaker.createPackageJson(util.get_file_name(), "1.0.0")

        # Write package.json to the project directory
        with open(package_json_path, 'w') as package_file:
            package_file.write(json.dumps(package_json_content, indent=4))

        server_config_path = os.path.join(out_path, "server.js")
        server_config_content = projectMaker.createExpressServer(util.get_build_path(), 3001, 3002)

        # Write server.js to the project directory
        with open(server_config_path, 'w') as server_file:
            server_file.write(server_config_content)

        # Step 1: Install dependencies with pnpm
        # TODO - ONLY IF REGEN IS ENABLED!
        cmd_install = [bin_path, "install"]
        install_process = subprocess.Popen(cmd_install, cwd=out_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Wait for the installation process to complete and capture output
        stdout, stderr = install_process.communicate()

        if install_process.returncode == 0:
            print("Dependencies installed successfully. Proceeding to run the 'dev' command.")
        else:
            print(f"Error installing dependencies. Stderr: {stderr}")
            # If there's an error message, print it, otherwise, print stdout
            if stderr:
                print(stderr)
            else:
                print(stdout)
            # Exit or handle the error before proceeding
            exit(1)  # Exit the script or handle the error appropriately

        # # Step 2: Only proceed to run the "dev" command if installation succeeded
        #start_server(bin_path, out_path, bpy.context.scene.NX_SceneProperties.nx_live_link, False)

        #stop_server(bpy.context.scene.NX_SceneProperties.nx_live_link)

        #print(f"Production server should now be running for {out_path}.")

        #webbrowser.open("http://localhost:" + str(4173))

        return {"FINISHED"}

class NX_Generate(bpy.types.Operator):
    bl_idname = "nx.generate"
    bl_label = "Generate"
    bl_description = "Generates the project (pre-generated dependencies and files)"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        return {"FINISHED"}

class NX_Run(bpy.types.Operator):
    bl_idname = "nx.compile_run"
    bl_label = "Start"
    bl_description = "Run"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        clean.clean_soft()
        injection_data = compile.build_assets()

        global global_dev_server_process

        # Your setup
        bin_path = os.path.join(util.get_addon_path(), "assets", "pnpm-win-x64.exe")
        project_path = util.get_project_path()
        out_dir = "out"
        out_path = os.path.join(project_path, out_dir)

        # Ensure the 'out' directory exists
        #if not os.path.exists(out_path):
        #    os.mkdir(out_path)

        # Copy files in folder addon/assets/template to out folder
        shutil.copytree(os.path.join(util.get_addon_path(), "assets", "template"), out_path, dirs_exist_ok=True)

        # Insert injection component data into the ComponentInjection file
        componentInjection.insertInjectionData(os.path.join(out_path,"src","ComponentInjection.tsx"), injection_data, 8)

        # Insert injection component headers into the ComponentInjection file
        injection_header = componentInjection.fetchInjectionHeader()
        componentInjection.insertInjectionData(os.path.join(out_path,"src","ComponentInjection.tsx"), injection_header, 0)

        # Copy assets folder to out folder (nx-build/assets) to public
        shutil.copytree(os.path.join(util.get_build_path()), os.path.join(out_path, "public"), dirs_exist_ok=True)

        # Copy Sources from public folder to src folder (for typescript to read it)
        shutil.copytree(os.path.join(out_path, "public","Sources"), os.path.join(out_path, "src","Sources"), dirs_exist_ok=True)

        package_json_path = os.path.join(out_path, "package.json")
        package_json_content = projectMaker.createPackageJson(util.get_file_name(), "1.0.0")

        # Write package.json to the project directory
        with open(package_json_path, 'w') as package_file:
            package_file.write(json.dumps(package_json_content, indent=4))

        server_config_path = os.path.join(out_path, "server.js")
        server_config_content = projectMaker.createExpressServer(util.get_build_path(), 3001, 3002)

        # Write server.js to the project directory
        with open(server_config_path, 'w') as server_file:
            server_file.write(server_config_content)

        # Step 1: Install dependencies with pnpm
        cmd_install = [bin_path, "install"]
        install_process = subprocess.Popen(cmd_install, cwd=out_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Wait for the installation process to complete and capture output
        stdout, stderr = install_process.communicate()

        if install_process.returncode == 0:
            print("Dependencies installed successfully. Proceeding to run the 'dev' command.")
        else:
            print(f"Error installing dependencies. Stderr: {stderr}")
            # If there's an error message, print it, otherwise, print stdout
            if stderr:
                print(stderr)
            else:
                print(stdout)
            # Exit or handle the error before proceeding
            exit(1)  # Exit the script or handle the error appropriately

        # # Step 2: Only proceed to run the "dev" command if installation succeeded
        start_server(bin_path, out_path, bpy.context.scene.NX_SceneProperties.nx_live_link, True) 
        #print(global_dev_server_process)
        #dev_process = subprocess.Popen(cmd_run_dev, cwd=out_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # # Here, we're assuming you want to manually monitor or stop the dev process,
        # # so we won't use communicate() which waits for the process to complete.
        print(f"Development server should now be running for {out_path}.")

        webbrowser.open("https://localhost:" + str(5173))


        return {"FINISHED"}
    
class NX_Stop(bpy.types.Operator):
    bl_idname = "nx.stop"
    bl_label = "Stop"
    bl_description = "Stop your project"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        stop_server(bpy.context.scene.NX_SceneProperties.nx_live_link)

        return {"FINISHED"}
    
class NX_Clean(bpy.types.Operator):
    bl_idname = "nx.clean"
    bl_label = "Clean"
    bl_description = "Clean your project"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        print("Clean")

        stop_server(bpy.context.scene.NX_SceneProperties.nx_live_link)

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

    filename: bpy.props.StringProperty(name="Filename (*.jsx/*.tsx)")
    fileformat: bpy.props.EnumProperty(
        items = [('TypeScript', 'TypeScript', 'TypeScript format'),
                 ('JavaScript', 'JavaScript', 'JavaScript format'),],
                name = "Script format", 
                description="Select the script format",
                default='JavaScript')

    def execute(self, context):

        obj = context.object
        list = obj.NX_UL_ModuleList
        index = obj.NX_UL_ModuleListItem

        self.filename = self.filename.capitalize()

        print("Creating javascript file at sources folder", self.filename)

        if(filemaker.create_javascript_file(self.filename, self.fileformat)):

            obj.NX_UL_ModuleList[index].nx_module_script = self.filename
            obj.NX_UL_ModuleList[index].nx_module_script_format = self.fileformat

            print("Javascript file created")

        else:
            
            print("TODO: ERROR")

        util.getProjectJSScripts()
        util.getBundledScripts()

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

        #If file exists
        if os.path.exists(os.path.join(util.get_sources_path(), list[index].nx_module_script + ".jsx")):
            file = os.path.join(util.get_sources_path(), list[index].nx_module_script + ".jsx")
        else:
            file = os.path.join(util.get_sources_path(), list[index].nx_module_script + ".tsx")

        os.system(file)

        print("Editing javascript file at sources folder: ", list[index].nx_module_script)

        util.getProjectJSScripts()
        util.getBundledScripts()

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

class OBJECT_OT_injection_component(bpy.types.Operator):
    bl_idname = "object.injection_component"
    bl_label = "Injection Component"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.ops.object.empty_add(type='SINGLE_ARROW')  # This adds an empty object to the scene
        component = bpy.context.object
        component.name = "InjectionComponent"
        component["NX_InjectionComponent"] = True

        return {'FINISHED'}
    
class VIEW3D_MT_nax_menu(bpy.types.Menu):
    bl_label = "NAX Engine"
    bl_idname = "VIEW3D_MT_nax_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator(OBJECT_OT_injection_component.bl_idname, icon='NODE')