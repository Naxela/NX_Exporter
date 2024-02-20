import bpy, os, shutil, json, math

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
            if bpy.context.scene.NX_SceneProperties.nx_minify_json:
                json.dump(compiled_data, file, separators=(',', ':'))
            else:
                json.dump(compiled_data, file, indent=4)


        #Transfer assets
        for file in transfer_files:
            shutil.copy(bpy.path.abspath(file), project_folder) 

        #Copy Sources folder (if it exists)
        if os.path.exists(os.path.join(currentSaveDir, "Sources")):
            shutil.copytree(os.path.join(currentSaveDir, "Sources"), os.path.join(project_folder, "Sources"))

        #Copy Bundled folder (if it exists)
        if os.path.exists(os.path.join(currentSaveDir, "Bundled")):
            shutil.copytree(os.path.join(currentSaveDir, "Bundled"), os.path.join(project_folder, "Bundled"))
            
        #Copy Shaders folder (if it exists)
        if os.path.exists(os.path.join(currentSaveDir, "Shaders")):
            shutil.copytree(os.path.join(currentSaveDir, "Shaders"), os.path.join(project_folder, "Shaders"))

        #Copy Lightmaps folder (if it exists)
        if os.path.exists(os.path.join(currentSaveDir, "Lightmaps")):
            shutil.copytree(os.path.join(currentSaveDir, "Lightmaps"), os.path.join(project_folder, "Lightmaps"))

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

        if scene.NX_SceneProperties.nx_compilation_mode == 'Combined':

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
                export_animations=True,
                export_image_format='WEBP',
                export_image_quality=100
            )

        elif scene.NX_SceneProperties.nx_compilation_mode == 'Separate':

            bpy.ops.export_scene.gltf(
                filepath=output_file, 
                export_format='GLTF_SEPARATE',
                export_texture_dir=scene.name + "_assets",
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

        if module.nx_module_enabled:
            print("Module: ", module.nx_module_script)
            modules.append(module.nx_module_script)

        if module.nx_module_type == 'Bundled':
            #We need to copy over the bundled module
            addon_bundled_path = util.get_bundled_path()
            module_path = os.path.join(addon_bundled_path, module.nx_module_script + ".js")
            shutil.copy(module_path, bpy.path.abspath("//Sources"))

            print("Copying from: " + module_path + " to " + bpy.path.abspath("//Sources"))

    return modules

def getActiveAction(obj):

    print("Getting active action for: ", obj.name)

    if obj.animation_data:
        if(obj.animation_data.action):
            return obj.animation_data.action.name
        else:
            return None
    else:
        return None
    
def getLightmaps(obj):

    try:
        if obj["TLM-Lightmap"] is not None:
            return obj["TLM-Lightmap"]
        else:
            return None
    except:
        return None
    
def getPostprocessStack():

    stack = []

    scene = bpy.context.scene

    for node in scene.NX_UL_PostprocessList:

        if node.nx_postprocess_type == "Bloom":

            effect = {
                "type": "bloom",
                "threshold": node.nx_postprocess_bloom_threshold,
                "radius": node.nx_postprocess_bloom_radius,
                "intensity": node.nx_postprocess_bloom_intensity
            }
            stack.append(effect)

        if node.nx_postprocess_type == "Bokeh":

            effect = {
                "type": "bokeh",
                "focus": node.nx_postprocess_bokeh_focus,
                "distance": node.nx_postprocess_bokeh_dof,
                "aperture": node.nx_postprocess_bokeh_aperture
            }
            stack.append(effect)

        if node.nx_postprocess_type == "ChromaticAberration":

            effect = {
                "type": "chromatic_aberration"
            }
            stack.append(effect)

        if node.nx_postprocess_type == "DepthOfField":

            effect = {
                "type": "depthoffield",
            }
            stack.append(effect)

        if node.nx_postprocess_type == "FXAA":

            effect = {
                "type": "fxaa",
            }
            stack.append(effect)

        if node.nx_postprocess_type == "GodRays":

            effect = {
                "type": "godray",
            }
            stack.append(effect)

        if node.nx_postprocess_type == "SMAA":

            effect = {
                "type": "smaa",
            }
            stack.append(effect)

        if node.nx_postprocess_type == "SSAO":

            effect = {
                "type": "ssao",
            }
            stack.append(effect)

        if node.nx_postprocess_type == "TiltShift":

            effect = {
                "type": "tiltshift",
            }
            stack.append(effect)

        if node.nx_postprocess_type == "Tonemapping":

            effect = {
                "type": "tonemapping",
            }
            stack.append(effect)

        if node.nx_postprocess_type == "Vignette":

            effect = {
                "type": "vignette",
            }
            stack.append(effect)

    return stack

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
        "debug": bpy.data.scenes[0].NX_SceneProperties.nx_debug_mode,
        "manifest":{
            "scenes":[
            ]
        },
        "gltf_mode": bpy.data.scenes[0].NX_SceneProperties.nx_compilation_mode,
        "options":{
            "xr":bpy.data.scenes[0].NX_SceneProperties.nx_xr_mode,
            "graphics":{
                "antialiasing":"true",
                "bloom":"false",
                "ssao":"false",
                "ssr":"false",
                "shadowType":"PCF",
                "shadowResolution":"1024",
                "postprocessStack":getPostprocessStack()
            },
            "audio":{
                "effects":1,
                "music":1,
                "ambient":1
            },
            "video":{
                "fullscreen": bpy.data.scenes[0].NX_SceneProperties.nx_fullscreen,
                "width": bpy.data.scenes[0].render.resolution_x * bpy.data.scenes[0].render.resolution_percentage / 100, 
                "height": bpy.data.scenes["Scene"].render.resolution_y * bpy.data.scenes[0].render.resolution_percentage / 100
            }
        }
    }

    project["name"] = bpy.data.filepath

    for scene in bpy.data.scenes:

        print(scene.name)

        data_scene = {
            "name":scene.name,
            "glb_groups":[],
            "scene_empties" : [],
            "scene_meshes" : [],
            "scene_materials" : [],
            "scene_cameras" : [],
            "scene_lights" : [],
            "scene_speakers" : [],
            "scene_probes" : [],
            "scene_decals" : [],
            "scene_text" : [],
            "scene_curves" : [],
            "scene_modules" : [], #TODO - ITERATE SCENE/ROOT MODULES FIRST!
            "environment" : {
            }
        }

        #TODO! - MAKE A NEW COMBINED ID LIST   OR   EMBED THE DATA INSIDE THE GLB FILE

        #GLB GROUPS (1 per scene for now)
        glb_name = scene.name + ".glb"
        data_scene["glb_groups"].append(glb_name)

        #Start with 1, because 0 is the active scene
        id_iterator = 1
        
        #The materials doesn't need to start with 1
        mat_iterator = 0

        scene_materials = set()

        for obj in scene.objects:

            #Before compile, we need to set a unique id for each object as a property
            obj['nx_id'] = id_iterator
            print(obj.name, obj['nx_id'])
            id_iterator += 1

            if obj.type == "EMPTY":

                empty = {
                    "name" : obj.name,
                    "identifier" : obj['nx_id'],
                    "matrix" : util.get_object_matrix_y_axis(obj),
                    "parent" : util.getObjectParent(obj),
                    "modules" : iterateObjectModules(obj),
                    "active_action" : getActiveAction(obj),
                }

                data_scene["scene_empties"].append(empty)

            if obj.type == "MESH" and obj.NX_ObjectProperties.nx_object_export:

                mesh = {
                    "name" : obj.name,
                    "identifier" : obj['nx_id'],
                    "modules" : iterateObjectModules(obj),
                    "lightmaps" : getLightmaps(obj),
                    "cast_shadows" : obj.NX_ObjectProperties.nx_object_cast_shadows,
                    "receive_shadows" : obj.NX_ObjectProperties.nx_object_receive_shadows,
                    "spawn" : obj.NX_ObjectProperties.nx_object_spawn,
                    "object_status" : obj.NX_ObjectProperties.nx_object_object_status,
                    "active_action" : getActiveAction(obj),
                }

                data_scene["scene_meshes"].append(mesh)

                if obj.material_slots:

                    for slot in obj.material_slots:

                        if slot.material:

                            scene_materials.add(slot.material)

                # if len(obj.material_slots) > 0:

                #     for slots in obj.material_slots:

                #         mat = slots.material

                #         if(mat.name not in data_scene["scene_materials"]):

                #             mat = {
                #                 "name" : mat.name
                #             }

            if obj.type == "CAMERA" and obj.NX_ObjectProperties.nx_object_export:

                camera = {
                    "name" : obj.name,
                    "identifier" : obj['nx_id'],
                    "matrix" : util.get_object_matrix_y_axis(obj),
                    "fov" : obj.data.angle,
                    "clip_near" : obj.data.clip_start,
                    "clip_far" : obj.data.clip_end,
                    "parent" : util.getObjectParent(obj),
                    "modules" : iterateObjectModules(obj),
                    "active_action" : getActiveAction(obj),
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

                data_scene["scene_cameras"].append(camera)

            if obj.type == "LIGHT" and obj.NX_ObjectProperties.nx_object_export:

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
                    "modules" : iterateObjectModules(obj),
                    "active_action" : getActiveAction(obj),
                }

                if(obj.data.type == 'POINT'):

                    light["radius"] = obj.data.shadow_soft_size

                elif(obj.data.type == 'SUN'):

                    light["angle"] = obj.data.angle

                elif(obj.data.type == 'SPOT'):

                    light["radius"] = obj.data.shadow_soft_size

                    current_angle = obj.data.spot_size
                    # Calculate the opposite angle
                    if current_angle <= math.pi:
                        opposite_angle = current_angle + math.pi
                    else:
                        opposite_angle = current_angle - math.pi

                    # Set the new spot size
                    light["spotSize"] = opposite_angle

                    #light["spotSize"] = obj.data.spot_size

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

                data_scene["scene_lights"].append(light)

            if obj.type == "SPEAKER" and obj.NX_ObjectProperties.nx_object_export:

                #TODO - IMPLEMENT AUDIO AUTOPLAY, LOOP, etc.

                if(obj.data.sound):

                    if(obj.data.sound.filepath != ""):

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
                            "sound" : os.path.basename(obj.data.sound.filepath),
                            "active_action" : getActiveAction(obj),
                            "autoplay" : obj.NX_ObjectProperties.nx_speaker_autoplay,
                            "loop" : obj.NX_ObjectProperties.nx_speaker_loop,
                            "stream" : obj.NX_ObjectProperties.nx_speaker_stream
                        }

                        parallel_transfer_assets.append(obj.data.sound.filepath)

                        data_scene["scene_speakers"].append(speaker)

            if obj.type == "CURVE" and obj.NX_ObjectProperties.nx_object_export:

                curve = {
                    "name" : obj.name,
                    "identifier" : obj['nx_id'],
                    "matrix" : util.get_object_matrix_y_axis(obj),
                    "parent" : util.getObjectParent(obj),
                    "modules" : iterateObjectModules(obj),
                    "active_action" : getActiveAction(obj),
                    "curve_type" : obj.data.splines[0].type,
                    "spline_data" : []
                }

                #TODO - IMPLEMENT CURVE SPLINE CONTROL

                for spline in obj.data.splines:
                    
                    spline_data = {
                        'points': [],
                        'type': spline.type
                    }
                    
                    # Handle different spline types separately
                    if spline.type == 'BEZIER':
                        for point in spline.bezier_points:
                            # For Bezier, export the handle and control point positions
                            handle1 = point.handle_left[:]
                            control = point.co[:]
                            handle2 = point.handle_right[:]
                            
                            spline_data['points'].append({
                                'handle_left': handle1,
                                'co': control,
                                'handle_right': handle2
                            })
                    elif spline.type == 'NURBS':
                        for point in spline.points:
                            # For NURBS, export the control points and weights
                            spline_data['points'].append({
                                'co': point.co[:],  # Note: Includes weight in co[3]
                            })
                    # Add the spline data to the export data
                    curve['spline_data'].append(spline_data)

                data_scene["scene_curves"].append(curve)

        for mat in scene_materials:

            mat['nx_id'] = id_iterator
            id_iterator += 1

            #print(mat.name, mat['nx_id'])

            #TODO - IMPLEMENT SOME KIND OF MOVIETEXTURE CONTROL
            #TODO - IMPLEMENT SOME KIND OF ALPHA BLENDING
            #TODO - IMPLEMENT SOME KIND OF TEXTURE FILTER CONTROL
            #TODO - IMPLEMENT SOME KIND OF ANIMATED UV CONTROL - EXPRESSION PERHAPS? X=DELTA*0.1; Y=DELTA*0.1 => Uses material.map.offset
            #TODO - IMPLEMENT DIRECT TEXTURE ASSET MOVE
            #TODO - Currently GLB files for each scene contain all materials, not just the ones in the active scene
            #TODO - The above might also be a faster solution - keep some kind of change cache available? Also for future sockets

            scene_textures = set()

            mat = {
                "name" : mat.name,
                "identifier" : mat['nx_id']#,
                #"textures" : scene_textures,
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
                                    data_scene["environment"]["backgroundIntensity"] = node.inputs[1].default_value
                                elif(input_node.type == "TEX_ENVIRONMENT"):
                                    print("BG:", "ENVTEX")
                                    data_scene["environment"]["backgroundType"] = "texture"

                                    backgroundTexPath = input_node.image.filepath
                                    data_scene["environment"]["backgroundTexture"] = bpy.path.basename(bpy.path.abspath(backgroundTexPath))
                                    data_scene["environment"]["backgroundIntensity"] = node.inputs[1].default_value
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
                                    data_scene["environment"]["backgroundIntensity"] = node.inputs[1].default_value

                                # Add additional code here if you want to do something with the node
                                break
    
    return project, parallel_transfer_assets