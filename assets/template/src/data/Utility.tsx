export default class Utility {

    static getGlobal = (property) => {

        if (typeof window !== 'undefined') {
            // Browser environment
            return window[property];
        } else if (typeof global !== 'undefined') {
            // Node.js environment
            return global[property];
        }


    }

    static setGlobal = (property, value) => {

        if (typeof window !== 'undefined') {
            // Browser environment
            window[property] = value;
        } else if (typeof global !== 'undefined') {
            // Node.js environment
            global[property] = value;
        }

    }

    static loadProject = async(project) => {

        try {

            const response = await fetch(project);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const text = await response.text();
            
            return JSON.parse(text);

        } catch (e) {

            //ErrorManager.catchError("ERROR: CAN'T FIND ASSET FOLDER");
            //ErrorManager.catchError(e);

            return null;

        }
        
    }

    static findObjectByName(scene, name) {
        let object = null;

        scene.traverse(function (child) {
            if (child.name == name) {
                console.log("Found", child);
                object = child;
                return;
            }
        });

        return object;
        
    }

    static findObjectById(scene, id) {

        console.log("Searching", id);

        let object = null;

        scene.traverse(function (child) {

            if (child.userData.nx_id == id) {
                console.log("Found", child);
                object = child;
                return;
            }

        })

        return object;
        
    }

    static findAnimationByName(scene, name) {

        let animations = scene.animations;
    
        for (let i = 0; i < animations.length; i++) {
            if (animations[i].name == name) {
                return animations[i];
            }
        }
    
        // Return null if no animation with the given name is found
        return null;
    }
    

    static wattToLumens(watts){
        return watts / 10;
        //return (683 * watts)  / ( 4 * Math.pi)
        //const LUMENS_PER_WATT = 683;
        //watts * LUMENS_PER_WATT / (4 * Math.PI);
    }

    static isMobileDevice() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }

}