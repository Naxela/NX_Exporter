import { OrbitControls } from '/modules/three/examples/jsm/controls/OrbitControls.js';
//import { OrbitControls } from '/modules/three/addons/controls/OrbitControls.js';

export default class OrbitCamControls {
    constructor(object) {
        this.object = object;
    }

    NotifyOnInit() {
        new OrbitControls( this.object, app.renderManager.renderer.domElement );
    }

    NotifyOnUpdate() {
    }

}