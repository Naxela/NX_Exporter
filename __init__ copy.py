#region header-section

bl_info = {
    "name": "NX-Exporter",
    "description": "NX-Exporter",
    "author": "Alexander Kleemann @ Naxela",
    "version": (0, 0, 2),
    "blender": (3, 50, 0),
    "location": "View3D",
    "category": "3D View"
}

#endregion

#region imports
import os, sys, bpy, time, threading, socket, shutil, json, multiprocessing, math, mathutils
from . import threejs

import subprocess
import webbrowser
import tempfile


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
#endregion

#region properties
#endregion

#region utility-methods
def is_node_installed():
    try:
        # Check if 'npm' command works
        subprocess.check_output(['npm', '-v'], stderr=subprocess.STDOUT)
        print("NPM is installed.")
        return True
    except (subprocess.CalledProcessError, OSError):
        try:
            # Full path to node.exe (assuming your folder structure)
            node_path = os.path.join(os.path.dirname(__file__), 'node', 'node.exe')

            # Check if 'node' command works with this path
            subprocess.check_output([node_path, '-v'], stderr=subprocess.STDOUT)
            print("Node.js is installed at:", node_path)
            return True
        except (subprocess.CalledProcessError, OSError) as e:
            print("Error:", e)
            return False

def is_generated_project_present():

    currentSavePath = bpy.data.filepath
    currentSaveDir = os.path.dirname(currentSavePath)

    project_name = "nx-project"
    directory = os.path.join(currentSaveDir, project_name)  # Set your desired path here

    package_json_path = os.path.join(directory, 'package.json')

    # Check if package.json exists
    if not os.path.isfile(package_json_path):
        return False

    # Optional: Validate the contents of package.json
    try:
        with open(package_json_path, 'r') as file:
            package_data = json.load(file)

        return True
        # You can add more checks here to validate the structure of package.json
        # For example, check if certain fields exist:
        # if 'name' in package_data and 'scripts' in package_data:
        #     if package_data['name'] == 'test':
        #         return True
        #     else:
        #         return False
        # else:
        #     return False

    except json.JSONDecodeError:
        # The file is not a valid JSON
        return False

    return False

def create_config_file(path, name, private, version):

    path = os.path.join(path, "nx-project") 

    package_preset = {
        "name": name,
        "private": 'true',
        "version": version,
        "type": "module",
        "scripts": {
            "dev": "vite --host",
            "build": "vite build",
            "preview": "vite preview"
        },
        "devDependencies": {
            "vite": "^5.0.8"
        },
        "dependencies": {
            "three": "^0.160.0"
        }
    }

    vite_config_preset = '''
import { defineConfig } from 'vite'
import mkcert from 'vite-plugin-mkcert'

function watchAllPlugin() {
  return {
    name: 'watch-all',
    configureServer(server) {
      server.watcher.on('all', (event, path) => {
        if (event === 'change' || event === 'add' || event === 'unlink') {
          server.ws.send({
            type: 'full-reload',
            path
          });
        }
      });
    }
  };
}

export default defineConfig({
  server: { https: true }, // Not needed for Vite 5+
  plugins: [ mkcert(), watchAllPlugin() ]
})
'''

    #with open(os.path.join(path,'package.json'), 'w') as f:
    #    json.dump(package_preset, f)
    
    with open(os.path.join(path,'vite.config.js'), 'w') as f:
        f.write(vite_config_preset)

    print("Config files created")

def play_runtime():

    print("Preview Scene")

    currentSavePath = bpy.data.filepath
    currentSaveDir = os.path.dirname(currentSavePath)
    desired_path = currentSaveDir
    #create_config_file(desired_path, "test", True, "0.0.1")
    create_main_file(desired_path)

    project_name = "nx-project"

    node_path = os.path.join(os.path.dirname(__file__), 'node', 'node.exe')
    npm_cli_path = os.path.join(os.path.dirname(__file__), 'node', 'node_modules', 'npm', 'bin', 'npx-cli.js')

    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.bat') as batch_file:
        batch_command = f'cd /d "{desired_path}\\{project_name}" && cls \n'
        batch_command += f'"{node_path}" "{npm_cli_path}" vite \n'
        batch_file.write(batch_command)
        batch_file_path = batch_file.name

    subprocess.Popen(f'cmd /k "{batch_file_path}"', cwd=desired_path, shell=True)

    webbrowser.open("http://localhost:5173/")

def get_object_matrix_y_axis(obj):
    matrix_world = obj.matrix_world

    # Create a rotation matrix (rotating -90 degrees around X-axis)
    rot_x_90 = mathutils.Matrix.Rotation(-math.pi / 2, 4, 'X')

    # Apply the rotation to the world matrix
    adjusted_matrix = rot_x_90 @ matrix_world

    # Flatten the matrix into a list
    matrix_flat = [val for row in adjusted_matrix for val in row]
    return(matrix_flat)

def compile_project_data():

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
            "scene_camera" : [],
            "scene_light" : [],
            "scene_speaker" : [],
            "scene_probes" : [],
            "scene_decals" : [],
            "scene_text" : [],
            "scene_curves" : [],
            "environment" : {
            }
        }

        #GLB GROUPS (1 per scene for now)
        glb_name = scene.name + ".glb"
        data_scene["glb_groups"].append(glb_name)

        for obj in scene.objects:

            if obj.type == "EMPTY":

                empty = {
                    "name" : obj.name,
                    "matrix" : get_object_matrix_y_axis(obj)
                }

                data_scene["scene_empty"].append(empty)

            if obj.type == "MESH":
                pass
                #LIGHTMAP TRANSFER

            if obj.type == "CAMERA":

                camera = {
                    "name" : obj.name,
                    "matrix" : get_object_matrix_y_axis(obj),
                    "fov" : obj.data.angle,
                    "clip_near" : obj.data.clip_start,
                    "clip_far" : obj.data.clip_end
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
                    "matrix" : get_object_matrix_y_axis(obj),
                    "color" : list(obj.data.color),
                    "intensity" : obj.data.energy,
                    "type" : obj.data.type,
                    "shadow" : obj.data.use_shadow,
                    "shadowBias" : obj.data.shadow_buffer_bias,
                    "contactShadow" : obj.data.use_contact_shadow
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

                speaker = {
                    "name" : obj.name,
                    "matrix" : get_object_matrix_y_axis(obj),
                    "volume" : obj.data.volume,
                    "pitch" : obj.data.pitch,
                }

                data_scene["scene_speaker"].append(speaker)

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
                                input_node = node.inputs[0].links[0].from_node

                                print("Active Environment Background Input Node: ", input_node.type)

                                if(input_node.type == "RGB"):
                                    print("BG:", "RGB")
                                    data_scene["environment"]["backgroundType"] = "color"
                                    data_scene["environment"]["backgroundColor"] = [input_node.outputs[0].default_value[0], input_node.outputs[0].default_value[1], input_node.outputs[0].default_value[2]]
                                elif(input_node.type == "TEX_ENVIRONMENT"):
                                    print("BG:", "ENVTEX")
                                    data_scene["environment"]["backgroundType"] = "texture"
                                    data_scene["environment"]["backgroundTexture"] = os.path.basename(input_node.image.filepath)
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

                                # Add additional code here if you want to do something with the node
                                break
    
    return project

def compile_scene():

    print("Compiling Scene")

    scene_glb_groups = []
    scene_empty = []
    scene_camera = []
    scene_light = []
    scene_speaker = []
    scene_probes = []
    scene_decals = []
    scene_text = []

    #Get the active environment
    current_scene = bpy.context.scene
    active_world = current_scene.world

    if active_world.use_nodes:
    # Get the node tree of the world
        print("Fetching world nodes")
        node_tree = active_world.node_tree

        # Iterate over the nodes in the node tree
        for node in node_tree.nodes:
            print("NODE A")
            print(node.type)
            
            if(node.type == "BACKGROUND"):
                print("NODE B")
                # Check if it's connected to the World Output node
                for output in node.outputs:
                    for link in output.links:
                        if isinstance(link.to_node, bpy.types.ShaderNodeOutputWorld):
                            print("Active Environment Background Node:", node.name)
                            # Add additional code here if you want to do something with the node
                            break

    environment = {
        
    }

    for obj in bpy.context.scene.objects:

        #Mesh/Objects

        if obj.type == 'EMPTY':
            scene_empty.append(obj)

        if obj.type == 'CAMERA':

            #Check if the camera is the active one in blender scene
            if obj == bpy.context.scene.camera:
                active = True
            else:
                active = False

            if obj.data.type == "PERSP":
                camType = "Perspective"
            elif obj.data.type == "ORTHO":
                camType = "Orthographic"
            else:
                camType = "Perspective"

            cam = {
                "name" : obj.name,
                "position" : obj.location,
                "rotation" : obj.rotation_euler,
                "active" : active,
                "type" : camType,
                "fov" : obj.data.angle,
                "clip_near" : obj.data.clip_start,
                "clip_far" : obj.data.clip_end
            }

            scene_camera.append(cam)

        if obj.type == 'LIGHT':

            light = {
                "name" : obj.name,
                "position" : obj.location,
                "rotation" : obj.rotation_euler,
                "color" : tuple(obj.data.color),
                "intensity" : obj.data.energy,
                "type" : obj.data.type,
                "shadow" : obj.data.use_shadow,
                "shadowBias" : obj.data.shadow_buffer_bias,
                "contactShadow" : obj.data.use_contact_shadow
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

                light["areaSize"] = obj.data.size

            scene_light.append(light)

        if obj.type == 'SPEAKER':

            speaker = {
                "name" : obj.name,
                "position" : obj.location,
                "rotation" : obj.rotation_euler,
                "volume" : obj.data.volume,
                "pitch" : obj.data.pitch,
            }

            scene_speaker.append(speaker)

        if obj.type == 'LIGHT_Probe':
            scene_probes.append("UNSUPPORTED")

        if obj.type == 'FONT':
            scene_text.append("UNSUPPORTED")

    scene_data = {

        "environment" : environment,
        "glb_groups" : scene_glb_groups,
        "empties" : scene_empty,
        "cameras" : scene_camera,
        "lights" : scene_light,  
        "speakers" : scene_speaker,
        "probes" : scene_probes,
        "decals" : scene_decals,
        "text" : scene_text
    }

    #Convert all vectors to json compatible tuples
    for obj in scene_data["empties"]:
        obj["position"] = tuple(obj["position"])
        obj["rotation"] = tuple(obj["rotation"])

    for obj in scene_data["cameras"]:
        obj["position"] = tuple(obj["position"])
        obj["rotation"] = tuple(obj["rotation"])
    
    for obj in scene_data["lights"]:
        obj["position"] = tuple(obj["position"])
        obj["rotation"] = tuple(obj["rotation"])
    
    for obj in scene_data["speakers"]:
        obj["position"] = tuple(obj["position"])
        obj["rotation"] = tuple(obj["rotation"])
    
    for obj in scene_data["probes"]:
        obj["position"] = tuple(obj["position"])
        obj["rotation"] = tuple(obj["rotation"])

    return scene_data

def create_main_file(path):

    path = os.path.join(path, "nx-project")

    main_content = '''
    import * as THREE from 'three';
    import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
    import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
    import {DRACOLoader} from 'three/addons/loaders/DRACOLoader.js';
    import {RGBELoader} from 'three/addons/loaders/RGBELoader.js';
    import { VRButton } from "three/addons/webxr/VRButton.js";

    import data from './scene_manifest.json';

    //console.log(data);

    let camera, scene, renderer, composer, mixer, clock, bloomPass, outputPass;

    const envLoader = new RGBELoader();
    const loader = new GLTFLoader();

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize( window.innerWidth, window.innerHeight );
    renderer.physicallyCorrectLights = true;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap; // default THREE.PCFShadowMap
    document.body.appendChild( renderer.domElement );

    scene = new THREE.Scene();

    for (const [key, value] of Object.entries(data)) {
    
        const arr = Array.from(value);
    
        arr.forEach((obj) => {
            
            if(key == "cameras"){
                
                console.log(obj);
                let cam = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, obj["clip_near"], obj["clip_far"]);
                cam.position.set(obj["position"][0], obj["position"][2], -obj["position"][1]);
                cam.rotation.set(obj["rotation"][0], obj["rotation"][2], -obj["rotation"][1]);

                scene.add(cam);

                if(obj["active"]){
                    camera = cam;
                    let controls = new OrbitControls(cam, renderer.domElement);
                }

            }

            if(key == "lights"){
                
                console.log(obj);

                if(obj["type"] == "POINT"){

                    let light = new THREE.PointLight( 0xFFFFFF, obj["intensity"]/10 );
                    light.position.set(obj["position"][0], obj["position"][2], -obj["position"][1]);
                    light.rotation.set(obj["rotation"][0], obj["rotation"][2], -obj["rotation"][1]);


                    if(obj["shadow"] == true){
                        light.castShadow = true;
                        light.shadow.mapSize.width = 1024;
                        light.shadow.mapSize.height = 1024;
                        light.shadow.camera.near = 0.5;
                        light.shadow.camera.far = 500.0;
                        const helper = new THREE.CameraHelper( light.shadow.camera );
                        scene.add( helper );
                    }

                    scene.add(light);

                }

                if(obj["type"] == "SPOT"){

                    const light = new THREE.SpotLight( 0xffffff, obj["intensity"]/10 );
                    light.position.set(obj["position"][0], obj["position"][2], -obj["position"][1]);
                    light.rotation.set(obj["rotation"][0], obj["rotation"][2], -obj["rotation"][1]);
                    light.angle = Math.cos(obj["spotSize"]/2);
                    light.penumbra = obj["spotBlend"];
                    light.decay = 2;
                    light.distance = 0;

                    if(obj["shadow"] == true){
                        light.castShadow = true;
                        light.shadow.mapSize.width = 1024;
                        light.shadow.mapSize.height = 1024;
                
                        const spotlightAngleDegrees = light.angle * 180 / Math.PI;
                        light.shadow.camera.fov = spotlightAngleDegrees;
                
                        light.shadow.camera.near = 0.05;
                        light.shadow.camera.far = 10;
                        light.shadow.bias = -0.005;
                        
                    }

                    scene.add(light);
                    const helper = new THREE.CameraHelper( light.shadow.camera );
                    scene.add( helper );
                    //Do nothing yet
                }


            }

        })
    
        if(key == "glb_groups"){
            //Do nothing yet
        }

        if(key == "empties"){
            //Do nothing yet
        }
    
        //console.log(key, value);


    }

    //camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 0.1, 1000 );
    //camera.position.z = -5;
    scene.background = new THREE.Color( 0xFFFFFF );

    //const light = new THREE.AmbientLight( 0xFFFFFF ); // soft white light
    //scene.add( light );

    //controls = new OrbitControls( camera, renderer.domElement );

    const geometry = new THREE.BoxGeometry( 1, 1, 1 );
    const material = new THREE.MeshBasicMaterial( { color: 0x00ff00 } );
    const cube = new THREE.Mesh( geometry, material );
    //scene.add( cube );

    //renderer.toneMapping = THREE.ACESFilmicToneMapping;
    //renderer.toneMappingExposure = 1.0;
    //renderer.outputEncoding = THREE.sRGBEncoding

    loader.load("NX.glb",
        function (gltf) {
            const model = gltf.scene;
            model.traverse(function (child) {
                if (child.isMesh) {
                    child.castShadow = true;
                    child.receiveShadow = true;
                }

                if (child.isMesh && child.material) {
                    const materials = Array.isArray(child.material) ? child.material : [child.material];
                    
                    materials.forEach(material => {
                        if (material.map) {
                            material.map.anisotropy = renderer.capabilities.getMaxAnisotropy();
                            console.log("Material map anisotropy: " + material.map.anisotropy);
                        }
                    });
                }

            });

            scene.add(model);
            console.log("Loaded GLB");
            console.log(scene);
            animate();
        },
        undefined,
        function (error) {
            console.error(error);
        }
    );

    function animate() {
        requestAnimationFrame( animate );

        cube.rotation.x += 0.01;
        cube.rotation.y += 0.01;

        renderer.render( scene, camera );
    }

    //animate();
'''

    index_content = '''
<!DOCTYPE html>
<html lang="en">
	<head>
		<meta charset="utf-8">
		<title>NX Project</title>
		<style>
			body { margin: 0; }
		</style>
	</head>
	<body>
		<script type="module" src="/main.js"></script>
	</body>
</html>
'''

    with open(os.path.join(path,'main.js'), 'w') as f:
        f.write(main_content)

    with open(os.path.join(path,'index.html'), 'w') as f:
        f.write(index_content)

    print("Index files created")

def create_glb_file(path):
    path = os.path.join(path, "nx-project",'NX.glb')

    bpy.ops.export_scene.gltf(
            export_format="GLB",
            export_draco_mesh_compression_enable=False,
            export_apply=True,
            export_original_specular=True,
            use_visible=True,
            use_renderable=True,
            use_active_scene=True,
            export_yup=True,
            filepath=path)
    
    print("GLB Created")

def create_scene_manifest():
    data = compile_scene()

    with open(os.path.join(os.path.dirname(bpy.data.filepath), "nx-project", "scene_manifest.json"), 'w') as f:
        json.dump(data, f)

    print("Scene Manifest Created")

def copy_nx_engine():
    pass

#endregion

#region operators
class NX_Test(bpy.types.Operator):
    bl_idname = "nx.test"
    bl_label = "Generate Project"
    bl_description = "Test"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        project_name = "nx-project"
        currentSavePath = bpy.data.filepath
        currentSaveDir = os.path.dirname(currentSavePath)
        desired_path = currentSaveDir

        os.chdir(currentSaveDir)
        if(os.path.exists(project_name)):
            shutil.rmtree(project_name)
        os.mkdir(project_name)

        create_glb_file(desired_path)
        create_scene_manifest()

        process_thread = threading.Thread(target=self.run_subprocess, args=(self.on_subprocess_complete,))
        process_thread.start()

        return {"FINISHED"}

    def run_subprocess(self, callback):
        print("Test")

        if not is_node_installed():
            print("Node.js/NPM is not installed.")
            return {"CANCELLED"}
        else:

            currentSavePath = bpy.data.filepath
            currentSaveDir = os.path.dirname(currentSavePath)

            project_name = "nx-project"
            desired_path = currentSaveDir  # Set your desired path here

            node_path = os.path.join(os.path.dirname(__file__), 'node', 'node.exe')
            npm_cli_path = os.path.join(os.path.dirname(__file__), 'node', 'node_modules', 'npm', 'bin', 'npm-cli.js')

            with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.bat') as batch_file:
                batch_command = f'cd /d "{desired_path}" && cls \n'
                #batch_command += f'"{node_path}" "{npm_cli_path}" create vite@latest {project_name} -- --template vanilla && cls && cd {project_name} && cls && npm install --save three && npm i vite-plugin-mkcert -D && cls && npm install && cls && exit \n'
                batch_command += f'cd {project_name} && "{node_path}" "{npm_cli_path}" install --save three && npm install --save-dev vite && npm i vite-plugin-mkcert -D && exit \n'
                batch_file.write(batch_command)
                batch_file_path = batch_file.name

            if sys.platform == "win32":
                try:
                    process = subprocess.Popen(f'cmd /k "{batch_file_path}"', cwd=desired_path, shell=True)
                    process.wait()  # Wait for the subprocess to complete
                except Exception as e:
                    print(f"Error running batch file: {e}")

            # Call the callback once subprocess is complete
            callback()

    def on_subprocess_complete(self):
        pass
        # currentSavePath = bpy.data.filepath
        # currentSaveDir = os.path.dirname(currentSavePath)
        # desired_path = currentSaveDir
        # #create_config_file(desired_path, "test", True, "0.0.1")
        # create_main_file(desired_path)

        # project_name = "nx-project"

        # node_path = os.path.join(os.path.dirname(__file__), 'node', 'node.exe')
        # npm_cli_path = os.path.join(os.path.dirname(__file__), 'node', 'node_modules', 'npm', 'bin', 'npx-cli.js')

        # with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.bat') as batch_file:
        #     batch_command = f'cd /d "{desired_path}\\{project_name}" && cls \n'
        #     batch_command += f'"{node_path}" "{npm_cli_path}" vite \n'
        #     batch_file.write(batch_command)
        #     batch_file_path = batch_file.name

        # subprocess.Popen(f'cmd /k "{batch_file_path}"', cwd=desired_path, shell=True)

        # webbrowser.open("http://localhost:5173/")

        # project_name = "nx-project"

        # node_path = os.path.join(os.path.dirname(__file__), 'node', 'node.exe')
        # npm_cli_path = os.path.join(os.path.dirname(__file__), 'node', 'node_modules', 'npm', 'bin', 'npm-cli.js')

        # with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.bat') as batch_file:
        #     batch_command = f'cd /d "{desired_path}\\{project_name}" && cls \n'
        #     batch_command += f'"{node_path}" "{npm_cli_path}" run dev \n'
        #     batch_file.write(batch_command)
        #     batch_file_path = batch_file.name

        # subprocess.Popen(f'cmd /k "{batch_file_path}"', cwd=desired_path, shell=True)

class NX_Compile(bpy.types.Operator):
    bl_idname = "nx.compile"
    bl_label = "Compile scene"
    bl_description = "Compile the scene"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        compiled = json.dumps(compile_project_data())
        print(compiled)


        return {"FINISHED"}

class NX_Play(bpy.types.Operator):
    bl_idname = "nx.play"
    bl_label = "Start player"
    bl_description = "Preview the scene in the browser"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        print("Preview Scene")
        play_runtime()

        return {"FINISHED"}
    
class NX_Stop(bpy.types.Operator):
    bl_idname = "nx.stop"
    bl_label = "Stop player"
    bl_description = "Preview the scene in the browser"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        print("Preview Scene")
        stop_runtime()

        return {"FINISHED"}

class NX_Update(bpy.types.Operator):
    bl_idname = "nx.update"
    bl_label = "Update scene"
    bl_description = "Update the scene in the browser"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        currentSavePath = bpy.data.filepath
        currentSaveDir = os.path.dirname(currentSavePath)
        desired_path = currentSaveDir

        create_glb_file(desired_path)
        create_scene_manifest()

        return {"FINISHED"}

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
    
#endregion
    
#region UIList
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

#endregion

#region panel
class NX_PT_Panel(bpy.types.Panel):
    bl_label = "NX Exporter"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.use_property_split = True
        layout.use_property_decorate = False

        file_path = bpy.data.filepath

        # Check if the file has been saved
        if file_path:
            row = layout.row(align=True)
            #Here we check if 
            if is_generated_project_present():

                row.label(text="NX Play")
                row = layout.row(align=True)
                row.operator("nx.play", text="Play", icon="PLAY")
                row = layout.row(align=True)
                row.operator("nx.update", text="Update", icon="PLAY")

            else:

                row.label(text="Local project files needs to be generated first")
                row = layout.row(align=True)
                row.operator("nx.test", text="Generate Project")

        else:
            row = layout.row(align=True)
            row.label(text="Please save your project")

class NX_PT_Settings(bpy.types.Panel):
    bl_label = "Settings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "NX_PT_Panel"

    @classmethod
    def poll(cls, context):
        file_path = bpy.data.filepath

        # Check if the file has been saved
        return bool(file_path)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.use_property_split = True
        layout.use_property_decorate = False

        row = layout.row(align=True)
        row.label(text="Environment:", icon="WORLD")
        row = layout.row(align=True)
        row.operator("nx.compile")

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
        row.operator("nx.test")
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

#endregion

#region class-registration
classes = [NX_Preview, NX_PreviewVR, NX_AutoUV, SCENE_PT_NX_panel, NX_UL_PostprocessStack, NX_Test, NX_PT_Panel, NX_PT_Settings, NX_Play, NX_Update, NX_Compile]

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

#endregion