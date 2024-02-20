import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { FlyControls } from 'three/addons/controls/FlyControls.js';
import { FirstPersonControls } from 'three/addons/controls/FirstPersonControls.js';
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';
import { VRButton } from "three/addons/webxr/VRButton.js";
import { RectAreaLightHelper }  from 'three/addons/helpers/RectAreaLightHelper.js';
import { PositionalAudioHelper } from 'three/addons/helpers/PositionalAudioHelper.js';
import { RectAreaLightUniformsLib } from 'three/addons/lights/RectAreaLightUniformsLib.js';
import { Sky } from 'three/addons/objects/Sky.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { FXAAShader } from 'three/addons/shaders/FXAAShader.js';

let moveForward = false;
let moveBackward = false;
let moveLeft = false;
let moveRight = false;
let moveUp = false;
let moveDown = false;

const velocity = new THREE.Vector3();
const direction = new THREE.Vector3();

export class Engine {
    constructor(project){
        this.project = project;
        this.projectData = null;
        this.projectManifest = null;
        this.debug = false;
        this.activeCamera = null;
        this.renderer = null;
        this.animate = this.animate.bind(this);
        this.scene = null;
        this.controls = null;
        this.AECViewer = false;
        this.geometricCenter = new THREE.Vector3();
        this.mixer = null;
        this.clock = null;
        this.components = [];
        this.modules = {};
        this.cubeCamera = null;
        this.cubeEnvSetup = false;
        this.listener = null;
        this.dynamicSetup = false;
    }

    //init().then(animate);

    async init () {

        this.projectData = await Utility.loadProject(this.project);
        this.projectManifest = this.projectData.manifest;
        this.clock = new THREE.Clock();

        if(!this.projectData) {
            alert('Project not found');
            return;
        } else {

            document.title = this.projectData.name;

            if(this.projectData.manifest.scenes < 1){

                showProjectDataError();

            } else {

                if(this.debug){
                    console.log("Manifest contains " + this.projectData.manifest.scenes.length + " scenes.");
                }

                //0 is the first scene
                await this.loadSceneByIndex(this, 0);

            }

        }

        if(this.debug){
            console.log(this.projectData)
        }

    }

    async loadSceneByIndex(engine, index){

        let sceneData = engine.projectManifest.scenes[index];

        if(this.debug){
            console.log(sceneData);
        }

        //Look into https://discourse.threejs.org/t/performant-soft-shadows-three-js/27777/13
        //https://raw.githack.com/donmccurdy/three.js/feat-lightprobevolume-build/examples/index.html?q=volume#webgl_lightprobe_volume

        this.renderer = this.createRenderer();
        document.body.appendChild( this.renderer.domElement );

        //Create scene
        this.scene = new THREE.Scene();
        this.createBackground(sceneData.environment.backgroundType, this.scene, sceneData);

        //Create loaders
        let envLoader = new RGBELoader();
        let loader = new GLTFLoader();
        const draco = new DRACOLoader()
        draco.setDecoderPath('data/libs/js/draco/')
        loader.setDRACOLoader(draco)

        //TODO - RESET THE ENGINE PROPERTIES WHEN LOADING A NEW SCENE

        //Load scene
        let glb_assembly = "assets/" + sceneData.glb_groups[0];

        if(this.debug){
            console.log("Loading file: " + glb_assembly);
        }

        await loader.load(glb_assembly,
            (gltf) => {
                let model = gltf.scene;
                
                model.traverse((child) => {
                    if(child.isMesh) {


                        if(this.debug){
                            console.log(child.userData.nx_id);

                            let sceneMeshList = sceneData.scene_meshes.map(item => item.identifier);

                        }

                        
                        let sceneMeshList = sceneData.scene_meshes.map(item => item.identifier);

                        let name;
                        if(child.userData.nx_id){
                            name = child.userData.nx_id;    
                        } else {
                            console.log("ERROR! Not found: " + child.name + " // " + child.userData.nx_id);
                        }
                        
                        if(sceneMeshList.includes(name)) {
                            let index = sceneMeshList.indexOf(name);
                            let meshData = sceneData.scene_meshes[index];
        
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

                                    this.modules[name] = module;

                                    if(this.debug) {
                                        console.log(module);
                                    }
                                })
                            }

                            if(meshData.object_status === "Dynamic") {
                                if(!this.dynamicSetup){

                                    if(this.debug) {
                                        console.log("Dynamic setup: " + name);
                                    }

                                    this.dynamicSetup = true;
                                }

                            } else {
                                //Move this to be further down the process
                                //child.matrixAutoUpdate = false;
                            }

                        } else {
                            if(this.debug) {
                                console.log("Not found mesh: " + name);
                                console.log(child);
                            }
                        }
                        

                    }
                });

                this.scene.add(model);

                if(this.dynamicSetup) {
                    this.mixer = new THREE.AnimationMixer(model);
                    if(gltf.animations.length > 0){
                        this.mixer.clipAction(gltf.animations[0]).play();
                    }
                }

                if(this.AECViewer){
                    let box = new THREE.Box3().setFromObject(model);
                    this.geometricCenter = box.getCenter(new THREE.Vector3());
                }

                //this.rotateObj = Utility.findObjectByName(this.scene, "CC");
                //console.log(this.rotateObj)

                this.setupScene(sceneData);

            },
            undefined,
            function (error) {
                console.error(error);
            }
        );

        window.addEventListener( 'resize', this.onWindowResize );
        window.addEventListener('click', this.onClickContext);
        window.addEventListener('touchstart', this.onClickContext);

    }

    setupScene = (sceneData) => {

        //Create cameras
        this.createCameras(sceneData);

        //Create lights
        this.createLights(this.scene, sceneData, this);

        //Create speakers
        this.createSpeakers(this.scene, sceneData, this);

        //Initialize components

        console.log(this.modules);

        Object.entries(this.modules).forEach(async ([key, value]) => {

            let objectId = key;
            let module = value;

            console.log(objectId, module);

            let object = Utility.findObjectById(this.scene, objectId);

            console.log("/////////");
            console.log(object);

            if(!object) {
                return;
            } else {
                let moduleComponent = await Utility.loadComponent(object, module);

                if(this.debug) {
                    console.log("Loaded modulex");
                    console.log(moduleComponent);
                }

                this.components.push(moduleComponent);
            }

        })
        //this.components.forEach(component => component.NotifyOnInit());

        //let cubeRenderTarget = new THREE.WebGLCubeRenderTarget( 256 );
		
        //cubeRenderTarget.texture.type = THREE.HalfFloatType;

		//this.cubeCamera = new THREE.CubeCamera( 1, 1000, cubeRenderTarget );

        this.scene.traverse(function (object) {
            if (object.material) {
                if (Array.isArray(object.material)) {
                    object.material.forEach(function (material) {
                        //material.envMap = cubeRenderTarget.texture;
                        if (material.map) {
                            material.map.anisotropy = Math.min(16, this.renderer.capabilities.getMaxAnisotropy());
                            material.map.needsUpdate = true;
                            //material.envMapIntensity = 1.0;
                        }
                    });
                } else {
                    //object.material.envMap = cubeRenderTarget.texture;
                    if (object.material.map) {
                        object.material.map.anisotropy = Math.min(16, 16);
                        object.material.map.needsUpdate = true;
                        //object.material.envMapIntensity = 1.0;
                    }
                    //let material = object.material;
                    //if (material.map) {
                    //    material.map.anisotropy = Math.min(16, this.renderer.capabilities.getMaxAnisotropy());
                    //    material.map.needsUpdate = true;
                    //}
                }
            }
        });

        //this.cubeCamera.update( this.renderer, this.scene );

        this.animate();
    }

    onWindowResize = () => {

        this.activeCamera.aspect = window.innerWidth / window.innerHeight;
        this.activeCamera.updateProjectionMatrix();

        this.renderer.setSize( window.innerWidth, window.innerHeight );
        //Composer?

    }
    
    onClickContext = () => {

        if (this.listener.context.state === 'suspended') {
            this.listener.context.resume().then(() => {
                console.log('AudioContext resumed!');
                // Now you can play your audio
            });
        }

        document.removeEventListener('click', this.onClickContext);
        document.removeEventListener('touchstart', this.onClickContext);
    }

    animate = () => {
        requestAnimationFrame(this.animate);

        //if(!this.cubeEnvSetup){
        //    this.cubeCamera.update( this.renderer, this.scene );
        //    this.cubeEnvSetup = true;
        //}

        const delta = this.clock.getDelta();

        //if(this.mixer !== null){
        //    this.mixer.update(delta);
        //}
        this.mixer.update( delta );

        //console.log(this.controls.isLocked);

/*         if ( this.controls.isLocked === true ) {
            const delta = 0.01;
        
            velocity.x -= velocity.x * 10.0 * delta;
            velocity.y -= velocity.y * 10.0 * delta;
            velocity.z -= velocity.z * 10.0 * delta;
        
            direction.z = Number( moveForward ) - Number( moveBackward );
            direction.x = Number( moveRight ) - Number( moveLeft );
            direction.y = Number( moveUp ) - Number( moveDown );
            direction.normalize(); // this ensures consistent movements in all directions
        
            if ( moveForward || moveBackward ) velocity.z -= direction.z * 400.0 * delta;
            if ( moveLeft || moveRight ) velocity.x -= direction.x * 400.0 * delta;
            if ( moveUp || moveDown ) velocity.y -= direction.y * 400.0 * delta;
        
            this.controls.moveRight( - velocity.x * delta );
            this.controls.moveForward( - velocity.z * delta );
            this.controls.getObject().position.y += velocity.y * delta; // apply the y-axis movement

        }   */      

		this.controls.update();
        this.components.forEach(component => component.NotifyOnUpdate());
    
        if (this.scene && this.activeCamera) {
            this.renderer.render(this.scene, this.activeCamera);
        }

        //this.rotateObj.rotateY(0.01);

    }

    createRenderer(type){
        //TODO: Support for WebGPU, antialias argument and custom dimensions, custom shadow type
        let renderer = new THREE.WebGLRenderer({ antialias: this.projectData.options.graphics.antialiasing });
        //let renderer = new THREE.WebGLRenderer({ antialias: false });
        renderer.setPixelRatio(window.devicePixelRatio * 1.0);
        renderer.setSize( window.innerWidth, window.innerHeight );
        renderer.physicallyCorrectLights = true;
        renderer.shadowMap.enabled = true;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap; // default THREE.PCFShadowMap

        return renderer;
    }

    async createBackground(type, scene, sceneData){

        if(type === 'color'){

            if(this.debug){
                console.log("Background type: " + type);
            }

            let color = new THREE.Color(sceneData.environment.backgroundColor[0], sceneData.environment.backgroundColor[1], sceneData.environment.backgroundColor[2]);
            scene.background = color;
            scene.environment = color;

            let pmremGenerator = new THREE.PMREMGenerator( this.renderer );
            scene.environment = pmremGenerator.fromScene(scene).texture;

        } else if(type === 'texture'){

            let hdrLoader = new RGBELoader();
            let envMap = await hdrLoader.loadAsync("assets/" +sceneData.environment.backgroundTexture);
            envMap.mapping = THREE.EquirectangularReflectionMapping;

            scene.environment = envMap;
            scene.background = envMap;

            let pmremGenerator = new THREE.PMREMGenerator( this.renderer );
            scene.environment = pmremGenerator.fromScene(scene).texture;

        } else if(type === 'sky'){

            let sky = new Sky();
            sky.scale.setScalar( 450000 );
            scene.add( sky );
            let sun = new THREE.Vector3();
            
            let pmremGenerator = new THREE.PMREMGenerator( this.renderer );

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

    createCameras(sceneData){

        sceneData.scene_camera.forEach((cameraData) => {

            if(this.debug){
                console.log("Creating camera: " + cameraData.name);
            }

            let camera = new THREE.PerspectiveCamera(cameraData.fov * (180 / Math.PI), window.innerWidth / window.innerHeight, cameraData.near, cameraData.far);
            
            let dataMatrix = cameraData.matrix;
            const matrix = new THREE.Matrix4();
            matrix.fromArray(dataMatrix).transpose();
            let position = new THREE.Vector3();
            let quaternion = new THREE.Quaternion();
            let scale = new THREE.Vector3();
            matrix.decompose(position, quaternion, scale);

            // Apply these to the light
            camera.position.copy(position);
            camera.quaternion.copy(quaternion);
            camera.scale.copy(scale);

            this.listener = new THREE.AudioListener();
            camera.add(this.listener);
            
            this.scene.add(camera);

            if(cameraData.parent){
                camera.parent = Utility.findObjectByName(this.scene, cameraData.parent);
            }

            if(cameraData.active){

                if(this.debug){
                    console.log("Setting active camera: " + cameraData.name);
                }

                this.activeCamera = camera;


                this.controls = new OrbitControls( this.activeCamera, this.renderer.domElement );
                //this.controls.target.copy(this.geometricCenter);
                //this.controls = new PointerLockControls( this.activeCamera, this.renderer.domElement );

                // this.renderer.domElement.addEventListener( 'click', () => {

                //     console.log("Click");
                //     console.log(this.controls);
                //     this.controls.lock();
        
                // });

				const onKeyDown = function ( event ) {

					switch ( event.code ) {

						case 'ArrowUp':
						case 'KeyW':
							moveForward = true;
							break;

						case 'ArrowLeft':
						case 'KeyA':
							moveLeft = true;
							break;

						case 'ArrowDown':
						case 'KeyS':
							moveBackward = true;
							break;

						case 'ArrowRight':
						case 'KeyD':
							moveRight = true;
							break;

                        case 'KeyQ':
                            moveUp = true;
                            break;

                        case 'KeyE':
                            moveDown = true;
                            break;

						case 'Space':
							if ( canJump === true ) velocity.y += 350;
							canJump = false;
							break;

					}

				};

				const onKeyUp = function ( event ) {

					switch ( event.code ) {

						case 'ArrowUp':
						case 'KeyW':
							moveForward = false;
							break;

						case 'ArrowLeft':
						case 'KeyA':
							moveLeft = false;
							break;

						case 'ArrowDown':
						case 'KeyS':
							moveBackward = false;
							break;

                        case 'KeyQ':
                            moveUp = false;
                            break;

                        case 'KeyE':
                            moveDown = false;
                            break;

						case 'ArrowRight':
						case 'KeyD':
							moveRight = false;
							break;

					}

				};

				document.addEventListener( 'keydown', onKeyDown );
				document.addEventListener( 'keyup', onKeyUp );

                //let controls = new OrbitControls(this.activeCamera, this.renderer.domElement);
                //NB! OrbitControls needs a target (thus renders position needless)
                
                //this.controls = new FlyControls(this.activeCamera, this.renderer.domElement);
				//this.controls.rollSpeed = Math.PI / 24;
				//this.controls.autoForward = false;
				//this.controls.dragToLook = true;
                //this.controls.movementSpeed = 0.01;

                //this.controls = new FirstPersonControls(this.activeCamera, this.renderer.domElement);
                //this.controls.constrainVertical = true;


            }
            else if(sceneData.scene_camera.length == 1){

                if(this.debug){
                    console.log("Only one scene camera: " + cameraData.name);
                }

                this.activeCamera = camera;
            }
            
        });

    }

    createSpeakers(scene, sceneData, engine){
        
        sceneData.scene_speaker.forEach((speakerData) => {

            if(this.debug){
                console.log("Creating speaker: " + speakerData.name);
                console.log(speakerData);
            }

            let positionalAudio = new THREE.PositionalAudio(this.listener);

            var audioLoader = new THREE.AudioLoader();
            audioLoader.load("assets/" + speakerData.sound, function(buffer) {
                positionalAudio.setBuffer(buffer);
                positionalAudio.setRefDistance(speakerData.distance_ref);
                positionalAudio.setMaxDistance(speakerData.distance_max);
                positionalAudio.setDirectionalCone( speakerData.cone_inner, speakerData.cone_outer, speakerData.cone_outer_volume );
                positionalAudio.setLoop( true );
                positionalAudio.setVolume( speakerData.volume );
                positionalAudio.play();
            });

            // Create an 'empty' Object3D and attach the positional audio to it
            var audioPosition = new THREE.Object3D();

            let dataMatrix = speakerData.matrix;
            let matrix = new THREE.Matrix4();
            matrix.fromArray(dataMatrix).transpose();
            let position = new THREE.Vector3();
            let quaternion = new THREE.Quaternion();
            let scale = new THREE.Vector3();
            matrix.decompose(position, quaternion, scale);
            audioPosition.matrixAutoUpdate = false;

            // Apply these to the light
            audioPosition.position.copy(position);
            audioPosition.quaternion.copy(quaternion);
            audioPosition.scale.copy(scale);
            audioPosition.add(positionalAudio);

            // Then add the Object3D to your scene
            this.scene.add(audioPosition);

            if(this.debug){
                console.log(audioPosition);

                let helper = new PositionalAudioHelper( positionalAudio, 1.0 );
                positionalAudio.add( helper );

            }

        });

    }

    createLights(scene, sceneData, engine){
        //let lightAmbient = new THREE.AmbientLight( 0xFFFFFF ); // soft white light
        //scene.add(lightAmbient);

        sceneData.scene_light.forEach((lightData) => {

            let pointLightModifier = 10;
            let directionalLightModifier = 1;
            let spotLightModifier = 10;
            let areaLightModifier = 10;
            let helperSize = 0.5;

            if(lightData.type == "POINT"){

                let color = new THREE.Color(lightData.color[0], lightData.color[1], lightData.color[2]);
                let light = new THREE.PointLight(color, Utility.wattToLumens(lightData.intensity), 20);
                let dataMatrix = lightData.matrix;
                let matrix = new THREE.Matrix4();
                matrix.fromArray(dataMatrix).transpose();
                let position = new THREE.Vector3();
                let quaternion = new THREE.Quaternion();
                let scale = new THREE.Vector3();
                matrix.decompose(position, quaternion, scale);
    
                // Apply these to the light
                light.position.copy(position);
                light.quaternion.copy(quaternion);
                light.scale.copy(scale);
                light.updateMatrixWorld()

                if(lightData.shadow){
                    light.castShadow = true;
                    light.shadow.mapSize.width = 1024;
                    light.shadow.mapSize.height = 1024;
                    light.shadow.camera.near = 0.05; // default
                    light.shadow.camera.far = 500; // default
                    light.shadow.bias = -0.005;
                }

                if(lightData.parent != null){
                    let parent = Utility.findObjectByName(this.scene, lightData.parent);
                    console.log(parent);
                    parent.add(light);
                } else {
                    scene.add(light);
                }

                if(this.debug){
                    console.log("Added point light: " + lightData.name);
                    let lightHelper = new THREE.PointLightHelper(color, light, helperSize );

                    scene.add(lightHelper);
                }

            }
            if(lightData.type == "SUN"){
                let color = new THREE.Color(lightData.color[0], lightData.color[1], lightData.color[2]);
                let light = new THREE.DirectionalLight(color, Utility.wattToLumens(lightData.intensity));
                let dataMatrix = lightData.matrix;
                let matrix = new THREE.Matrix4();
                matrix.fromArray(dataMatrix).transpose();
                let position = new THREE.Vector3();
                let quaternion = new THREE.Quaternion();
                let scale = new THREE.Vector3();
                matrix.decompose(position, quaternion, scale);
    
                // Apply these to the light
                light.position.copy(position);
                light.quaternion.copy(quaternion);
                light.scale.copy(scale);

                //Directional lights uses targets rather than rotation
                let direction = new THREE.Vector3(0, 0, -1);
                direction.applyQuaternion(quaternion);
                let lightTargetPosition = position.clone().add(direction);
                light.target.position.copy(lightTargetPosition);
                light.target.updateMatrixWorld();

                if(lightData.shadowx){
                    console.log("Added shadow");
                    light.castShadow = true;
                    light.shadow.mapSize.width = 2048;
                    light.shadow.mapSize.height = 2048;
                    light.shadow.camera.near = 0.5; // default
                    light.shadow.camera.far = 500; // default
                    light.shadow.bias = 0.5;
                }

                scene.add(light);

                if(this.debug){
                    console.log("Added directional light: " + lightData.name);
                    let lightHelper = new THREE.DirectionalLightHelper(color,  light, helperSize );
                    scene.add(lightHelper);
                }

            }
            if(lightData.type == "SPOT"){
                let color = new THREE.Color(lightData.color[0], lightData.color[1], lightData.color[2]);
                let light = new THREE.SpotLight(color, Utility.wattToLumens(lightData.intensity));
                let dataMatrix = lightData.matrix;
                let matrix = new THREE.Matrix4();
                matrix.fromArray(dataMatrix).transpose();
                let position = new THREE.Vector3();
                let quaternion = new THREE.Quaternion();
                let scale = new THREE.Vector3();
                matrix.decompose(position, quaternion, scale);
    
                // Apply these to the light
                light.position.copy(position);
                light.quaternion.copy(quaternion);
                light.scale.copy(scale);

                //Directional lights uses targets rather than rotation
                let direction = new THREE.Vector3(0, 0, -1);
                direction.applyQuaternion(quaternion);
                let lightTargetPosition = position.clone().add(direction);
                light.target.position.copy(lightTargetPosition);
                light.target.updateMatrixWorld();

                light.angle = Math.cos(lightData.spotSize/2);
                light.penumbra = lightData.spotBlend;
                light.decay = 2;
                light.distance = 0;

                if(lightData.shadow){
                    light.castShadow = true;
                    light.shadow.mapSize.width = 1024;
                    light.shadow.mapSize.height = 1024;
                    light.shadow.camera.near = 0.05; // default
                    light.shadow.camera.far = 500; // default
                    light.shadow.bias = -0.005;
                }

                scene.add(light);

                if(this.debug){
                    console.log("Added spot light: " + lightData.name);
                    let lightHelper = new THREE.SpotLightHelper(color, light, helperSize );
                    scene.add(lightHelper);
                }


            }
            if(lightData.type == "AREA"){

                RectAreaLightUniformsLib.init();

                let color = new THREE.Color( lightData.color[0], lightData.color[1], lightData.color[2] );
                let light = new THREE.RectAreaLight( color, Utility.wattToLumens(lightData.intensity), lightData.areaSize[0], lightData.areaSize[1] );
                let dataMatrix = lightData.matrix;
                let matrix = new THREE.Matrix4();
                matrix.fromArray(dataMatrix).transpose();
                let position = new THREE.Vector3();
                let quaternion = new THREE.Quaternion();
                let scale = new THREE.Vector3();
                matrix.decompose(position, quaternion, scale);
    
                // Apply these to the light
                light.position.copy(position);
                light.quaternion.copy(quaternion);
                light.scale.copy(scale);

				scene.add( light );

                if(this.debug){
                    console.log("Added spot light: " + lightData.name);
                    let lightHelper = new RectAreaLightHelper( light );
                    scene.add(lightHelper);
                }

            }
            
        });
    }
    // Engine class implementation
}

export class Utility {

    static async loadProject(project, overridePath = null) {
        try {
            if (overridePath) {
                project = overridePath;
            } else {
                // Await the fetch call and subsequent transformation to JSON
                const response = await fetch(project);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const text = await response.text();
                return JSON.parse(text);
            }
        } catch (e) {
            console.error(e);
            // Optionally, you might want to return null or some default value in case of an error
            return null;
        }
    }

    static async loadComponent (object, componentName) {
        try {
            // Using Webpack magic comments to provide more context about dynamic imports
            const ModuleClass = await import(
              /* webpackInclude: /\.js$/ */
              /* webpackChunkName: "components" */
              `/assets/Sources/${componentName}.js`
            );

            //console.log("Loaded module");
    
            // Dynamically set the prototype of the loaded class to BaseComponent
            Object.setPrototypeOf(ModuleClass.default.prototype, BaseComponent.prototype);
    
            // Create an instance of the dynamically loaded component
            const componentInstance = new ModuleClass.default(object);

            //console.log(componentInstance.NotifyOnInit());
            //let componentInstance = new ModuleClass();

            return componentInstance;
            
        } catch (error) {
            console.error("Failed to load component:", error);
        }
    }
    

    static findObjectByName(scene, name) {
        let object = null;

        scene.traverse(function (child) {
            if (child.name === name) {
                object = child;
                return;
            }
        });

        return object;
        
    }

    static findObjectById(scene, id) {

        let object = null;

        scene.traverse(function (child) {
            if (child.userData.nx_id == id) {
                object = child;
                return;
            }
        })

        return object;
        
    }

    static wattToLumens(watts){
        return watts / 10;
    }

    // Utility class implementation
}

export class Meshcreator {
    // Meshcreator class implementation
}

export class UI2D {
    // UI2D class implementation
}

export class UI3D {
    // UI3D class implementation
}

export class XR {
    // XR class implementation
}

export class Controls {
    // Controls class implementation
}

export class Audio {
    // Audio class implementation
}

export class BaseComponent {

    constructor(object) {

        this.object = object;

    }

    NotifyOnInit() {
        // Initial setup logic here
    }

    NotifyOnUpdate() {
        // Update logic here
    }
}

//ADDED DYNAMICALLY
class MODRotationComponent extends BaseComponent {

    NotifyOnInit() {
        alert("GRIMBERGEN!");
    }
    NotifyOnUpdate() {
        this.object.rotation.x += 0.01;
        this.object.rotation.y += 0.01;
    }
}

export class ErrorManager {
    // ErrorManager class implementation

    static showProjectDataError(){
        alert("Project data error");
    }

}

/*
Bundled components:
- ArcballControls
- DragControls
- FirstPersonControls
- FlyControls
- MapControls
- OrbitControls
- PointerLockControls
- TrackballControls
- TransformControls
- FollowCamera
- NavCrowd
- NavMesh
- NavObstacle
- VehicleBody
- VirtualGamepad
- XR Controls?
- LoadingScreen
- CameraController
- SplitScreen
- TerrainPhysics
- MovieTexture
- Inspector
- NodeToy importer
- Section tool

- 2D Support? Template setup with 2D sprites, 2D lighting and 2D UI and 2D physics?

Other ideas:
- Blender operations output to the text log
- Asset library:
-- Auto-set download directory for Blender assets
-- Proxy-reference from threejs

-- Batching / Instancing for heavy scenes, see IFC.js: https://discourse.threejs.org/t/the-most-efficient-way-to-display-heavy-environments/39362

==> Before programming nodes, create easy snippets? Bundled/support for VSCode?
- Exposed props similar to Armory3d

- If live patching is active, unique ID's are used and adjusted with websockets
https://github.com/armory3d/armory/blob/main/blender/arm/live_patch.py




*/
