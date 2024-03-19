import React, { useState, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { Bloom, DepthOfField, SMAA, ToneMapping, EffectComposer, Noise, Vignette, N8AO} from '@react-three/postprocessing'
import {ToneMappingMode} from 'postprocessing'

export default function Postprocessing({PostprocessData}) {

    console.log("PostprocessData: ", PostprocessData);

    const [abc, setAbc] = useState(0.5);

    // Use useEffect to set up a subscription or listener for changes to window.abc
    useEffect(() => {
        const handleAbcChange = () => setAbc(window.abc || 0.5);
        
        // Optional: Setup a listener for a custom event if changes to window.abc are broadcasted that way
        // window.addEventListener('abcChanged', handleAbcChange);

        // Cleanup function to remove listener
        return () => {
            // window.removeEventListener('abcChanged', handleAbcChange);
        };
    }, []);

    // Alternatively, directly update abc from window.abc on each frame
    useFrame(() => {
        setAbc(window.abc || 0.5);
    });

    if(PostprocessData.pipeline == "Standard") {

        let multisampling = PostprocessData.graphics.antialiasing ? 4 : 0;

        let tonemapMode = 0;
        switch(PostprocessData.graphics.tonemapping_type) {
            case "None":
                tonemapMode = ToneMappingMode.LINEAR;
                break;

            case "Linear":
                tonemapMode = ToneMappingMode.LINEAR;
                break;

            case "Reinhard":
                tonemapMode = ToneMappingMode.REINHARD;
                break;

            case "Cineon":
                tonemapMode = ToneMappingMode.OPTIMIZED_CINEON;
                break;

            case "Filmic":
                tonemapMode = ToneMappingMode.ACES_FILMIC;
                break;

            case "AgX":
                tonemapMode = ToneMappingMode.AGX;
                break;

            default:
                tonemapMode = ToneMappingMode.LINEAR;
                break;
        }

        return (
            <>
                <EffectComposer multisampling={multisampling} disableNormalPass={false} autoClear={true} depthBuffer={true} stencilBuffer={false}>
                    
                    { PostprocessData.graphics.bloom &&
                        <Bloom luminanceThreshold={0} luminanceSmoothing={0.9} height={300} />
                    }
                    { PostprocessData.graphics.ssao &&
                        <N8AO aoRadius={0.5} intensity={abc} />
                    }

                    <ToneMapping mode={tonemapMode} />

                </EffectComposer>
            </>
        );
    }

}