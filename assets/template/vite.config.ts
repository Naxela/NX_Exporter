// vite.config.js
import { defineConfig } from 'vite';
import path from 'path';
import { dynamicImportResolver } from './resolve_dynamic_imports.js';

export default defineConfig({

  base: './',

  resolve: {
    alias: {
      'assets': path.resolve(__dirname, 'assets')
    }
  }
  // ... other configurations
});