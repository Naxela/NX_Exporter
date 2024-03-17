import { useRef, useEffect } from 'react';
import { useThree } from '@react-three/fiber';
import * as THREE from 'three';
import { PointLightHelper, DirectionalLightHelper, SpotLightHelper } from 'three';
import { RectAreaLightHelper }  from 'three/addons/helpers/RectAreaLightHelper.js';
import { RectAreaLightUniformsLib } from 'three/examples/jsm/lights/RectAreaLightUniformsLib';
//import Utility from './Utility';

// Initialize RectAreaLight uniforms
RectAreaLightUniformsLib.init();

interface LightData {
  shadow: boolean | undefined;
  matrix: Array<number>;
  areaSize: Array<number>;
  spotSize: number;
  castShadow: boolean;
  intensity: number;
  color: Array<number>;
  type: string;
}

function Light({ lightData }: { lightData: LightData }) {

  const lightRef = useRef();
  const { scene } = useThree(); 
  
  useEffect(() => {

    if (!lightRef.current) return;
    if (!lightData) return;

    const light = lightRef.current as THREE.Light;
    
    const dataMatrix = lightData.matrix;
    const matrix = new THREE.Matrix4();
    matrix.fromArray(dataMatrix).transpose();
    
    const position = new THREE.Vector3();
    const quaternion = new THREE.Quaternion();
    const scale = new THREE.Vector3();
    
    matrix.decompose(position, quaternion, scale);
    
    light.position.copy(position);
    light.quaternion.copy(quaternion);
    light.scale.copy(scale);
    light.updateMatrixWorld();

    if(lightData.type == "POINT"){
        //Pass
    }

    if(lightData.type == "SUN"){

        const direction = new THREE.Vector3(0, 0, -1);
        direction.applyQuaternion(quaternion);
        const lightTargetPosition = position.clone().add(direction);
        light.target.position.copy(lightTargetPosition);
        light.target.updateMatrixWorld();

        // const dirLight = light as THREE.DirectionalLight;

        // dirLight.shadow.camera.near = 0.1;
				// dirLight.shadow.camera.far = 500;
				// dirLight.shadow.camera.right = 17;
				// dirLight.shadow.camera.left = - 17;
				// dirLight.shadow.camera.top	= 17;
				// dirLight.shadow.camera.bottom = - 17;
				// dirLight.shadow.mapSize.width = 512;
				// dirLight.shadow.mapSize.height = 512;
				// dirLight.shadow.radius = 4;
				// dirLight.shadow.bias = - 0.0005;
    }

    if(lightData.type == "SPOT"){

      const direction = new THREE.Vector3(0, 0, -1);
      direction.applyQuaternion(quaternion);
      const lightTargetPosition = position.clone().add(direction);
      light.target.position.copy(lightTargetPosition);
      light.target.updateMatrixWorld();

    }

    if(lightData.type == "AREA"){
        //pass
    }
    
    let helper:any;
    switch (lightData.type) {
      case "POINT":
        helper = new PointLightHelper(lightRef.current, 0.5);
        break;
      case "SUN":
        helper = new DirectionalLightHelper(lightRef.current, 0.5);
        break;
      case "SPOT":
        helper = new SpotLightHelper(lightRef.current, 0.5);
        break;
      case "AREA":
        // Note: RectAreaLightHelper requires a second argument: the scene
        helper = new RectAreaLightHelper(lightRef.current);
        if (lightRef.current) lightRef.current.add(helper);
        break;
    }
    
    if (helper && lightData.type !== "AREA") {
      scene.add(helper);
    }
    
    return () => {
      if (helper) {
        scene.remove(helper);
        helper.dispose();
      }
    };
  }, [lightData]);

  //SoftShadows();

  const fov = 20;
  
  // Determine which light component to render based on the light type
  switch (lightData.type) {
    case "POINT":
      return (
        <pointLight
          ref={lightRef}
          color={new THREE.Color(lightData.color)}
          intensity={wattToLumens(lightData.intensity)}
          castShadow={lightData.shadow}
          // Additional shadow and light properties would be set here
        />
      );
    case "SUN":
      return (
        <directionalLight
          ref={lightRef}
          color={new THREE.Color(lightData.color)}
          intensity={wattToLumens(lightData.intensity) * 5}
          castShadow={lightData.shadow}
          shadow-mapSize-height={1024}
          shadow-mapSize-width={1024}
          shadow-camera-far={50}
          shadow-camera-left={-fov}
          shadow-camera-right={fov}
          shadow-camera-top={fov}
          shadow-camera-bottom={-fov}
          shadow-bias={-0.005}
          shadow-normalBias={0.1}
          shadow-radius={10}
        />
      );
    case "SPOT":
      return (
        <spotLight
          ref={lightRef}
          color={new THREE.Color(lightData.color)}
          intensity={wattToLumens(lightData.intensity)}
          angle={Math.cos(lightData.spotSize / 2)}
          penumbra={2}
          decay={2}
          castShadow={lightData.shadow}
          shadow-mapSize-height={2048}
          shadow-mapSize-width={2048}
          shadow-camera-far={50}
          shadow-camera-left={-10}
          shadow-bias={-0.00005}
          shadow-normalBias={0.1}
          shadow-radius={1000}
          // Additional shadow and light properties
        />
      );
    case "AREA":
      return (
        <rectAreaLight
          ref={lightRef}
          color={new THREE.Color(lightData.color)}
          intensity={wattToLumens(lightData.intensity)}
          width={lightData.areaSize[0]}
          height={lightData.areaSize[1]}
        />
      );
    default:
      return null;
  }
}

function wattToLumens(watts: number){
  return watts / 10;
  //return (683 * watts)  / ( 4 * Math.pi)
  //const LUMENS_PER_WATT = 683;
  //watts * LUMENS_PER_WATT / (4 * Math.PI);
}

function Lights({ lightData}: { lightData:object }) {

  return (
    <>
      {lightData.map((data:object, index: number) => (
        <Light key={index} lightData={data} />
      ))}
    </>
  );
}

export default Lights;