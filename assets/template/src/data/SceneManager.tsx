import { Suspense, useEffect, useState } from 'react'
import { Canvas } from '@react-three/fiber'
import { Html, useProgress, StatsGl, OrbitControls, Environment } from '@react-three/drei'

import RenderController from './RenderController'
import EnvironmentSetup from './Environment';
import Bridge from './Bridge'
import Models from './Models';
import Lights from './Light';
import Cameras from './Camera';
import Speakers from './Speaker';
import Empty from './Empty';
import { ScriptManagerProvider } from './Scripts'
import Postprocessing from './Postprocess'
import ComponentInjection from '../ComponentInjection';

function Loader() {
    const { progress } = useProgress()
    return <Html center>{progress} % loaded</Html>
}

export default function SceneManager({ projectData }) {

    let [currentScene, setCurrentScene] = useState(0);
    let [sceneData, setSceneData] = useState(null);

    window.NAX = window.NAX || {};

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
            <Canvas /* flat gl={{ antialias: false }} */ shadows>
                <Bridge />
                <Suspense fallback={<Loader />}>
                    <EnvironmentSetup key={currentScene} environmentData={sceneData.environment} />
                    <RenderController data={projectData.options} />
                    <Cameras cameraData={sceneData.scene_cameras} />
                    <Lights lightData={sceneData.scene_lights } />
                    <Speakers />
                    <Models data={{modelPath: sceneData.glb_groups[0], sceneManifest: sceneData }} />
                    <Empty data={{modelPath: sceneData.glb_groups[0], sceneManifest: sceneData }} />
                    <Postprocessing PostprocessData={projectData.options} />

                    {/* <StatsGl className="stats" /> */}

                    {/* NAX-POST-EFFECT START */}
                    <ComponentInjection />
                    {/* NAX-POST-EFFECT END */}


                </Suspense>

            </Canvas>
        </ScriptManagerProvider>
        
    );

}