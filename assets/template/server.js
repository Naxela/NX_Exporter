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
  //app.use('/assets', express.static('C:/Users/kleem/Desktop/LMX/nx-build'));
  //app.use('/modules', express.static(path.join(__dirname, 'node_modules')));

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

    socket.on('end', () => {
      console.log('Blender/Python client disconnected');
    })

    socket.on('error', (error) => {

      if(error.code === 'ECONNREFUSED') {
        console.log('Blender/Python client refused connection');

        //Close the socket
        socket.end();
        
      } else {
        console.log('Blender/Python client error:', error.code);
      }

    })

  });

  tcpServer.listen(3001, () => {
    console.log('TCP server listening for Blender/Python connections on 3001');
  });

  const port = 3001;
  httpServer.listen(port, () => {
    console.log(`HTTP/WebSocket server listening on http://localhost:${port}`);
  });
  
}

startServer();