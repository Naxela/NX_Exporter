import * as THREE from 'three';
import Utility from './utility'
import SceneManager from './scene'
import ErrorManager from './error_manager';
import EventManager from './events';
import ComponentManager from './components';
import Logger from './logger';
import Stats from 'stats.js';

/*
################
NX Exporter => Blender
NX Runtime => Runtime/JS
################
*/

export class NXEngine {

    constructor(projectFile) {
        //Project properties
        this.projectFile = projectFile;
        this.projectData = null;
        this.debugMode = null;

        //Engine properties
        this.three = THREE;
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

    init = async (app) => {

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

        this.componentManager.components.forEach(component => {
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
    
            this.componentManager.components.forEach(component => {
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

                    this.componentManager.components.forEach(component => {
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

}