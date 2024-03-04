import * as THREE from 'three';
import Utility from './utility'
import SceneManager from './scene'
import ErrorManager from './error_manager';
import EventManager from './events';
import ComponentManager from './components';
import Logger from './logger';
import Stats from 'stats.js';

/* THIS PART IS DYNAMICALLY GENERATED */

//import { OrbitControls } from 'three/examples/jsm/Addons.js';

/* DYNAMICALLY GENERATED END */


export class NXEngine {
    projectFile: string;
    engineTime: THREE.Clock;
    projectData: null|JSON;
    debugMode: boolean;
    modules: object;
    three: object;
    utility: Utility;


    constructor(projectFile: string) {
        //Project properties
        this.projectFile = projectFile;
        this.projectData = null;
        this.debugMode = false;


        //TODO - FIND SOME WAY TO DYNAMICALLY GENERATE THIS
        //this.modules = {
        //    "OrbitControls": OrbitControls
        //};

        //TODO - TEST THIS FOR SOURCE FILES
        //const modules = import.meta.glob('./dir/*.js')

        //Engine properties
        this.three = THREE;
        this.utility = Utility;
        this.renderManager = null;
        this.engineTime = null;
        this.sceneManager = null;
        this.componentManager = null;
        this.xr = false;
        this.stats = {
            "fps": null,
            "ms": null,
            "mem": null
        };
        this.loaders = {
            "RGBE": null,
            "GLTF": null
        };
        this.ready = false;


        this.controllers = null;
    }

    init = async (app: object) => {

        // Make app globally available
        Utility.setGlobal('app', app);

        // Set engine time
        this.engineTime = new THREE.Clock();

        Logger.log("NX Engine initializing - loading project...");

        // Load project
        this.projectData = await Utility.loadProject(this.projectFile);

        this.debugMode = this.projectData.debug;
        this.xr = this.projectData.options.xr;

        if(this.debugMode){
            this.stats["fps"] = new Stats();
            this.stats["ms"] = new Stats();
            this.stats["mem"] = new Stats();

            this.stats["fps"].showPanel( 0 );
            this.stats["ms"].showPanel( 1 );
            this.stats["mem"].showPanel( 2 );

            document.body.appendChild( this.stats["fps"].dom );
            document.body.appendChild( this.stats["ms"].dom );
            document.body.appendChild( this.stats["mem"].dom );

            this.stats["ms"].domElement.style.cssText = 'position:absolute;top:0px;left:80px;';
            this.stats["mem"].domElement.style.cssText = 'position:absolute;top:0px;left:160px;';
        }

        Logger.log(this.projectData);

        // Check if project data is valid
        if(!this.projectData) {
            ErrorManager.showProjectDataError();
            return;
        }

        Logger.log("Project loaded - loading root scene");
        document.title = this.projectData.name;

        this.componentManager = new ComponentManager(app);

        // Load root scene
        let rootScene = this.projectData.manifest.scenes[0];
        this.sceneManager = new SceneManager(app, this.projectData.options);

        this.renderManager = await this.sceneManager.loadScene(rootScene);

        let eventManager = new EventManager(this.sceneManager);

        eventManager.setupEvents([
            "resize",
            "click",
            "touchstart"
        ]);

        this.ready = true;

        Logger.log("Root scene loaded");

        await this.componentManager.setupComponents();

        Logger.log(this.componentManager.components);

        this.componentManager.components.forEach((component: { NotifyOnInit: () => void; }) => {
            if (component.NotifyOnInit) {
                component.NotifyOnInit();
            }
        });

        ////
        //console.log(app.sceneManager.scene3D);
        ////

        /*
        this.sceneManager.scene3D.traverse(child => {
            if (child.isMesh) {
                child.updateMatrixWorld(); //(force?)
                child.matrixAutoUpdate = false;
            }
        });
        */

        this.controller = this.renderManager.renderer.xr.getController( 0 );
        this.controller.addEventListener( 'select', this.onSelect );
        this.sceneManager.scene3D.add( this.controller );

        Logger.log(this.sceneManager.cameraManager.camera);
        const xrManager = this.sceneManager.renderManager.renderer.xr;
        xrManager.addEventListener('sessionstart', () => { 
            this.sceneManager.renderManager.renderer.xr.getCamera(0).near = 0.001;
            console.log(this.sceneManager.renderManager.renderer.xr.getCamera(0)); 
        });

        if(this.projectData.livelink) {
            const port = 3001;
            const ws = new WebSocket('ws://localhost:'+port);
    
            ws.onopen = () => {
                console.log('WebSocket connection established');
                ws.send('Hello from client');
            };
    
            ws.onmessage = (event) => {
    
                if(event.data.startsWith('app')) {
                    console.log('Command:', event.data);
                    eval(event.data);
    
                } else {
                    console.log('Message from server:', event.data);
                }
    
            };
        }

    }



    //Temporary
    onSelect = () => {
        const geometry = new THREE.CylinderGeometry( 0, 0.05, 0.2, 32 ).rotateX( Math.PI / 2 );
        const material = new THREE.MeshPhongMaterial( { color: 0xffffff * Math.random() } );
        const mesh = new THREE.Mesh( geometry, material );
        mesh.position.set( 0, 0, - 0.3 ).applyMatrix4( this.controller.matrixWorld );
        mesh.quaternion.setFromRotationMatrix( this.controller.matrixWorld );
        this.sceneManager.scene3D.add( mesh );
        
    }

    //Delete this
    animate = () => {

        if (this.ready && this.renderManager.renderer != null) {
    
            requestAnimationFrame(this.animate);
    
            this.componentManager.components.forEach((component: { NotifyOnUpdate: () => void; }) => {
                if (component.NotifyOnUpdate) {
                    component.NotifyOnUpdate();
                }
            });
    
            this.sceneManager.mixer.update(this.engineTime.getDelta());
    
            // Use the composer to render the scene instead of the direct render call
            if (this.renderManager.composer) {
                this.renderManager.composer.render();
            } else {
                // Fallback to normal rendering if composer is not set up
                this.renderManager.renderer.render(this.sceneManager.scene3D, this.sceneManager.cameraManager.camera);
            }
        }
    };


    startAnimationLoop = () => {
        if (this.renderManager.renderer != null) {
            this.renderManager.renderer.setAnimationLoop(() => {
                if (this.ready) {

                    if(this.debugMode){
                        this.stats["fps"].begin();
                        this.stats["ms"].begin();
                        this.stats["mem"].begin();
                    }

                    this.componentManager.components.forEach((component: { NotifyOnUpdate: () => void; }) => {
                        if (component.NotifyOnUpdate) {
                            component.NotifyOnUpdate();
                        }
                    });

                    this.sceneManager.mixer.update(this.engineTime.getDelta());

                    if (this.renderManager.composer) {
                        this.renderManager.composer.render();
                    } else {
                        this.renderManager.renderer.render(this.sceneManager.scene3D, this.sceneManager.cameraManager.camera);
                    }

                    if(this.debugMode){
                        this.stats["fps"].end();
                        this.stats["ms"].end();
                        this.stats["mem"].end();
                    }

                } else {
                    // Optionally stop the animation loop if not ready
                    this.renderManager.renderer.setAnimationLoop(null);
                }
            });
        }
    };

    moveObject = (objID: any, location: any[]) => {
        Utility.findObjectById(app.sceneManager.scene3D, objID).position.set(location[0], location[1], location[2]);
    };

    rotateObject = (objID: any, rotation: any[]) => {
        Utility.findObjectById(app.sceneManager.scene3D, objID).rotation.set(rotation[0], rotation[1], rotation[2]);
    }

    scaleObject = (objID: any, scale: any[]) => {
        Utility.findObjectById(app.sceneManager.scene3D, objID).scale.set(scale[0], scale[1], scale[2]);
    }

    applyMatrix = (objID: any, matrixValues: number[]) => {
        // Create a new THREE.Matrix4 object
        const matrix = new THREE.Matrix4();
        // Set the matrix using the provided array values
        matrix.set(
            matrixValues[0], matrixValues[1], matrixValues[2], matrixValues[3],
            matrixValues[4], matrixValues[5], matrixValues[6], matrixValues[7],
            matrixValues[8], matrixValues[9], matrixValues[10], matrixValues[11],
            matrixValues[12], matrixValues[13], matrixValues[14], matrixValues[15]
        );
    
        // Decompose the matrix into position, quaternion, and scale
        const position = new THREE.Vector3();
        const quaternion = new THREE.Quaternion();
        const scale = new THREE.Vector3();
        matrix.decompose(position, quaternion, scale);
    
        // Apply the decomposed values to the object
        const object = Utility.findObjectById(app.sceneManager.scene3D, objID);
        object.position.copy(position);
        object.quaternion.copy(quaternion);
        object.scale.copy(scale);
        
        const adjustmentQuat = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), Math.PI / 2);
        object.quaternion.multiply(adjustmentQuat);
    };

    setLightColor = (lightID: any, color: any[]) => {
        Utility.findObjectById(app.sceneManager.scene3D, lightID).color.set(color[0], color[1], color[2]);
    }

    setLightStrength = (lightID: any, strength: any) => {
        Utility.findObjectById(app.sceneManager.scene3D, lightID).intensity = strength;
    }

}