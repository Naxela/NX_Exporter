import Utility from "../../data/utility";

export default class PlayAnimation {
    constructor(object) {
        this.object = object;
    }

    NotifyOnInit() {
        //We find the default animation for the object as set in Blender
        let defaultAnimation = Utility.findAnimationByName(app.sceneManager, this.object.default_action);

        if(defaultAnimation) {
            app.sceneManager.mixer.clipAction(defaultAnimation).play();
        }
    }

    NotifyOnUpdate() {
        // Update logic here
    }

}