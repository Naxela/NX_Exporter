import { React, useEffect, useRef, useContext, useState } from 'react'
import { useGLTF, useAnimations } from '@react-three/drei'
import {RGBELoader} from "three/examples/jsm/loaders/RGBELoader";
import { ScriptManagerContext } from './Scripts'; // Import your ScriptManager context
import { act, useLoader, useThree, useFrame } from '@react-three/fiber'
import { AnimationMixer } from 'three';

function getChildID(IDList, child) { 

if(child.name != "Scene") {

    let internalIdentifier = child.userData.nx_id;

    if(internalIdentifier == undefined) {

    const parent = child.parent;

    if(parent.userData.nx_id != undefined) {
        internalIdentifier = parent.userData.nx_id;
    }
    else {
        return false;
    }

    }

    const ObjectID = IDList.find(item => item == internalIdentifier);
    return ObjectID;

} else {

    return false;

}

}

function Empty({data}) { // Receive the path as a prop

  const { modelPath, sceneManifest } = data;
  //const [lightmapTextures, lightmapsLoading] = useLightmapPreloader(sceneManifest);

  const { gltf, scene, animations } = useGLTF(modelPath);
  const { actions } = useAnimations(animations, scene);

  const sceneMeshIDList = sceneManifest.scene_empties.map(item => item.identifier);
  const scriptManager = useContext(ScriptManagerContext); // Use the ScriptManager context
  const mixerRef = useRef(); // Ref to hold the mixer


  useEffect(() => {

    // Initialize the mixer with the loaded GLTF scene
    mixerRef.current = new AnimationMixer(scene);
    if(window.NAX != undefined) {
      window.NAX["mixer"] = mixerRef.current;

      if (animations.length) {
        animations.forEach((clip) => {
          window.NAX["scene"].animations = [...window.NAX["scene"].animations, clip];
        });
      }
    }

    scene.traverse(async child => {

        const child_id = getChildID(sceneMeshIDList, child);

        if(child_id) {

            const emptyData = sceneManifest.scene_empties.find(item => item.identifier === child_id);

            if(emptyData) {
                

                if(emptyData.active_action && emptyData.active_action != "none") {

                    child["default_action"] = emptyData.active_action;
        
                }

                // Visibility (spawn)
                if (emptyData.spawn) {
                    child.visible = true;
                } else {
                    child.visible = false;
                }

                if (emptyData && emptyData.modules) {
                    for (const moduleName of emptyData.modules) {
                        try {
                            const Module = await import(`../Sources/${moduleName}.tsx`);
                            const identifier = `${moduleName}_${child_id}`;
                            
                            const moduleInstance = scriptManager.getOrCreateInstance(Module, child, identifier);
                            scriptManager.addScript(child, moduleInstance, identifier);
                
                        } catch (error) {
                            console.warn("NAX: Module not found:", moduleName, "Trying javascript");
                            try {
                                const Module = await import(`../Sources/${moduleName}.jsx`);
                                const identifier = `${moduleName}_${child_id}`;
                
                                const moduleInstance = scriptManager.getOrCreateInstance(Module, child, identifier);
                                scriptManager.addScript(child, moduleInstance, identifier);
                
                            } catch (error) {
                                console.error(`Failed to load module: ${moduleName}`, error);
                            }
                        }
                    }
                } 



            }

        }
        

    });

    return () => mixerRef.current?.stopAllAction();

  }, [scene, sceneMeshIDList, sceneManifest.scene_meshes]); // Depend on relevant states and props


  useFrame((state, delta) => mixerRef.current?.update(delta)); // Update the mixer on each frame

  return (
    <></>
  )

}

export default Empty