import * as THREE from 'three';
import Logger from './logger';
import Utility from './utility';
import { RectAreaLightHelper }  from 'three/addons/helpers/RectAreaLightHelper.js';
import { PositionalAudioHelper } from 'three/addons/helpers/PositionalAudioHelper.js';
import { RectAreaLightUniformsLib } from 'three/addons/lights/RectAreaLightUniformsLib.js';

export default class LightManager {
    
    constructor(renderer, scene, lightData) {
        
        this.renderer = renderer;
        this.scene = scene;
        this.lightData = lightData;

    }

    setupLights() {
        
        Logger.log("Setting up lights...");

        if(this.lightData.length < 0) {

            //TODO - SETUP A SCENE LIGHT THAT FOLLOWS THE CAMERA
            alert("NO LIGHT DATA");

        } else {
            
            this.lightData.forEach(lightData => {
                
                this.createLight(this.scene, lightData);
                
            });
        
        }

    }

    updateLights() {
        
    }

    applyLight(scene, light, lightData, targetBased) {

        let dataMatrix = lightData.matrix;
        let matrix = new THREE.Matrix4();
        matrix.fromArray(dataMatrix).transpose();
        let position = new THREE.Vector3();
        let quaternion = new THREE.Quaternion();
        let scale = new THREE.Vector3();
        matrix.decompose(position, quaternion, scale);

        light.position.copy(position);
        light.quaternion.copy(quaternion);
        light.scale.copy(scale);
        light.updateMatrixWorld()

        light.userData.nx_id = lightData.identifier;

/*         if(lightData.modules.length > 0) {

            Logger.log("Attaching modules to: " + lightData.name + " // " + lightData.identifier);

            lightData.modules.forEach((module) => {

                this.engine.componentManager.attach(lightData.identifier, module);

                Logger.log("Attached module: " + module + " to: " + lightData.name + " // " + lightData.identifier);

            })

        } */

        if(targetBased){

            //Directional lights uses targets rather than rotation
            let direction = new THREE.Vector3(0, 0, -1);
            direction.applyQuaternion(quaternion);
            let lightTargetPosition = position.clone().add(direction);
            light.target.position.copy(lightTargetPosition);
            light.target.updateMatrixWorld();

        }

        

        if(lightData.parent != null){
            
            //let parent = Utility.findObjectByName(scene, lightData.parent);
            let parent = Utility.findObjectById(scene, lightData.parent);

            // Store the global/world position
            let globalPosition = new THREE.Vector3();
            light.getWorldPosition(globalPosition);
    
            // Parent the light
            parent.add(light);
    
            // Convert the stored global position to the new local position
            let localPosition = parent.worldToLocal(globalPosition.clone());
            light.position.copy(localPosition);

        } else {
            scene.add(light);
        }

        if(app.debugMode){

            if(lightData.type == "POINT"){
                let lightHelper = new THREE.PointLightHelper(light, 0.1);
                scene.add(lightHelper);
            }
            
            if(lightData.type == "SUN"){
                let lightHelper = new THREE.DirectionalLightHelper(light, 0.1);
                scene.add(lightHelper);
            }

            if(lightData.type == "SPOT"){
                let lightHelper = new THREE.SpotLightHelper(light);
                scene.add(lightHelper);
            }

            if(lightData.type == "AREA"){
                let lightHelper = new RectAreaLightHelper(light);
                scene.add(lightHelper);
            }

        }

    }

    createLight(scene, lightData) {

        Logger.log("Creating light...");

        if(lightData.type == "POINT"){

            let color = new THREE.Color(lightData.color[0], lightData.color[1], lightData.color[2]);
            let light = new THREE.PointLight(color, Utility.wattToLumens(lightData.intensity), 20);

            if(lightData.shadow){

                Logger.log("Creating shadow...");

                light.castShadow = true;
                light.shadow.mapSize.width = 1024;
                light.shadow.mapSize.height = 1024;
                light.shadow.camera.near = 0.05; // default
                light.shadow.camera.far = 500; // default
                light.shadow.bias = -0.005;
            }

            this.applyLight(scene, light, lightData, false);

        }
        if(lightData.type == "SUN"){
            let color = new THREE.Color(lightData.color[0], lightData.color[1], lightData.color[2]);
            let light = new THREE.DirectionalLight(color, Utility.wattToLumens(lightData.intensity));

            if(lightData.shadow){
                console.log("Added shadow");
                light.castShadow = true;
                light.shadow.mapSize.width = 2048;
                light.shadow.mapSize.height = 2048;
                light.shadow.camera.near = 0.5; // default
                light.shadow.camera.far = 500; // default
                light.shadow.bias = 0.5;
            }

            this.applyLight(scene, light, lightData, true);

        }
        if(lightData.type == "SPOT"){
            let color = new THREE.Color(lightData.color[0], lightData.color[1], lightData.color[2]);
            let light = new THREE.SpotLight(color, Utility.wattToLumens(lightData.intensity));

            if(lightData.shadow){
                light.castShadow = true;
                light.shadow.mapSize.width = 1024;
                light.shadow.mapSize.height = 1024;
                light.shadow.camera.near = 0.05; // default
                light.shadow.camera.far = 500; // default
                light.shadow.bias = -0.005;
            }

            light.angle = Math.cos(lightData.spotSize/2);
            light.penumbra = lightData.spotBlend;
            light.decay = 2;
            light.distance = 0;

            this.applyLight(scene, light, lightData, true);

        }
        if(lightData.type == "AREA"){

            RectAreaLightUniformsLib.init();

            let color = new THREE.Color( lightData.color[0], lightData.color[1], lightData.color[2] );
            let light = new THREE.RectAreaLight( color, Utility.wattToLumens(lightData.intensity), lightData.areaSize[0], lightData.areaSize[1] );
            
            this.applyLight(scene, light, lightData, false);

        }


    }
    
}