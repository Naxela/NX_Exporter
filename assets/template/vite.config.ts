// vite.config.js
import { defineConfig } from 'vite';
import path from 'path';

import { createServer as createNetServer } from 'net';
import { WebSocketServer, WebSocket } from 'ws';


// Combined WebSocket and TCP Server Plugin
const combinedServerPlugin = () => ({
  name: 'combined-server',
  configureServer() {
    // Start the WebSocket server on a separate port
    const wss = new WebSocketServer({ port: 3004 });
    console.log(`WebSocket server started on port 3004`);

    wss.on('connection', ws => {
      console.log('WebSocket client connected');
      ws.on('message', message => {
        console.log('received: %s', message);
      });
      ws.send('Connection established with WebSocket server');
    });

    // Function to send data to all connected WebSocket clients
    const sendDataToFrontend = (data) => {
      wss.clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
          client.send(data);
        }
      });
    };

    // Start the TCP server
    const tcpServer = createNetServer(socket => {
      console.log('TCP client connected');
      socket.on('data', data => {
        console.log('TCP Server Received:', data.toString());
        sendDataToFrontend(data.toString()); // Use the shared function here
      });
    });

    tcpServer.listen(3003, () => {
      console.log('TCP server listening on port 3003');
    });
  }
});

// WebSocket Server Plugin

export default defineConfig({

  //Set this so we doesn't get errors
  base: './',

  //We want to resolve the asset path, maybe more in the future
  resolve: {
    alias: {
      'assets': path.resolve(__dirname, 'assets')
    }
  },

  plugins: [combinedServerPlugin()]
  
});