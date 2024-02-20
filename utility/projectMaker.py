import os
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
            "three": "^0.161.0"
        }
    }

    return package_json_content

def createExpressServer(assetsPath, port):

  convertedPath = assetsPath.replace(os.sep, '/')

  serverConfig = """
// server.js
import express from 'express';
import { createServer as createViteServer } from 'vite';
import * as path from 'path';
import { fileURLToPath } from 'url';

async function startServer() {
  const app = express();
  const __filename = fileURLToPath(import.meta.url);
  const __dirname = path.dirname(__filename);

  // Serve static assets from the external folder
  app.use('/assets', express.static('"""+convertedPath+"""'));
  app.use('/modules', express.static(path.join(__dirname, 'node_modules')));

  // When in development mode, use Vite as a middleware
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: 'html' },
      // Vite config options...
    });
    app.use(vite.middlewares);
  }

  // Additional routes or middleware for your app
  // app.get('/', (req, res) => { ... });

  const port = """ + str(port) + """;
  app.listen(port, () => {
    console.log(`Server listening on http://localhost:${port}`);
  });
}

startServer();
"""

  return serverConfig