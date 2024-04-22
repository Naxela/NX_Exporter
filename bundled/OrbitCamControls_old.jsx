import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

export default class OrbitCamControls {

    constructor(object) {
        this.object = object;
        this.controls = null;

    }

    NotifyOnInit() {
        this.controls = new OrbitControls( this.object, NAX.renderer.domElement );
        this.controls.enableDamping = true;
    }

    NotifyOnUpdate() {
        this.controls.update();
    }

}