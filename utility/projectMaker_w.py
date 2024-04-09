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
      "dev3": "mkcert create-ca && node server.js",
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
import { createServer } from 'https';
import { readFileSync } from 'fs';
import { createCA, createCert } from "mkcert";

const ca = await createCA({
  organization: "Hello CA",
  countryCode: "NP",
  state: "Bagmati",
  locality: "Kathmandu",
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

const app = express();

app.get('/', (req, res) => {
  res.send('Hello, HTTPS world!');
});

createServer(sslOptions, app).listen(5173, () => {
  console.log('HTTPS server running on https://localhost:5173');
});


"""

  return serverConfig