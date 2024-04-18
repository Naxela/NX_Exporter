import { Suspense, useEffect, useState } from 'react'
import { Canvas, useThree } from '@react-three/fiber'
import { Html, useProgress, StatsGl, PerspectiveCamera } from '@react-three/drei'
import { ARButton, XR, useHitTest, useXR, Interactive } from '@react-three/xr';
import * as THREE from 'three'


import RenderController from './RenderController'
import EnvironmentSetup from './Environment';
import Bridge from './Bridge'
import Models from './Models';
import Lights from './Light';
import Cameras from './Camera';
import Empty from './Empty';
import Speakers from './Speaker';
import { ScriptManagerProvider } from './Scripts'
import ComponentInjection from '../ComponentInjection';

function Loader() {
    const { progress } = useProgress()
    return <Html center>{progress} % loaded</Html>
}

function MyCamera() {
    return (
        <PerspectiveCamera makeDefault near={0.001} />
    )
}

function AdjustARCamera({ near }) {
    const { camera } = useThree();

    useEffect(() => {
        if (camera && camera.isPerspectiveCamera) {
        camera.near = near;
        camera.updateProjectionMatrix();
        }
    }, [camera, near]);

return null;
}

function ToneMapping() {
    const { gl, scene } = useThree(({ gl, scene }) => ({ gl, scene }));
    useEffect(() => {
      gl.toneMapping = THREE.ACESFilmicToneMapping;
      gl.toneMappingExposure = 1.0;
      scene.traverse((object) => {
        if (object.material) {
          object.material.needsUpdate = true;
        }
      });
    }, [gl, scene]);
    return <></>;
  }

export default function SceneManager({ projectData }) {

    let [currentScene, setCurrentScene] = useState(0);
    let [sceneData, setSceneData] = useState(null);

    window.NAX.ChangeScene = function(scene) {

        //TODO! - Unload existing scene?

        if(typeof scene == "number") {
            setCurrentScene(scene);
        } else if(typeof scene == "string") {
            
            for(let i = 0; i < projectData.manifest.scenes.length; i++) {
                if(projectData.manifest.scenes[i].name == scene) {
                    setCurrentScene(i);
                    break;
                }
            }
            
        }

    }

    useEffect(() => {

        if(projectData.manifest.scenes[currentScene] != null){
            const newSceneData = projectData.manifest.scenes[currentScene];
            setSceneData(newSceneData); // Correctly use setSceneData to update sceneData
            console.log("SceneData: ", newSceneData);
            console.log("ProjectData: ", projectData);
        } else {
            console.log("SCENE NOT FOUND!");
        }

    }, [currentScene, projectData]); // Include projectData in the dependency array if it could change over time

    if (!sceneData || !projectData) {
        console.log("Loading scene...");
        return <div>Loading scene...</div>;
    }

    // Render scene using sceneData
    return (
        <ScriptManagerProvider>
            {/* <ARButton sessionInit={{ optionalFeatures: [
                'local-floor', 
                'bounded-floor', 
                'hand-tracking', 
                'layers', 
                'dom-overlay'
            ] }} /> */}
            <ARButton
                sessionInit={{ 
                    requiredFeatures: ['hit-test'],
                    optionalFeatures: ['local-floor','dom-overlay', 'dom-overlay-for-handheld-ar'],
                    domOverlay: { root: document.querySelector('#NAX-XR-Overlay') }
                }}
            />
            <Canvas flat gl={{ antialias: false }}>
                <Bridge />
                <Suspense fallback={<Loader />}>
                    
                    <XR>
                    <ToneMapping />
                    <EnvironmentSetup key={currentScene} environmentData={sceneData.environment} />
                    <RenderController data={projectData.options} />
                    {/* <Cameras cameraData={sceneData.scene_cameras} /> */}
                    <MyCamera />
                    <AdjustARCamera near={0.01} />
                    <Lights lightData={sceneData.scene_lights } />
                    <Speakers />

                    
                    <Models data={{modelPath: sceneData.glb_groups[0], sceneManifest: sceneData }} />
                    <Empty data={{modelPath: sceneData.glb_groups[0], sceneManifest: sceneData }} />

                    {/* <StatsGl className="stats" /> */}

                    {/* NAX-POST-EFFECT START */}
                    <ComponentInjection />
                    {/* NAX-POST-EFFECT END */}
                    </XR>

                </Suspense>

            </Canvas>
        </ScriptManagerProvider>
        
    );

}