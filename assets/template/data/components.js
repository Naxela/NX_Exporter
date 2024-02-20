import Logger from './logger';
import Utility from './utility'

export default class ComponentManager {

    constructor(engine){

        this.engine = engine;
        this.components = [];
        this.componentPairs = [];
        
    }

    attach = (obj_id, component) => {

        let pair = {[obj_id] : component};

        this.componentPairs.push(pair);

        Logger.log("Attached component: " + component);

    }

    setupComponents = async () => {

        Logger.log("Setting up components...");

        Logger.log(this.componentPairs);

        for (const pair of this.componentPairs) {
            let obj_id = Object.keys(pair)[0];
            let component = pair[obj_id];
    
            let object = Utility.findObjectById(this.engine.sceneManager.scene3D, obj_id);
    
            if (object) {

                Logger.log("Setting up component: " + component.constructor.name);

                let moduleComponent = await this.loadComponent(object, component);
    
                if (moduleComponent) {
                    this.components.push(moduleComponent);
                }
            } else {

                Logger.log("Object not found: " + obj_id);

            }
        }
    }

    async loadComponent (object, componentName) {
        try {

            Logger.log("Loading component: " + componentName);

            // Using Webpack magic comments to provide more context about dynamic imports
            const ModuleClass = await import(
              /* @vite-ignore */
              `/assets/Sources/${componentName}.js`
            );

            //console.log("Loaded module");
    
            // Dynamically set the prototype of the loaded class to BaseComponent
            Object.setPrototypeOf(ModuleClass.default.prototype, BaseComponent.prototype);
    
            // Create an instance of the dynamically loaded component
            const componentInstance = new ModuleClass.default(object);

            //console.log(componentInstance.NotifyOnInit());
            //let componentInstance = new ModuleClass();

            return componentInstance;
            
        } catch (error) {
            console.error("Failed to load component:", error);
        }
    }
    
}

export class BaseComponent {

    constructor(object) {

        this.object = object;

    }

    NotifyOnInit() {
        // Initial setup logic here
    }

    NotifyOnUpdate() {
        // Update logic here
    }
}