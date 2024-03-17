import { Suspense, useEffect, useState } from 'react'
import { Canvas, useFrame} from '@react-three/fiber'
import { Bloom, DepthOfField, SMAA, ToneMapping, EffectComposer, Noise, Vignette, N8AO} from '@react-three/postprocessing'
import { OrbitControls, Html, StatsGl } from '@react-three/drei'
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

async function loadProject(configUrl) {
    try {

        const response = await fetch(configUrl);
        const sceneConfig = await response.json();
        return sceneConfig;
        
    } catch (error) {
        console.error('Failed to load scene:', error);
    }
}

//TODO MOVE
function DrawCallMonitor() {
    const { gl } = useThree();
    const [drawCalls, setDrawCalls] = useState(0);

    useFrame(() => {
        setDrawCalls(gl.info.render.calls);
    });

    return (
        <Html occlude>
            <div style={{ position: 'absolute', top: 0, left: 0, color: 'white', backgroundColor: 'rgba(0, 0, 0, 0.7)', padding: '10px' }}>
                Draw Calls: {drawCalls}
                <br />
                Texture Calls: {gl.info.memory.textures}
            </div>
        </Html>
    );
}

//TODO MOVE
function Bridge(){

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
        window.NAX = {
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
            "mixer":{}
        };
        console.log('Bridge active');
    }, [scene]);

}

function Postprocessing({PostprocessData}) {

    const type = "Standard";

    if(type == "Standard") {
        return (
            <>
                <EffectComposer multisampling={4} disableNormalPass={false} autoClear={true} depthBuffer={true} stencilBuffer={false}>
                    <Bloom luminanceThreshold={0} luminanceSmoothing={0.9} height={300} />
                    <N8AO aoRadius={0.5} intensity={0.5} />
                </EffectComposer>
            </>
        );
    }
}

export default function SceneManager() {

    const [sceneConfig, setSceneConfig] = useState(null);
    const [renderSettings, setRenderSettings] = useState(null);
    const [modelPath, setModelPath] = useState('');
    const [cameras, setCameras] = useState([]);
    const [lights, setLights] = useState([]);

    useEffect(() => {
        async function fetchAndSetSceneConfig() {
            if(sceneConfig == null) {
                const config = await loadProject("project.nx");
                if (config) { // Ensure config is not null
                    setSceneConfig(config);
                }
            }
        }

        fetchAndSetSceneConfig();
    }, [sceneConfig]);

    // Optional: Use another useEffect here if subsequent state updates depend on sceneConfig being set
    useEffect(() => {
        if (sceneConfig && sceneConfig !== null) {
            console.log(sceneConfig);
            // Perform actions that depend on sceneConfig here
            // e.g., setRenderSettings(sceneConfig.manifest.render_settings);
            setRenderSettings(sceneConfig.options);
            setModelPath(sceneConfig.manifest.scenes[0].glb_groups[0]);
            setCameras(sceneConfig.manifest.scenes[0].scene_cameras);
            setLights(sceneConfig.manifest.scenes[0].scene_lights);
        }
    }, [sceneConfig]); // This ensures the code runs only after sceneConfig is updated

    return (
        <Suspense>
            {sceneConfig && renderSettings && (
                <ScriptManagerProvider>
                    <Canvas gl={{ antialias: false }} shadows="soft">
                        
                        <EnvironmentSetup environmentData={sceneConfig.manifest.scenes[0].environment} />
                        <RenderController data={renderSettings} />
                        <Cameras cameraData={cameras} />
                        <Lights lightData={lights} />
                        <Models data={{modelPath: modelPath, sceneManifest: sceneConfig.manifest.scenes[0] }} />
                        <Speakers />

                        <OrbitControls />
                        <Bridge />
                        <StatsGl className="stats" />
                        {/* <SoftShadows enabled={true} size={0.5} blur={0.8} resolution={1024} samples={8}/> */}
                        {/* <DrawCallMonitor /> */}

                        <Suspense>
                            <Postprocessing />
                        </Suspense>

                    </Canvas>
                </ScriptManagerProvider>
            )}
        </Suspense>
      )

}