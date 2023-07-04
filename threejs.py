import bpy, os, sys, time, webbrowser, subprocess, shutil, math, mathutils, json
from http.server import HTTPServer, SimpleHTTPRequestHandler

process = None

def run(vr):

    global process

    if process!= None:
        #TODO - Future: Instead of terminating, cast a signal to reload existing page
        end()

    filename=bpy.path.basename(bpy.context.blend_data.filepath)[:-6]

    out_path=bpy.path.abspath("//HTML5\\"+filename+".glb")

    os.makedirs(bpy.path.abspath("//HTML5"), exist_ok=True)

    addDebug=bpy.context.scene.nx_add_inspector

    if bpy.context.scene.nx_environment_file != "":
        envPath=bpy.context.scene.nx_environment_file
        environmentPart="""var envTexture = new BABYLON.HDRCubeTexture("Bundled/"""+envPath+"""", scene, 256, false, true, false, true);"""
    else:
        envPath="null"
        environmentPart="var envTexture = null;"

    if bpy.context.scene.nx_lightmap_file != "":
        lmPath=bpy.context.scene.nx_lightmap_file

        print(lmPath)

        if os.path.exists(bpy.path.abspath(lmPath)):
            with open(bpy.path.abspath(lmPath)) as f:
                lightmapSet = json.load(f)
                lightmapPart = "var lightmapSet = " + json.dumps(lightmapSet, indent = 4)
        else:
            lightmapPart="var lightmapSet = null;"

    else:
        lmPath="null"
        lightmapPart="var lightmapSet = null;"
        
    if vr:
        pipelineVR="""
        document.body.appendChild( VRButton.createButton( renderer ) );
        renderer.xr.enabled = true;
        var vr = true;
    """
    else:
        pipelineVR="var vr = false;"

    convertMaterials=False

    if convertMaterials:
        bpy.data.materials.new(name="B2AGrey")
        for obj in bpy.context.scene.objects:

            if obj.type == "MESH":

                print("Replacing for object: " + obj.name)

                if len(obj.material_slots) < 1:

                    print("Object has no material")
                    obj.data.materials.append(bpy.data.materials["B2AGrey"])

                else:
                
                    for slots in obj.material_slots:

                        mat = slots.material

                        mat.use_nodes = True
                        
                        for node in mat.node_tree.nodes:
                            
                            if node.type == "BSDF_PRINCIPLED":
                                
                                node.inputs.get("Base Color").default_value = mat.diffuse_color
                                
                                node.inputs.get("Specular").default_value = 0.0
                                
                                node.inputs.get("Roughness").default_value = mat.roughness

                                if node.inputs.get("Base Color").default_value[3] < 0.99:
                                    
                                    mat.blend_method = "BLEND"
                                    mat.shadow_method = "CLIP"

                                    node.inputs.get("Alpha").default_value = node.inputs.get("Base Color").default_value[3]

    bpy.ops.export_scene.gltf(
                export_format="GLB",
                export_draco_mesh_compression_enable=False,
                export_apply=True,
                export_original_specular=True,
                use_visible=True,
                use_renderable=True,
                use_active_scene=True,
                export_yup=True,
                filepath=out_path)

    mainCamLocation=[0,0,0]
    mainCamRotation="0,0,0"
    mainCamFOV = 20
    mainCamClipStart = "0.1"
    mainCamClipEnd = "100"
    mainCamTarget = [0,0,0]

    #If the active scene has a camera, use it"s location. Also use Y+ as up per gltf spec. The rotation is in degrees
    if bpy.context.scene.camera != None:
        mainCamLocation = [bpy.context.scene.camera.location.x,bpy.context.scene.camera.location.z,bpy.context.scene.camera.location.y]
        mainCamRotation = [bpy.context.scene.camera.rotation_euler.x * math.pi / 180,bpy.context.scene.camera.rotation_euler.z * math.pi / 180,bpy.context.scene.camera.rotation_euler.y * math.pi / 180] #))/180*math.pi) + "," + str(-(math.degrees(bpy.context.scene.camera.rotation_euler.z))/180*math.pi) + "," + str((180-math.degrees(bpy.context.scene.camera.rotation_euler.y))/180*math.pi)
        mainCamFOV = math.degrees(bpy.context.scene.camera.data.angle)
        mainCamClipStart = str(bpy.context.scene.camera.data.clip_start)
        mainCamClipEnd = str(bpy.context.scene.camera.data.clip_end)

        targetVector = bpy.context.scene.camera.matrix_world.to_quaternion() @ mathutils.Vector((0, 0, -1))
        mainCamTarget = [targetVector[0], targetVector[2], targetVector[1]]

    print(mainCamRotation)
    #Create a string containing the debugLayer.show() command if we want to show the debug layer

    debugVal = ""
    if addDebug:
        debugVal = "scene.debugLayer.show();"

    #HTML_Sections (htmlmaker.py)
    #Sections:
        #Header (Title + Optional stylesheet)
        #Libraries and extensions (GUI Library, RGBD/RGBE loader)
        #Scene Engine
        #Runtime-Footer

    #Create a file
    htmlScript="""
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>NX Exporter</title>
  <style>
    body { margin: 0; }
    canvas { width: 100%; height: 100% }
  </style>
  <!--  Three.js CDN  -->
<script async src="https://unpkg.com/es-module-shims@1.6.3/dist/es-module-shims.js"></script>

<script type="importmap">
  {
    "imports": {
      "three": "https://unpkg.com/three@0.145.0/build/three.module.js",
      "three/addons/": "https://unpkg.com/three@0.145.0/examples/jsm/",
      "postprocessing": "https://cdn.jsdelivr.net/npm/postprocessing@6.30.0/build/postprocessing.esm.js"
    }
  }
</script>
</head>
<body>
  <!--  Our code  -->
  <script type="module" src="app.js"></script>
</body>
</html>
    """

    appScript="""
// ------------------------------------------------
// BASIC SETUP
// ------------------------------------------------

import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {TWEEN} from 'three/addons/libs/tween.module.min.js';
import {DRACOLoader} from 'three/addons/loaders/DRACOLoader.js';
import {RGBELoader} from 'three/addons/loaders/RGBELoader.js';
import { VRButton } from "three/addons/webxr/VRButton.js";


import {EffectComposer, RenderPass, EffectPass, BloomEffect, SMAAPreset, SMAAEffect, ChromaticAberrationEffect} from 'postprocessing';

let camera, scene, renderer, composer, controls, mixer, clock, bloomPass, outputPass;
var parameters = {
    exposure: """+ str(bpy.data.scenes["Scene"].nx_exposure) +""",
    contrast: """+ str(bpy.data.scenes["Scene"].nx_contrast) +""",
    bloom: """+ str(bpy.data.scenes["Scene"].nx_add_bloom).lower() +""",
    antialiasing: """+ str(bpy.data.scenes["Scene"].nx_add_antialiasing).lower() +""",
    chromaticaberration: """+ str(bpy.data.scenes["Scene"].nx_add_chromaticaberration).lower() +""",
    vignette: """+ str(bpy.data.scenes["Scene"].nx_add_vignette).lower() +"""
}

init();

""" + str(pipelineVR) + """

function init(){

    renderer = new THREE.WebGLRenderer({ antialias: parameters.antialiasing});
    renderer.setPixelRatio( window.devicePixelRatio );
    renderer.setSize( window.innerWidth, window.innerHeight );
    renderer.useLegacyLights = false;
    document.body.appendChild(renderer.domElement);

    scene = new THREE.Scene();

    camera = new THREE.PerspectiveCamera("""+ str(mainCamFOV) +""", window.innerWidth / window.innerHeight, """ + mainCamClipStart + """, """ + mainCamClipEnd + """);
    //camera.position.set("""+str(mainCamLocation[0])+""","""+str(mainCamLocation[1])+""","""+str(mainCamLocation[2])+""");
    camera.position.set("""+str(mainCamLocation[0])+""","""+str(mainCamLocation[1])+""","""+str(-mainCamLocation[2])+""");
    scene.add( camera );

    const controls = new OrbitControls( camera, renderer.domElement );

    scene.add( new THREE.AmbientLight( 0xFFFFFF ) );
    
    const renderScene = new RenderPass( scene, camera );

    const envLoader = new RGBELoader();
    const loader = new GLTFLoader();

    """ + lightmapPart + """

    const scene_materials = new Set();

    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = parameters.exposure;
    renderer.outputEncoding = THREE.sRGBEncoding

    composer = new EffectComposer(renderer);
    composer.addPass(new RenderPass(scene, camera));

    const bloom = new BloomEffect();
    const smaaAliasEffect = new SMAAEffect({preset: SMAAPreset.ULTRA});
    const chromaticAberration = new ChromaticAberrationEffect({
        offset: new THREE.Vector2(0.002, 0.02),
        radialModulation: true,
        modulationOffset: 0.7,
    });
    
    composer.addPass(new EffectPass(camera, bloom, smaaAliasEffect));
    composer.addPass(new EffectPass(camera, chromaticAberration));

    //This was added to VR
    //effectPass.renderToScreen = true;
    //renderer.autoClear = false;

    //if (vr) {
    //    stereo = new THREE.StereoEffect(renderer);
    //    stereo.setSize( window.innerWidth, window.innerHeight );
    //}

    envLoader.load("/Bundled/environment.hdr", function(texture){
        texture.mapping = THREE.EquirectangularReflectionMapping;

        scene.background = texture;
        //scene.environment = texture;
        scene.backgroundBlurriness = 0.3;

        loader.load(
            "/"""+bpy.path.basename(bpy.context.blend_data.filepath)[:-6]+""".glb",
            function (gltf) {
                const model = gltf.scene;
                scene.add(model);
                //mixer = new THREE.AnimationMixer( model );
                //const clip = gltf.animations[ 0 ];
                //mixer.clipAction( clip.optimize() ).play();
                //animate();
                renderer.setAnimationLoop(render);

                scene.traverse( function( object ) {
                
                    if ( object.material ) {
                        scene_materials.add( object.material );
                    }
                    
                });

                for(let mat of scene_materials) {
                
                    console.log(mat.name);

                    //console.log(mat.name + " => " + lightmapSet[mat.name]);

                    if(lightmapSet != null){
                    
                        if(lightmapSet[mat.name] != undefined){
                            new RGBELoader().load( "/Bundled/" + lightmapSet[mat.name], function ( lmtexture ) {
                            
                                console.log("Lightmap loaded: " + mat.name);
                            
                                lmtexture.flipY = false;
                                lmtexture.channel = 1;
                                lmtexture.encoding = THREE.sRGBEncoding
                                lmtexture.wrapS = THREE.RepeatWrapping;
                                lmtexture.wrapT = THREE.RepeatWrapping;
                                mat.lightMap = lmtexture;
                                mat.lightMapIntensity = 1.0;
                                mat.needsUpdate = true;
                            
                            });
                        }

                    }

                }

                //console.log(materials);

            },
            undefined,
            function (error) {
                console.error(error);
            }
        );

    });

    window.addEventListener( 'resize', onWindowResize, false );

}

function onWindowResize() {

    const width = window.innerWidth;
    const height = window.innerHeight;

    camera.aspect = width / height;
    camera.updateProjectionMatrix();

    renderer.setSize( width, height );
    composer.setSize( width, height );

}

function render() {

    //Works in VR with no composer
    renderer.render( scene, camera );
    if (!vr) { 
        composer.render();
    } else {
        //pass => Waiting for https://github.com/mrdoob/three.js/pull/26160
    }

    //renderer.clear();
    //composer.render();

    //renderFrame = requestAnimationFrame(render);
    //if (vr) { stereo.render(scene, camera); }
    //else { renderer.render(scene, camera); }

}
"""

    with open(bpy.path.abspath("//HTML5\\index.html"),"w") as f:
        f.write(htmlScript)

    with open(bpy.path.abspath("//HTML5\\app.js"),"w") as f:
        f.write(appScript)


    python_server="""
import sys, os, time, webbrowser, subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler

os.chdir(sys.argv[1])

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        #self.send_header("Access-Control-Allow-Methods", "GET")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalnxte")
        self.extensions_map.update({
            ".js": "application/javascript",
        });
        return super(CORSRequestHandler, self).end_headers()

def func_run_server(url, port):
    httpd = HTTPServer((url, port), CORSRequestHandler)
    httpd.serve_forever()
    
func_run_server("localhost", 8080)
    """

    with open(bpy.path.abspath("//server.py"),"w") as f:
        f.write(python_server)

    #If bundled folder exists and isn"t empty
    if os.path.exists(bpy.path.abspath("//Bundled")) and os.listdir(bpy.path.abspath("//Bundled")):
        #Copy bundled and overwrite
        shutil.copytree(bpy.path.abspath("//Bundled"), bpy.path.abspath("//HTML5\\Bundled"), dirs_exist_ok=True)

    webbrowser.open("http://localhost:8080")
    pythonpath = os.path.abspath(sys.executable)
    process = subprocess.Popen([pythonpath, bpy.path.abspath("//server.py"), bpy.path.abspath("//HTML5")])

def end():
    global process
    process.terminate()
    
    #If server.py exists, delete it
    try:
        if os.path.exists(bpy.path.abspath("//server.py")):
            os.remove(bpy.path.abspath("//server.py"))
        #If folder HTML5 exists, delete it
        if os.path.exists(bpy.path.abspath("//HTML5")):
            shutil.rmtree(bpy.path.abspath("//HTML5"))
    except:
        time.sleep(2)
        if os.path.exists(bpy.path.abspath("//server.py")):
            os.remove(bpy.path.abspath("//server.py"))
        #If folder HTML5 exists, delete it
        if os.path.exists(bpy.path.abspath("//HTML5")):
            shutil.rmtree(bpy.path.abspath("//HTML5"))
    finally:
        print("Can't delete?...")

def package():

    filename=bpy.path.basename(bpy.context.blend_data.filepath)[:-6]
    out_path=bpy.path.abspath("//Package\\"+filename+".glb")
    os.makedirs(bpy.path.abspath("//Package"), exist_ok=True)
    os.makedirs(bpy.path.abspath("//Package/textures"), exist_ok=True)
    convertMaterials=False

    if convertMaterials:
        bpy.data.materials.new(name="B2AGrey")
        for obj in bpy.context.scene.objects:

            if obj.type == "MESH":

                print("Replacing for object: " + obj.name)

                if len(obj.material_slots) < 1:

                    print("Object has no material")
                    obj.data.materials.append(bpy.data.materials["B2AGrey"])

                else:
                
                    for slots in obj.material_slots:

                        mat = slots.material

                        mat.use_nodes = True
                        
                        for node in mat.node_tree.nodes:
                            
                            if node.type == "BSDF_PRINCIPLED":
                                
                                node.inputs.get("Base Color").default_value = mat.diffuse_color
                                
                                node.inputs.get("Specular").default_value = 0.0
                                
                                node.inputs.get("Roughness").default_value = mat.roughness

                                if node.inputs.get("Base Color").default_value[3] < 0.99:
                                    
                                    mat.blend_method = "BLEND"
                                    mat.shadow_method = "CLIP"

                                    node.inputs.get("Alpha").default_value = node.inputs.get("Base Color").default_value[3]

    manifest = {}
    
    bpy.ops.export_scene.gltf(
                export_format="GLB",
                export_draco_mesh_compression_enable=False,
                export_apply=True,
                export_original_specular=True,
                use_visible=True,
                use_renderable=True,
                use_active_scene=True,
                filepath=out_path)
    
    manifest["models"] = [filename + ".glb"]
    manifest["materials"] = []
    manifest["textures"] = []

    for mat in bpy.data.materials:
        if mat.name != "Dots Stroke":
            manifest["materials"].append(mat.name)
    
    for image in bpy.data.images:
        if image.size[0] != 0 or image.name != "Viewer Node":

            if image.filepath_raw.endswith(".hdr"):
                print(image.name)
                image.filepath_raw = "//Package/textures/"+image.name+".hdr"
                image.file_format = "HDR"
                image.save()
                manifest["textures"].append(image.name)
            else:
                print(image.name)
                image.filepath_raw = "//Package/textures/"+image.name+".jpg"
                image.file_format = "JPEG"
                image.save()
                manifest["textures"].append(image.name)

    def_account="Example Account"
    def_base_mesh_colour="Neutral"

    recipeDict = {}

    r_room = {
        "Name": filename,
        "slug" : filename.toLowerCase(),
        "Account" : def_account,
        "Base Mesh Colour" : def_base_mesh_colour,
        "Camera" : "Set it to whatever you like.",
        "Camera FOV" : mainCamFOV,
        "Camera Origin" : mainCamPosition,
        "Default Mesh":"---------"
    }

    r_model = {
        "Account" : def_account,
        "Default Material" : "Generic-Grey",
        "Name": filename,
        "File" : out_path,
        "Default UV Channel" : "0"
    }

    recipe = """
Recipe for CMS setup

First, create a new model
"""

    with open(bpy.path.abspath("//Package/readme.txt"),"w") as f:
        f.write("In the future, this will be a json manifest file which references all the materials and the used textures. In the future, the standard PBR setup will rely on all materials having the principled shader connected to the output node. The manifest will automatically detect these files.")
    
    with open(bpy.path.abspath("//Package/manifest.json"),"w") as f:
        f.write(str(json.dumps(manifest)))
    
    webbrowser.open(bpy.path.abspath("//Package"))
