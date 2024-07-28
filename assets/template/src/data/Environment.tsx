import * as THREE from 'three';
import { useThree } from '@react-three/fiber'
import { Sky } from 'three/addons/objects/Sky.js';
import { Environment } from '@react-three/drei';

interface EnvironmentData {
    azimuth: number;
    elevation: number;
    mieDirectionalG: number;
    mieCoefficient: number;
    rayleigh: number;
    turbidity: number;
    backgroundColor: Array<number>;
    backgroundType: string;
}

function EnvironmentSetup({ environmentData }: { environmentData: EnvironmentData }) {

    //const environmentRef = useRef();
    const { scene, gl } = useThree();

    //TODO MAKE CONDITIONAL FROM PROJECT
    const generateIrradiance = true;

    //console.log("ENV",environmentData);
    if(environmentData.backgroundType == "color"){
        
        const color = new THREE.Color(environmentData.backgroundColor[0], environmentData.backgroundColor[1], environmentData.backgroundColor[2]);
        
        scene.background = color;
        scene.environment = color;

        if(generateIrradiance){
            const pmremGenerator = new THREE.PMREMGenerator( gl );
            scene.environment = pmremGenerator.fromScene(scene).texture;
        }
        
        return (
            <>
            <color attach="background" args={[color]} />
            <ambientLight intensity={1.0} color={color}/>
            </>
        )
        
    }
    if(environmentData.backgroundType == "texture"){

        if(generateIrradiance){
            const pmremGenerator = new THREE.PMREMGenerator( gl );
            scene.environment = pmremGenerator.fromScene(scene).texture;
        }

        return (
            <>
            <Environment background files={environmentData.backgroundTexture} />
            </>
        )
    }
    if(environmentData.backgroundType == "sky"){

        const sky = new Sky();
        sky.scale.setScalar( 450000 );

        scene.add(sky);
        
        const sun = new THREE.Vector3();

        const uniforms = sky.material.uniforms;
        uniforms[ 'turbidity' ].value = environmentData.turbidity;
        uniforms[ 'rayleigh' ].value = environmentData.rayleigh;
        uniforms[ 'mieCoefficient' ].value = environmentData.mieCoefficient;
        uniforms[ 'mieDirectionalG' ].value = environmentData.mieDirectionalG;
        
        const phi = THREE.MathUtils.degToRad( 90 - environmentData.elevation );
        const theta = THREE.MathUtils.degToRad( environmentData.azimuth );

        sun.setFromSphericalCoords(1, phi, theta);

        uniforms['sunPosition'].value.copy( sun );

        if(generateIrradiance){
            const pmremGenerator = new THREE.PMREMGenerator( gl );
            scene.environment = pmremGenerator.fromScene(sky).texture;
        }

    }

}


export default EnvironmentSetup