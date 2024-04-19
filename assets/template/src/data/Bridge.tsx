import { useEffect} from 'react'
import { useThree } from '@react-three/fiber'
import Utility from './Utility';
import * as THREE from 'three';

export default function Bridge(){

    const { 
        scene, 
        gl,
        camera,
        raycaster,
        pointer,
        clock,
        frameloop,
        performance,
        size,
        viewport,
        xr,
        advance,
        setSize,
        setDpr,
        setFrameloop,
        setEvents,
        onPointerMissed,
        events
    } = useThree();

    useEffect(() => {
        // Expose the scene globally
        Object.assign(window.NAX, {
            "scene": scene,
            "renderer": gl,
            "camera": camera,
            "raycaster": raycaster,
            "pointer": pointer,
            "clock": clock,
            "frameloop": frameloop,
            "performance": performance,
            "size": size,
            "viewport": viewport,
            "xr": xr,
            "advance": advance,
            "setSize": setSize,
            "setDpr": setDpr,
            "setFrameloop": setFrameloop,
            "setEvents": setEvents,
            "onPointerMissed": onPointerMissed,
            "events": events,
            "mixer": {}
        });

        window.NAX.moveObject = (objID: any, location: any[]) => {
            Utility.findObjectById(NAX.scene, objID).position.set(location[0], location[1], location[2]);
        };

        window.NAX.rotateObject = (objID: any, rotation: any[]) => {
            Utility.findObjectById(NAX.scene, objID).rotation.set(rotation[0], rotation[1], rotation[2]);
        }

        window.NAX.scaleObject = (objID: any, scale: any[]) => {
            Utility.findObjectById(NAX.scene, objID).scale.set(scale[0], scale[1], scale[2]);
        }

        window.NAX.applyMatrix = (objID: any, matrixValues: number[]) => {

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
            const object = Utility.findObjectById(NAX.scene, objID);
            object.position.copy(position);
            object.quaternion.copy(quaternion);
            object.scale.copy(scale);
            
            const adjustmentQuat = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), Math.PI / 2);
            object.quaternion.multiply(adjustmentQuat);
        };

        window.NAX.setLightColor = (lightID: any, color: any[]) => {

            Utility.findObjectById(NAX.scene, lightID).color.set(color[0], color[1], color[2]);
            
        }

        window.NAX.setLightStrength = (lightID: any, strength: any) => {

            Utility.findObjectById(NAX.scene, lightID).intensity = strength;

        }


        console.log('Bridge active');
    }, [scene]);

}