import React, { useState, useEffect } from 'react';
import SceneManager from './data/SceneManager';
import SceneManagerXR from './data/SceneManagerXR';
import './NAXApp.css';

function OverlayDiv() {

    return (
        <>
            <div id='NAX-XR-Overlay'></div>
        </>
    )
}

function SocketManager(){

  const port = 5173; //5173;
  const ws = new WebSocket('wss://localhost:' + port);

  ws.onopen = () => {
      console.log('WebSocket connection established');
      ws.send('Hello from client');
  };

  ws.onmessage = (event) => {

      if(event.data.startsWith('NAX')) {

          console.log('Command:', event.data);
          eval(event.data);

      } else {
          console.log('Message from server:', event.data);
      }

  };

  return(
      <>
      </>
  )
}

async function loadProject(projectURL) {
  try {
      const response = await fetch(projectURL);
      if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
      }
      const sceneConfig = await response.json();
      return sceneConfig;
  } catch (error) {
      console.error('Failed to load scene:', error);
      throw error; // Re-throw to catch it in the calling function
  }
}

export default function NAXApp() {
  const [projectManifest, setProjectManifest] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  window.NAX = window.NAX || {};

  useEffect(() => {
    async function fetchAndSetProjectData() {
        try {
            const config = await loadProject("project.nx");
            setProjectManifest(config);
        } catch (error) {
            setError(error);
            console.error(error);
        } finally {
            setIsLoading(false);
        }
    }

    fetchAndSetProjectData();
  }, []); // Empty dependency array means this effect runs once after the initial render

  if (isLoading) return <div>Loading project file...</div>;
  if (error) return <div>Error loading project - Is the path to the project file correct?</div>;

  return (
    <>
    <SocketManager />


    {projectManifest.options.xr && (
        <>
        <OverlayDiv></OverlayDiv>
        <SceneManagerXR projectData={projectManifest} />
        </>
    )}

    {!projectManifest.options.xr && (
        <SceneManager projectData={projectManifest} />
    )}
    </>
  );
}