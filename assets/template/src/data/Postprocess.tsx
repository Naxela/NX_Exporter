import React, { useState, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { Bloom, DepthOfField, SMAA, ToneMapping, EffectComposer, Noise, Vignette, N8AO} from '@react-three/postprocessing'
import {ToneMappingMode} from 'postprocessing'

export default function Postprocessing({PostprocessData}) {

    console.log("PostprocessData: ", PostprocessData);

    const [abc, setAbc] = useState(0.5);
    const [tonemapMode, setTonemapMode] = useState(ToneMappingMode.LINEAR);

    // Use useEffect to set up a subscription or listener for changes to window.abc
    useEffect(() => {

        window.setAbc = setAbc;
        window.setTonemapMode = setTonemapMode;
        window.ToneMappingMode = ToneMappingMode;

        const handleAbcChange = () => setAbc(window.abc || 0.5);
        const handleTonemapModeChange = () => setTonemapMode(window.tonemapMode || ToneMappingMode.LINEAR);

        window.addEventListener('abcChanged', handleAbcChange);
        window.addEventListener('tonemapModeChanged', handleTonemapModeChange);

        return () => {
            window.removeEventListener('abcChanged', handleAbcChange);
            window.removeEventListener('tonemapModeChanged', handleTonemapModeChange);
            delete window.setAbc;
            delete window.setTonemapMode;
            delete window.ToneMappingMode;
        };
    }, []);

    // Alternatively, directly update abc from window.abc on each frame
    useFrame(() => {
        setAbc(window.abc || 0.5);
        setTonemapMode(window.tonemapMode || ToneMappingMode.LINEAR);
    });

    if (PostprocessData.pipeline === "Standard") {
        let multisampling = PostprocessData.graphics.antialiasing ? 4 : 0;

        return (
            <EffectComposer multisampling={multisampling} disableNormalPass={false} autoClear={true} depthBuffer={true} stencilBuffer={false}>
                {PostprocessData.graphics.bloom && <Bloom luminanceThreshold={0} luminanceSmoothing={0.9} height={300} />}
                {PostprocessData.graphics.ssao && <N8AO aoRadius={0.5} intensity={abc} />}
                <ToneMapping mode={tonemapMode} />
            </EffectComposer>
        );
    }

}