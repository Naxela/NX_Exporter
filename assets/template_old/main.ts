import * as NX from './src/data/nx';

const app = new NX.NXEngine("assets/project.nx");
app.init(app).then(app.startAnimationLoop);