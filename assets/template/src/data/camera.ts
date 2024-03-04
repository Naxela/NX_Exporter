import * as THREE from 'three';
import Logger from './logger';
import Utility from './utility';

export default class CameraManager {

    constructor(engine, renderer, scene, cameraData) {
        this.engine = engine;
        this.renderer = renderer;
        this.scene = scene;
        this.cameraData = cameraData;
        this.camera = null;
    }

    setupCameras() {

        Logger.log("Setting up cameras...");

        console.log(this.cameraData);
        
        if(this.cameraData.length < 1) {

            //TODO - Make camera based on viewport data
            alert("NO CAMERA DATA - Creating a default one...");

            const camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 0.1, 1000 );
            camera.position.z = 5;

            this.scene.add(camera);
            this.camera = camera;

        } else {
            
            this.cameraData.forEach(camData => {

                this.createCamera(camData);                
            
            });
        
        }

    }

    applyCamera(camera, camData) {

        Logger.log("Applying camera: " + camData.name);

        let dataMatrix = camData.matrix;
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

        camera.userData.nx_id = camData.identifier;

        //Arrange with ID and components
        if(camData.modules.length > 0) {

            Logger.log("Attaching modules to: " + camData.name + " // " + camData.identifier);

            camData.modules.forEach((module) => {

                this.engine.componentManager.attach(camData.identifier, module);

                Logger.log("Attached module: " + module + " to: " + camData.name + " // " + camData.identifier);

            })

        }

        if(camData.parent != null){
            
            //let parent = Utility.findObjectByName(scene, lightData.parent);
            let parent = Utility.findObjectById(this.scene, camData.parent);

            // Store the global/world position
            let globalPosition = new THREE.Vector3();
            camera.getWorldPosition(globalPosition);
    
            // Parent the light
            parent.add(camera);
    
            // Convert the stored global position to the new local position
            let localPosition = parent.worldToLocal(globalPosition.clone());
            camera.position.copy(localPosition);

        } else {
            this.scene.add(camera);
        }

        if(camData.active){
            this.camera = camera;
            //new OrbitControls( camera, this.renderer.domElement );
        }

    }

    createCamera(camData) {

        Logger.log("Creating camera: " + camData.name);

        let camera = null;

        if(camData.type == "Perspective") {

            let camera = new THREE.PerspectiveCamera(camData.fov, window.innerWidth / window.innerHeight, camData.clip_near, camData.clip_far);
            this.applyCamera(camera, camData);

        } else if (camData.type == "Orthographic") {

            let camera = new THREE.OrthographicCamera(camData.left, camData.right, camData.top, camData.bottom, camData.clip_near, camData.clip_far);
            this.applyCamera(camera, camData);

        } else {

            alert("UNKNOWN CAMERA TYPE: " + camData.type);
            return;

        }
        
    }

    updateCamera(camera) {
        
    }
    
}