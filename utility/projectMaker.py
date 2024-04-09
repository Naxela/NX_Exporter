import bpy, os
from ..utility import util

def createPackageJson(name, version):
    package_json_content = {
    "name": "nx-runtime-react",
    "private": True,
    "version": "0.0.0",
    "type": "module",
    "scripts": {
      "dev": "vite --host",
      "dev2": "node server.js",
      "dev3": "node server.js",
      "dev4": "gltf-transform optimize public/Scene.glb public/Scene.glb --texture-compress webp && node server.js",
      "build": "tsc && vite build",
      "build-free": "vite build",
      "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
      "preview": "vite preview"
    },
    "dependencies": {
      "@gltf-transform/cli": "^3.10.0",
      "@react-three/drei": "^9.101.0",
      "@react-three/fiber": "^8.15.19",
      "@react-three/postprocessing": "^2.16.2",
      "@react-three/xr": "^5.7.1",
      "mkcert": "^3.2.0",
      "express": "^4.18.3",
      "postprocessing": "^6.35.2",
      "react": "^18.2.0",
      "react-dom": "^18.2.0",
      "selfsigned": "^2.4.1",
      "three": "^0.162.0",
      "ws": "^8.16.0"
    },
    "devDependencies": {
      "@types/react": "^18.2.56",
      "@types/react-dom": "^18.2.19",
      "@typescript-eslint/eslint-plugin": "^7.0.2",
      "@typescript-eslint/parser": "^7.0.2",
      "@vitejs/plugin-react": "^4.2.1",
      "eslint": "^8.56.0",
      "eslint-plugin-react-hooks": "^4.6.0",
      "eslint-plugin-react-refresh": "^0.4.5",
      "typescript": "^5.2.2",
      "vite": "^5.1.4",
      "vite-plugin-mkcert": "^1.17.5"
    }
  }

    return package_json_content


def createExpressServer(assetsPath, port=5173, tcpport=5174):

  convertedPath = assetsPath.replace(os.sep, '/')

  serverConfig = """
// server.js
import express from 'express';
import { createServer as createViteServer } from 'vite';
import * as path from 'path';
import { fileURLToPath } from 'url';
import { createServer as createHttpsServer } from 'https';
import { createServer as createNetServer } from 'net';
import { WebSocketServer, WebSocket } from 'ws';
import fs from 'fs'; // To read the certificate files
import { createCA, createCert } from "mkcert";
//const https = require("https");


/*
https://github.com/remix-run/remix/discussions/8046

import https from "node:https";
import { createServer } from "vite";

const server = https.createServer(
  {
    key: fs.readFileSync("localhost-key.pem"),
    cert: fs.readFileSync("localhost.pem"),
  },
  app
);

let vite = await createServer({
  server: {
    middlewareMode: true,
    hmr: {
      server,        // <=========  user `server.hmr.server`
    }
  }
})
*/



async function startServer() {

  const app = express();

  const __filename = fileURLToPath(import.meta.url);
  const __dirname = path.dirname(__filename);

  // Serve static assets from the external folder
  app.use('/assets', express.static('""" + convertedPath + """'));
  app.use('/modules', express.static(path.join(__dirname, 'node_modules')));

  // When in development mode, use Vite as a middleware
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: 'html' },
    });
    app.use(vite.middlewares);
  }

  const ca = await createCA({
    organization: "Naxela",
    countryCode: "DK",
    state: "Greenland",
    locality: "Nuuk",
    validity: 365
  });

  const cert = await createCert({
    ca: { key: ca.key, cert: ca.cert },
    domains: ["127.0.0.1", "localhost"],
    validity: 365
  });

  const sslOptions = {
    //key: readFileSync('ca.key'),
    //cert: readFileSync('ca.crt')
    key: cert.key,
    cert: cert.cert
  };

  //const options = {
  //  key: fs.readFileSync('ca.key'),
  //  cert: fs.readFileSync('ca.crt')
  //};

  //const httpServer = createHttpServer(app);
  const httpsServer = createHttpsServer(sslOptions, app);
  const wss = new WebSocketServer({ server: httpsServer });

  // WebSocket connection handling
  wss.on('connection', (ws) => {
    console.log('WebSocket client connected');

    // Listen for messages from the frontend
    ws.on('message', (message) => {
      console.log('Received message from frontend:', message);
    });

    // Example relay function to send data to all connected WebSocket clients
  });

  const sendDataToFrontend = (data) => {
    wss.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(data);
      }
    });
  };

  // Set up the TCP server for communication with Blender/Python
  const tcpServer = createNetServer((socket) => {
    console.log('Blender/Python client connected via TCP');

    socket.on('data', (data) => {
      console.log('Received data from Blender/Python:', data.toString());
      sendDataToFrontend(data.toString()); // Use the function to relay messages
    });
  });

  const tcpport = """ + str(tcpport) + """;
  tcpServer.listen(tcpport, '0.0.0.0', () => {
    console.log('TCP server listening for Blender/Python connections');
  });

  const port = """ + str(port) + """;
  httpsServer.listen(port, '0.0.0.0', () => {
    console.log(`HTTPS/WebSocket server listening on https://localhost:${port}`);
  });
  
}

startServer();
"""

  return serverConfig