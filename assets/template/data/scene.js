import * as THREE from 'three';
import RenderManager from './renderer';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';
import { ARButton } from 'three/addons/webxr/ARButton.js';
import Logger from './logger';
import ErrorManager from './error_manager';
import CameraManager from './camera';
import LightManager from './light';
import SpeakerManager from './speaker';
import MaterialManager from './materials';
import CurveManager from './curves';

//TODO - MAKE CONDITIONAL
import { Sky } from 'three/addons/objects/Sky.js';
import RendererManager from './renderer';

export default class SceneManager {

    //The Scene Manager prepares everything related to the scene - objects, lights, sounds, etc.

    constructor(engine, options) {

        this.engine = engine;
        this.options = options;
        this.sceneData = null;
        this.scene3D = null; //ThreeJS Scene
        this.renderer = null; //ThreeJS Renderer
        this.cameraManager = null;
        this.lightManager = null;
        this.speakerManager = null;
        this.materialManager = null;
        this.curveManager = null;
        this.mixer = null;
        this.listener = null;
        this.animations = [];
        this.sceneIDTable = {}; //Every object in scene needs one unique ID

        this.loadProgress = {
            "predefinition": 0, //Loaders, background
            "meshes" : 0, //Meshes
            "sounds" : 0, //Sounds
            "finalization" : 0 //Lights, camera, etc.
        }

    }

    //Clean scene
    cleanSceneData = () => {

        Logger.log("Cleaning scene...");

    }

    setupSceneLoaders = (engine) => {

        Logger.log("Setting up scene loaders...");

        let envLoader = new RGBELoader();
        let meshloader = new GLTFLoader();
        const draco = new DRACOLoader()
        draco.setDecoderPath('data/libs/js/draco/')
        meshloader.setDRACOLoader(draco)

        engine.loaders["RGBE"] = envLoader;
        engine.loaders["GLTF"] = meshloader;

    }

    //Loading screen
    setupLoadingScreen = () => {
        
        Logger.log("Setting up loading screen...");

        //document.writeln("Loading...");
        const loadingScreen = document.createElement("div");
        loadingScreen.id = "loader";
        const newContent = document.createTextNode("Loading - Please wait");

        loadingScreen.appendChild(newContent);
        document.body.append(loadingScreen);

    }

    removeLoadingScreen = () => {

        Logger.log("Removing loading screen...");

        document.getElementById("loader").remove();

    }

    createBackground = async(type, scene, sceneData) => {

        Logger.log("Creating background...");

        if(type === 'color'){

            Logger.log("Background type: " + type);

            let color = new THREE.Color(sceneData.environment.backgroundColor[0], sceneData.environment.backgroundColor[1], sceneData.environment.backgroundColor[2]);
            scene.background = color;
            scene.environment = color;

            let pmremGenerator = new THREE.PMREMGenerator( this.renderManager.renderer );
            scene.environment = pmremGenerator.fromScene(scene).texture;

        } else if(type === 'texture'){

            Logger.log("Background type: " + type);

            let hdrLoader = new RGBELoader();

            Logger.log("Background texture: " + "assets/" + sceneData.environment.backgroundTexture);

            let envMap = await hdrLoader.loadAsync("assets/" +sceneData.environment.backgroundTexture);
            envMap.mapping = THREE.EquirectangularReflectionMapping;

            if(!app.xr){
                scene.background = envMap;
            } else {
                scene.background = new THREE.Color(0xFFFFFF);
            }

            let pmremGenerator = new THREE.PMREMGenerator(this.renderManager.renderer);
            let envMapPMREM = pmremGenerator.fromEquirectangular(envMap).texture;
            scene.environment = envMapPMREM;
            pmremGenerator.dispose();

        } else if(type === 'sky'){

            Logger.log("Sky type: " + type);

            let sky = new Sky();
            sky.scale.setScalar( 450000 );

            scene.add( sky );
            
            let sun = new THREE.Vector3();
            
            let pmremGenerator = new THREE.PMREMGenerator( this.renderManager.renderer );

            let uniforms = sky.material.uniforms;
            uniforms[ 'turbidity' ].value = sceneData.environment.turbidity;
            uniforms[ 'rayleigh' ].value = sceneData.environment.rayleigh;
            uniforms[ 'mieCoefficient' ].value = sceneData.environment.mieCoefficient;
            uniforms[ 'mieDirectionalG' ].value = sceneData.environment.mieDirectionalG;
            
            let phi = THREE.MathUtils.degToRad( 90 - sceneData.environment.elevation );
            let theta = THREE.MathUtils.degToRad( sceneData.environment.azimuth );

            sun.setFromSphericalCoords(1, phi, theta);

            uniforms['sunPosition'].value.copy( sun );

            scene.environment = pmremGenerator.fromScene(sky).texture;

        }

    }

    loadSceneModel_onLoad = (gltf) => {
        let model = gltf.scene;

        //Set the mixer for the scene
        this.mixer = new THREE.AnimationMixer(model);


        Logger.log("Animation List:");
        Logger.log(gltf.animations);

        gltf.animations.forEach((clip) => {
            //this.mixer.clipAction(clip).play();
            this.animations.push(clip);
        });

        Logger.log("Scene model loaded - adding to 3D Scene");

        let unknown_children = [];
        let other_children = [];

        model.traverse((child) => {

            if(child.isMesh) {

                //We have a list from a projectData that we want to couple our GLB data up with
                let sceneMeshIDList = this.sceneData.scene_meshes.map(item => item.identifier);

                let child_id;

                if(child.userData.nx_id != undefined) {
    
                    child_id = child.userData.nx_id;
    
                } else {

                    //It's probably parented to an object/group - we get that instead

                    let parent = child.parent;

                    if(parent.userData.nx_id != undefined) {

                        child_id = parent.userData.nx_id;

                    } else {

                        //Log these as compile errors
                        console.log("Child with undefined ID: " + child.name + " // " + child.userData.nx_id);
                        console.log(child);
                        unknown_children.push(child);

                    }
    
                }

                child_id = Number(child_id);

                //If the child has any of the included identifiers
                if(sceneMeshIDList.includes(child_id)) {

                    let index = sceneMeshIDList.indexOf(child_id);
                    let meshData = this.sceneData.scene_meshes[index];

                    if(meshData.active_action && meshData.active_action != "none") {

                        child["default_action"] = meshData.active_action;

                    }

                    if(meshData.lightmaps) {
                        console.log("Lightmap: " + meshData.lightmaps);
                        console.log(child.material);

                        let lightmapTex = new RGBELoader();
                        lightmapTex.load("assets/Lightmaps/" + meshData.lightmaps + ".hdr", (texture) => {
                            texture.channel = 1;
                            child.material.lightMap = texture;
                            child.material.lightMap.flipY = false;
                        });

                    }

                    if(meshData.cast_shadows) {
                        child.castShadow = true;
                    }

                    if(meshData.receive_shadows) {
                        child.receiveShadow = true;
                    }

                    if(!meshData.spawn) {
                        child.visible = false;
                    }

                    if(meshData.modules.length > 0) {

                        meshData.modules.forEach((module) => {

                            this.engine.componentManager.attach(child_id, module);

                            Logger.log("Attached module: " + module + " to: " + child.name + " // " + child_id);

                        })

                    }

                } else {


                    //Log these as compile errors
                    console.log("Child with undefined ID: " + child.name + " // " + child.userData.nx_id);
                    console.log(child);
                    unknown_children.push(child);

                }

            } else if (child.isGroup && child.name != "Scene") {

                let sceneMeshIDList = this.sceneData.scene_meshes.map(item => item.identifier);

                let child_id;

                if(child.userData.nx_id != undefined) {
    
                    child_id = child.userData.nx_id;
    
                } else {

                    //It's probably parented to an object/group - we get that instead

                    let parent = child.parent;

                    if(parent) {

                        if(parent.userData.nx_id != undefined) {
                            child_id = parent.userData.nx_id;
                        } else {
                            //Log these as compile errors
                            console.log("Child with undefined ID: " + child.name + " // " + child.userData.nx_id);
                            console.log(child);
                            unknown_children.push(child);
                        }

                        

                    } else {

                        //Log these as compile errors
                        console.log("Child with undefined ID: " + child.name + " // " + child.userData.nx_id);
                        console.log(child);
                        unknown_children.push(child);

                    }
    
                }

                child_id = Number(child_id);

                if(sceneMeshIDList.includes(child_id)) {

                    let index = sceneMeshIDList.indexOf(child_id);
                    let meshData = this.sceneData.scene_meshes[index];

                    if(meshData.active_action && meshData.active_action != "none") {

                        child["default_action"] = meshData.active_action;

                    }

                    if(meshData.cast_shadows) {
                        child.castShadow = true;
                    }

                    if(meshData.receive_shadows) {
                        child.receiveShadow = true;
                    }

                    if(!meshData.spawn) {
                        child.visible = false;
                    }

                    if(meshData.modules.length > 0) {

                        meshData.modules.forEach((module) => {

                            this.engine.componentManager.attach(child_id, module);

                            Logger.log("Attached module: " + module + " to: " + child.name + " // " + child_id);

                        })

                    }

                } else {


                    //Log these as compile errors
                    console.log("Child with undefined ID: " + child.name + " // " + child.userData.nx_id);
                    console.log(child);
                    unknown_children.push(child);

                }

            } else {

                //We also want to fetch empties objects from Blender (non-meshes)

                other_children.push(child);

            }

        });

        Logger.log("Unknown children (mesh): " + unknown_children.length);
        Logger.log(unknown_children);
        Logger.log("Other children: " + other_children.length);
        Logger.log(other_children);

        other_children.forEach((child) => {
                    
            let sceneEmptyIDList = this.sceneData.scene_empties.map(item => item.identifier);

            let child_id;

            if(child.userData.nx_id) {

                child_id = child.userData.nx_id;

            }

            if(sceneEmptyIDList.includes(child_id)) {

                
                //Logger.log("Found ID: " + child_id + " to: " + child.name);

                let index = sceneEmptyIDList.indexOf(child_id);

                let emptyData = this.sceneData.scene_empties[index];

                if(emptyData.active_action && emptyData.active_action != "none") {

                    child["default_action"] = emptyData.active_action;

                }

                if(emptyData.modules.length > 0) {

                    emptyData.modules.forEach((module) => {

                        this.engine.componentManager.attach(child_id, module);

                        Logger.log("Attached module: " + module + " to: " + child.name + " // " + child_id);

                    })

                }

            }

        })

        this.scene3D.add(model);
    }

    loadSceneModel_onProgress = (request) => {
        console.log(request);
        //TODO
    }

    loadSceneModel_onError = (error) => {
        console.log(error);
        //ErrorManager.catchError(error);
    }

    loadSceneModel = (sceneData) => {
        return new Promise((resolve, reject) => {
            Logger.log("Loading scene model...");
    
            let glb_assembly = "assets/" + sceneData.glb_groups[0];

            let loader = this.engine.loaders["GLTF"];
    
            loader.load (glb_assembly,

                (gltf) => {
                    this.loadSceneModel_onLoad(gltf);
                    resolve(gltf); // Resolve the promise when the model is loaded
                },

                this.loadSceneModel_onProgress,

                (error) => {
                    this.loadSceneModel_onError(error);
                    reject(error); // Reject the promise on error
                }

            );
        });
    }
    

    loadScene = async (sceneData) => {

        Logger.log(sceneData);

        this.cleanSceneData();
        this.sceneData = sceneData;
        this.setupLoadingScreen();
        this.setupSceneLoaders(this.engine);

        this.scene3D = new THREE.Scene();
        this.scene3D.userData.nx_id = 0;
        this.scene3D.autoUpdate = false;

        this.renderManager = new RenderManager(this.scene3D, this.options);

        await this.createBackground(sceneData.environment.backgroundType, this.scene3D, sceneData);
        await this.loadSceneModel(sceneData);

        this.cameraManager = new CameraManager(this.engine, this.renderer, this.scene3D, sceneData.scene_cameras);
        this.cameraManager.setupCameras();

        this.lightManager = new LightManager(this.renderer, this.scene3D, sceneData.scene_lights);
        this.lightManager.setupLights();

        this.speakerManager = new SpeakerManager(this.engine, this.scene3D, sceneData.scene_speakers);
        this.speakerManager.setupSpeakers();

        this.materialManager = new MaterialManager();
        this.materialManager.init();
        this.materialManager.storeSceneMaterials(this.scene3D);

        //this.curveManager = new CurveManager(this.engine, this.scene3D, sceneData.scene_curves);
        //this.curveManager.setupCurves(this.scene3D);

        //if(this.sceneData) {
        //    this.renderManager.createComposer();
        //}

        if(this.options.xr){
            this.renderManager.renderer.xr.enabled = true;
            document.body.appendChild( ARButton.createButton( this.renderManager.renderer ) );
        }

        
        if(this.renderManager.composerFlag){
            this.renderManager.createComposer();
        }

        this.removeLoadingScreen();

        return this.renderManager;

    }

}