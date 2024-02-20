import * as THREE from 'three';
import Logger from './logger';
import { PositionalAudioHelper } from 'three/addons/helpers/PositionalAudioHelper.js';

export default class SpeakerManager {

    constructor(engine, scene, speakerData) {
        
        this.scene = scene;
        this.speakerData = speakerData;
        this.engine = engine;

        this.speakers = [];
    
    }

    setupSpeakers() {

        this.speakerData.forEach((speakerData) => {
            
            this.createSpeaker(speakerData);

        })

    }

    createSpeaker(speakerData){

        this.engine.sceneManager.listener = new THREE.AudioListener();
        this.engine.sceneManager.cameraManager.camera.add(this.engine.sceneManager.listener);
        let positionalAudio = new THREE.PositionalAudio(this.engine.sceneManager.listener);

        var audioLoader = new THREE.AudioLoader();
        audioLoader.load("assets/" + speakerData.sound, function(buffer) {
            positionalAudio.setBuffer(buffer);
            positionalAudio.setRefDistance(speakerData.distance_ref);
            positionalAudio.setMaxDistance(speakerData.distance_max);
            positionalAudio.setDirectionalCone( speakerData.cone_inner, speakerData.cone_outer, speakerData.cone_outer_volume );
            positionalAudio.setLoop(speakerData.loop);
            positionalAudio.setVolume( speakerData.volume );
            if(speakerData.autoplay){
                positionalAudio.play();
            }
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

        if(speakerData.parent != null){
            
            //let parent = Utility.findObjectByName(scene, lightData.parent);
            let parent = Utility.findObjectById(this.scene, speakerData.parent);

            // Store the global/world position
            let globalPosition = new THREE.Vector3();
            audioPosition.getWorldPosition(globalPosition);
    
            // Parent the light
            parent.add(audioPosition);
    
            // Convert the stored global position to the new local position
            let localPosition = parent.worldToLocal(globalPosition.clone());
            audioPosition.position.copy(localPosition);

        } else {
            this.scene.add(audioPosition);
        }

        // Then add the Object3D to your scene
        //this.scene.add(audioPosition);

        if(app.debugMode){

            let helper = new PositionalAudioHelper( positionalAudio, 1.0 );
            positionalAudio.add( helper );

        }

    }

}