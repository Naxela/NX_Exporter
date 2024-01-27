import bpy, os, shutil, json

from .. utility import util

def build_assets():

    print("Building Assets")

    if util.ensureFilesave():

        print("File has been saved")

        currentSavePath = bpy.data.filepath
        currentSaveDir = os.path.dirname(currentSavePath)

        os.chdir(currentSaveDir)

        #Create a "nx-build" folder
        project_folder = "nx-build"

        if(os.path.exists(project_folder)):
            shutil.rmtree(project_folder)
        os.mkdir(project_folder)

        compiled_data, transfer_files = compile_project_data()

        #Write the project manifest to file
        with open(os.path.join(project_folder, "project.nx"), 'w') as file:
            json.dump(compiled_data, file, indent=4)

        #Transfer assets
        for file in transfer_files:
            shutil.copy(bpy.path.abspath(file), project_folder) 

        #Copy Sources folder (if it exists)
        if os.path.exists(os.path.join(currentSaveDir, "Sources")):
            shutil.copytree(os.path.join(currentSaveDir, "Sources"), os.path.join(project_folder, "Sources"))

        #Copy Assets folder
            
        #Copy Shaders

        #Export GLB files
        export_scenes(project_folder)

        print("Project built successfully")

    else:

        print("File has not been saved")
        return

def export_scenes(path):

    initialScene = bpy.context.scene

    #Hide objects not set to export
    for obj in bpy.data.objects:
        if not obj.NX_ObjectProperties.nx_object_export:
            obj.hide_set(True)

    for scene in bpy.data.scenes:
        # Set the current scene
        bpy.context.window.scene = scene

        # Set the output file path
        output_file = os.path.join(path, scene.name + ".glb")

        # Export to GLB
        bpy.ops.export_scene.gltf(
            filepath=output_file, 
            export_format='GLB', 
            use_visible=True,
            use_active_scene=True,
            export_apply=True,
            export_extras=True,
            export_cameras=False,
            export_lights=False,
            export_attributes=True,
            export_skins=True,
            export_draco_mesh_compression_enable=True,
            export_animations=True
        )

    #After export we want to unhide the objects not set to export
    for obj in bpy.data.objects:
        if not obj.NX_ObjectProperties.nx_object_export:
            obj.hide_set(False)

    bpy.context.window.scene = initialScene

def iterateObjectModules(obj):

    modules = []

    for module in obj.NX_UL_ModuleList:
        print("Module: ", module.nx_module_script)
        modules.append(module.nx_module_script)

    return modules

def compile_project_data():
    """
    Compile project data and generate a project manifest based on the scenes, objects, and settings in the Blender project. 
    Returns the compiled project data.
    """

    print("Compiling Project Data")

    parallel_transfer_assets = []

    project = {
        "name":"NAME",
        "developer":"DEV",
        "publisher":"PUB",
        "license":"LIC",
        "version":"VER",
        "description":"DESC",
        "url":"URL",
        "manifest":{
            "scenes":[
            ]
        },
        "options":{
            "graphics":{
                "antialiasing":"true",
                "bloom":"false",
                "ssao":"false",
                "ssr":"false",
                "shadowType":"PCF",
                "shadowResolution":"1024"
            },
            "audio":{
                "effects":1,
                "music":1,
                "ambient":1
            },
            "video":{
                "size":"fullscreen",
                "width":"1024",
                "height":"768"
            }
        }
    }

    project["name"] = bpy.data.filepath

    for scene in bpy.data.scenes:

        print(scene.name)

        data_scene = {
            "name":scene.name,
            "glb_groups":[],
            "scene_empty" : [],
            "scene_meshes" : [],
            "scene_materials" : [],
            "scene_camera" : [],
            "scene_light" : [],
            "scene_speaker" : [],
            "scene_probes" : [],
            "scene_decals" : [],
            "scene_text" : [],
            "scene_curves" : [],
            "scene_modules" : [], #TODO - ITERATE SCENE/ROOT MODULES FIRST!
            "environment" : {
            }
        }


        #GLB GROUPS (1 per scene for now)
        glb_name = scene.name + ".glb"
        data_scene["glb_groups"].append(glb_name)

        id_iterator = 1

        scene_materials = set()

        for obj in scene.objects:

            #Before compile, we need to set a unique id for each object as a property
            obj['nx_id'] = id_iterator
            id_iterator += 1

            if obj.type == "EMPTY":

                empty = {
                    "name" : obj.name,
                    "identifier" : obj['nx_id'],
                    "matrix" : util.get_object_matrix_y_axis(obj),
                    "parent" : util.getObjectParent(obj),
                    "modules" : iterateObjectModules(obj)
                }

                data_scene["scene_empty"].append(empty)

            if obj.type == "MESH" and obj.NX_ObjectProperties.nx_object_export:

                mesh = {
                    "name" : obj.name,
                    "identifier" : obj['nx_id'],
                    "modules" : iterateObjectModules(obj),
                    "lightmaps" : [],
                    "cast_shadows" : obj.NX_ObjectProperties.nx_object_cast_shadows,
                    "receive_shadows" : obj.NX_ObjectProperties.nx_object_receive_shadows,
                    "spawn" : obj.NX_ObjectProperties.nx_object_spawn,
                    "object_status" : obj.NX_ObjectProperties.nx_object_object_status
                }

                data_scene["scene_meshes"].append(mesh)

                if obj.material_slots:

                    for slot in obj.material_slots:

                        if slot.material:

                            scene_materials.add(slot.material.name)

                # if len(obj.material_slots) > 0:

                #     for slots in obj.material_slots:

                #         mat = slots.material

                #         if(mat.name not in data_scene["scene_materials"]):

                #             mat = {
                #                 "name" : mat.name
                #             }

            if obj.type == "CAMERA":

                camera = {
                    "name" : obj.name,
                    "identifier" : obj['nx_id'],
                    "matrix" : util.get_object_matrix_y_axis(obj),
                    "fov" : obj.data.angle,
                    "clip_near" : obj.data.clip_start,
                    "clip_far" : obj.data.clip_end,
                    "parent" : util.getObjectParent(obj),
                    "modules" : iterateObjectModules(obj)
                }

                if obj.data.type == "PERSP":
                    camType = "Perspective"
                elif obj.data.type == "ORTHO":
                    camType = "Orthographic"
                else:
                    camType = "Perspective"

                camera["type"] = camType

                if(obj == bpy.context.scene.camera):
                    camera["active"] = True
                else:
                    camera["active"] = False

                data_scene["scene_camera"].append(camera)

            if obj.type == "LIGHT":

                light = {
                    "name" : obj.name,
                    "identifier" : obj['nx_id'],
                    "matrix" : util.get_object_matrix_y_axis(obj),
                    "color" : list(obj.data.color),
                    "intensity" : obj.data.energy,
                    "type" : obj.data.type,
                    "shadow" : obj.data.use_shadow,
                    "shadowBias" : obj.data.shadow_buffer_bias,
                    "contactShadow" : obj.data.use_contact_shadow,
                    "parent" : util.getObjectParent(obj),
                    "modules" : iterateObjectModules(obj)
                }

                if(obj.data.type == 'POINT'):

                    light["radius"] = obj.data.shadow_soft_size

                elif(obj.data.type == 'SUN'):

                    light["angle"] = obj.data.angle

                elif(obj.data.type == 'SPOT'):

                    light["radius"] = obj.data.shadow_soft_size
                    light["spotSize"] = obj.data.spot_size
                    light["spotBlend"] = obj.data.spot_blend

                elif(obj.data.type == 'AREA'):

                    if(obj.data.shape == 'SQUARE'):
                        light["areaSize"] = [obj.data.size, obj.data.size]
                    elif(obj.data.shape == 'RECTANGLE'):
                        light["areaSize"] = [obj.data.size, obj.data.size_y]
                    elif(obj.data.shape == 'DISK'):
                        light["areaSize"] = [obj.data.size, obj.data.size]
                    elif(obj.data.shape == 'ELLIPSE'):
                        light["areaSize"] = [obj.data.size, obj.data.size_y]

                data_scene["scene_light"].append(light)

            if obj.type == "SPEAKER":

                #TODO - IMPLEMENT AUDIO AUTOPLAY, LOOP, etc.

                speaker = {
                    "name" : obj.name,
                    "identifier" : obj['nx_id'],
                    "matrix" : util.get_object_matrix_y_axis(obj),
                    "volume" : obj.data.volume,
                    "pitch" : obj.data.pitch,
                    "distance_ref" : obj.data.distance_reference,
                    "distance_max" : obj.data.distance_max,
                    "volume_min" : obj.data.volume_min,
                    "volume_max" : obj.data.volume_max,
                    "attenuation" : obj.data.attenuation,
                    "cone_outer" : obj.data.cone_angle_outer,
                    "cone_inner" : obj.data.cone_angle_inner,
                    "cone_outer_volume": obj.data.cone_volume_outer,
                    "parent" : util.getObjectParent(obj),
                    "modules" : iterateObjectModules(obj),
                    "sound" : os.path.basename(obj.data.sound.filepath)
                }

                parallel_transfer_assets.append(obj.data.sound.filepath)

                data_scene["scene_speaker"].append(speaker)

        for mat in scene_materials:

            #TODO - IMPLEMENT SOME KIND OF MOVIETEXTURE CONTROL
            #TODO - IMPLEMENT SOME KIND OF ANIMATED UV CONTROL - EXPRESSION PERHAPS? X=DELTA*0.1; Y=DELTA*0.1 => Uses material.map.offset

            mat = {
                "name" : mat
            }

            data_scene["scene_materials"].append(mat)

        #data_scene["scene_materials"] = list(scene_materials)

        project["manifest"]["scenes"].append(data_scene)

        #Get the active environment
        active_world = scene.world

        if active_world.use_nodes:
        # Get the node tree of the world
            print("Fetching world nodes")
            node_tree = active_world.node_tree

            # Iterate over the nodes in the node tree
            for node in node_tree.nodes:
                
                if(node.type == "BACKGROUND"):
                    for output in node.outputs:
                        for link in output.links:
                            if isinstance(link.to_node, bpy.types.ShaderNodeOutputWorld):

                                #Get the connected input node to the active background node
                                print(node.name)
                                print(node.inputs[0])
                                try:
                                    input_node = node.inputs[0].links[0].from_node
                                except:
                                    input_node = node

                                print("Active Environment Background Input Node: ", input_node.type)

                                if(input_node.type == "BACKGROUND"):
                                    print("BG:", "BG")
                                    data_scene["environment"]["backgroundType"] = "color" #bpy.data.worlds["World.001"].node_tree.nodes["Background"].inputs[0].default_value
                                    data_scene["environment"]["backgroundColor"] = [input_node.inputs[0].default_value[0], input_node.inputs[0].default_value[1], input_node.inputs[0].default_value[2]]
                                elif(input_node.type == "RGB"):
                                    print("BG:", "RGB")
                                    data_scene["environment"]["backgroundType"] = "color"
                                    data_scene["environment"]["backgroundColor"] = [input_node.outputs[0].default_value[0], input_node.outputs[0].default_value[1], input_node.outputs[0].default_value[2]]
                                    data_scene["environment"]["backgroundIntensity"] = input_node.inputs[1].default_value
                                elif(input_node.type == "TEX_ENVIRONMENT"):
                                    print("BG:", "ENVTEX")
                                    data_scene["environment"]["backgroundType"] = "texture"
                                    data_scene["environment"]["backgroundTexture"] = os.path.basename(input_node.image.filepath)
                                    data_scene["environment"]["backgroundIntensity"] = input_node.inputs[1].default_value
                                    parallel_transfer_assets.append(input_node.image.filepath)
                                elif(input_node.type == "TEX_SKY"):
                                    print("BG:", "TEXSKY")
                                    data_scene["environment"]["backgroundType"] = "sky"
                                    data_scene["environment"]["turbidity"] = 10
                                    data_scene["environment"]["rayleigh"] = 3
                                    data_scene["environment"]["mieCoefficient"] = 0.005
                                    data_scene["environment"]["mieDirectionalG"] = 0.7
                                    data_scene["environment"]["elevation"] = 2
                                    data_scene["environment"]["azimuth"] = 180
                                    data_scene["environment"]["exposure"] = 0.5
                                    data_scene["environment"]["backgroundIntensity"] = input_node.inputs[1].default_value

                                # Add additional code here if you want to do something with the node
                                break
    
    return project, parallel_transfer_assets