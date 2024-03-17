import { useRef, useEffect, useContext } from 'react';
import { PerspectiveCamera, OrthographicCamera } from '@react-three/drei'
import { Matrix4, Quaternion, Vector3 } from 'three'
import { ScriptManagerContext } from './Scripts'; // Import your ScriptManager context

function Camera({ cameraData }) {

    const cameraRef = useRef();
    const scriptManager = useContext(ScriptManagerContext); // Use the ScriptManager context

    useEffect(() => {

        if (!cameraRef.current) return;
        if(!cameraData) return

        const camera = cameraRef.current;

        const matrix = new Matrix4();
        matrix.fromArray(cameraData.matrix).transpose();
        
        const position = new Vector3();
        const quaternion = new Quaternion();
        const scale = new Vector3();
        matrix.decompose(position, quaternion, scale);

        camera.position.copy(position);
        camera.quaternion.copy(quaternion);
        camera.scale.copy(scale);

        camera.updateProjectionMatrix();

        if (cameraData && cameraData.modules) {
          (async () => {
            for (const moduleName of cameraData.modules) {
              try {
                const Module = await import(`../Sources/${moduleName}.tsx`);
                const moduleInstance = new Module.default(camera);
                const identifier = `${moduleName}_${camera}`; // Construct a unique identifier
                scriptManager.addScript(camera, moduleInstance, identifier);
              } catch (error) {
                console.error(`Failed to load module: ${moduleName}`, error);
              }
            }
          })();
        }

    }, [cameraData]);

    switch (cameraData.type) {
        case "Perspective":

            return (
                <>
                <PerspectiveCamera ref={cameraRef} fov={cameraData.fov} aspect={cameraData.aspect} near={cameraData.near}  far={cameraData.far} makeDefault={cameraData.active} />
                </>
            )
        
        case "Orthographic":
            return (
                <OrthographicCamera ref={cameraRef} makeDefault={cameraData.active} />
            )

        default:
            return null
    }

}

function Cameras({ cameraData }) {

    return (
      <>
        {cameraData.map((data, index) => (
          <Camera key={index} cameraData={data} />
        ))}
      </>
    );
  }

export default Cameras