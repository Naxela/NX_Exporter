import * as NX from './data/nx';

const app = new NX.NXEngine("/assets/project.nx");
//app.init(app).then(app.animate);
app.init(app).then(app.startAnimationLoop);