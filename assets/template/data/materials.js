import Logger from './logger';

export default class MaterialManager {

    constructor() {

        this.materials = null;

    }

    init = () => {

        this.materials = [];

    }

    storeSceneMaterials = (scene) => {

        // Iterate all scene objects and store their materials
        
        scene.traverse((object) => {
            if (object.isMesh) {
                if (object.material) {
                    if (Array.isArray(object.material)) {

                        Logger.log("Mat is array");
                        object.material.forEach((material) => {

                            this.storeMaterial(material);

                        });

                    } else {

                        this.storeMaterial(object.material);

                    }
                }
            }
        });
    }    

    storeMaterial = (material) => {

        this.materials.push(material);

    }


}