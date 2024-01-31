import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

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