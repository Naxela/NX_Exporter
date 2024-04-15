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

function useLightmapPreloader(sceneManifest) {
  const [lightmaps, setLightmaps] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!sceneManifest || !sceneManifest.scene_meshes) {
      console.error("Scene manifest is not valid");
      setLoading(false);
      return;
    }

    const loadLightmaps = async () => {
      console.log("Loading lightmaps...");
      const loader = new RGBELoader();
      const promises = Object.entries(sceneManifest.scene_meshes).map(async ([key, value]) => {

        if(value.lightmaps == undefined) {
          return null;
        }

        const path = `./Lightmaps/${value.lightmaps}.hdr`;
        try {
          const lightmap = await new Promise((resolve, reject) => {
            loader.load(path, resolve, undefined, reject);
          });
          return { key: value.lightmaps, lightmap };
        } catch (error) {
          console.error(`Failed to load lightmap for ${value.lightmaps}:`, error);
          return null;
        }
      });

      try {
        const loadedLightmapsResults = await Promise.all(promises);
        // Filter out any null results due to failed loads
        const loadedLightmaps = loadedLightmapsResults.reduce((acc, result) => {
          if (result) acc[result.key] = result.lightmap;
          return acc;
        }, {});
        setLightmaps(loadedLightmaps);
      } catch (error) {
        console.error("Failed to load lightmaps:", error);
      } finally {
        setLoading(false);
      }
    };

    loadLightmaps();
  }, [sceneManifest]);

  return [lightmaps, loading];
}

function Models({data}) { // Receive the path as a prop

  const { modelPath, sceneManifest } = data;
  const [lightmapTextures, lightmapsLoading] = useLightmapPreloader(sceneManifest);

  const { gltf, scene, animations } = useGLTF(modelPath);
  const { actions } = useAnimations(animations, scene);

  const sceneMeshIDList = sceneManifest.scene_meshes.map(item => item.identifier);
  const scriptManager = useContext(ScriptManagerContext); // Use the ScriptManager context
  const mixerRef = useRef(); // Ref to hold the mixer


  useEffect(() => {

    //animations.forEach((clip) => {
    //  actions[clip.name]?.play();
    //});

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
      const meshData = sceneManifest.scene_meshes.find(item => item.identifier === child_id);
  
      // Adjust properties based on meshData
      if (meshData) {
        
        if(meshData.lightmaps) {
          if(lightmapTextures[meshData.lightmaps] != undefined) {
            const texture = lightmapTextures[meshData.lightmaps];
            texture.flipY = false; // Adjust texture property as needed
            texture.channel = 1;
            child.material.lightMap = texture; // Apply the lightmap texture
            child.material.needsUpdate = true; // Ensure material updates to reflect the new texture
          } else {
            console.log("Lightmap assigned, but not found:", meshData.lightmaps);
          }

        }
        
        if(meshData.active_action && meshData.active_action != "none") {

          child["default_action"] = meshData.active_action;

        }

        // Cast Shadows
        if (meshData.cast_shadows) {
          child.castShadow = true;
        }
  
        // Receive Shadows
        if (meshData.receive_shadows) {
          child.receiveShadow = true;
        }
  
        // Visibility (spawn)
        if (meshData.spawn) {
          child.visible = true;
        } else {
          child.visible = false;
        }

        //TODO PARENTING

        //TODO COMPONENTS

        if (meshData && meshData.modules) {
          for (const moduleName of meshData.modules) {
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
  
    });

    return () => mixerRef.current?.stopAllAction();

  }, [scene, lightmapTextures, sceneMeshIDList, sceneManifest.scene_meshes]); // Depend on relevant states and props


  useFrame((state, delta) => mixerRef.current?.update(delta)); // Update the mixer on each frame

  return (
    <primitive object={scene} />
  )

}

export default Models