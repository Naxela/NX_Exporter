import bpy, os
from ..utility import util

def createPackageJson(name, version):
    package_json_content = {
        "name": util.get_file_name(),
        "version": "1.0.0",
        "type": "module",
        "scripts": {
            "dev": "node server.js",
            "build": "vite build",
        },
        "devDependencies": {
            "typescript": "^5.2.2",
            "vite": "^5.1.0"
        },
        "dependencies": {
            "express": "^4.18.2",
            "postprocessing": "^6.34.3",
            "realism-effects": "^1.1.2",
            "stats.js": "^0.17.0",
            "three": "^0.161.0",
            "ws": "^8.16.0"
        }
    }

    return package_json_content

def createImporterMapfile(assetsPath):
   
  map = []
  

  for obj in bpy.data.objects:
    for module in obj.NX_UL_ModuleList:
         
        name = module.nx_module_script
        map.append(name)

  print("MODULE MAP!")
  print(map)

  for file in map:
     
    print("import " + file + " from '/assets/Sources/" + file + ".js';")

def createExpressServer(assetsPath, port=3002, tcpport=3003):

  convertedPath = assetsPath.replace(os.sep, '/')

  serverConfig = """
// server.js
import express from 'express';
import { createServer as createViteServer } from 'vite';
import * as path from 'path';
import { fileURLToPath } from 'url';
import { createServer as createHttpServer } from 'http';
import { createServer as createNetServer } from 'net';
import { WebSocketServer, WebSocket } from 'ws';

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

  const httpServer = createHttpServer(app);
  const wss = new WebSocketServer({ server: httpServer });

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
  tcpServer.listen(tcpport, () => {
    console.log('TCP server listening for Blender/Python connections');
  });

  const port = """ + str(port) + """;
  httpServer.listen(port, () => {
    console.log(`HTTP/WebSocket server listening on http://localhost:${port}`);
  });
  
}

startServer();
"""

  return serverConfig