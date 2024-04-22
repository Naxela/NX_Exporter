import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

export default class OrbitCamControls {
    object: any;
    controls: null;

    //@NXPROP
    public target = new THREE.Vector3( 0, 0, 0 );

    constructor(object) {
        this.object = object;
        this.controls = null;

    }

    NotifyOnInit() {
        this.controls = new OrbitControls( this.object, NAX.renderer.domElement );
        this.controls.enableDamping = true;
        this.controls.target = this.target;
    }

    NotifyOnUpdate() {
        this.controls.update();
    }

}