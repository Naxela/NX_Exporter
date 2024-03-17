import { Suspense, useEffect, useState } from 'react'
import { Canvas, useFrame} from '@react-three/fiber'
import { Bloom, DepthOfField, SMAA, ToneMapping, EffectComposer, Noise, Vignette, N8AO} from '@react-three/postprocessing'
import { OrbitControls, Html, useProgress, StatsGl } from '@react-three/drei'
import { useThree } from '@react-three/fiber'
import { BlendFunction } from 'postprocessing'
import * as THREE from 'three';

import RenderController from './RenderController'
import EnvironmentSetup from './Environment';
import Models from './Models';
import Lights from './Light';
import Cameras from './Camera';
import Speakers from './Speaker';
import { ScriptManagerProvider } from './Scripts'

function Loader() {
    const { progress } = useProgress()
    return <Html center>{progress} % loaded</Html>
}

export default function SceneManager({ projectData }) {

    let [currentScene, setCurrentScene] = useState(0);
    let [sceneData, setSceneData] = useState(null);

    window.ChangeScene = function(scene) {

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
            <Canvas shadows>

                <Suspense fallback={<Loader />}>
                    <EnvironmentSetup key={currentScene} environmentData={sceneData.environment} />
                    <RenderController data={projectData.options} />
                    <Cameras cameraData={sceneData.scene_cameras} />
                    <Lights lightData={sceneData.scene_lights} />
                    <Speakers />
                    <OrbitControls />
                    <Models data={{modelPath: sceneData.glb_groups[0], sceneManifest: sceneData }} />
                </Suspense>

                {/* Render other components as needed, passing them appropriate data */}
            </Canvas>
        </ScriptManagerProvider>
    );



}