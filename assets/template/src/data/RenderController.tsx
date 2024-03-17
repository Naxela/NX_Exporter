import React, { useRef, useEffect } from 'react';
import { useThree } from '@react-three/fiber';
import { Environment } from '@react-three/drei';

function RenderController({ data }) {

    const controllerRef = useRef();
    const set = useThree((state) => state.set);

    useEffect(() => {

        if (data) {
            
            if(data.pipeline == "Standard"){
                const graphics = data.graphics;

                //console.log(gl);
                //
                //set({gl.antialias,false});
            }


        }

    }, [data]);

    return(
        <>
        {/* <color attach="background" args={["#dfdfdf"]} /> */}
        </>
    );

}

export default RenderController