import fs from 'fs-extra';
import path from 'path';

const srcDir = path.join(process.cwd(), 'assets');
const destDir = path.join(process.cwd(), 'dist', 'assets');

fs.copy(srcDir, destDir)
  .then(() => console.log('Assets copied successfully!'))
  .catch(err => console.error(err));