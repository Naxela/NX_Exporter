import Logger from './logger';

export default class EventManager {

    constructor(sceneManager) {

        this.sceneManager = sceneManager;

    }

    setupEvents(eventList) {
        
        eventList.forEach((event) => {

            if(event == "click" || event == "touchstart") {
                window.addEventListener('click', this.onClickContext);
                window.addEventListener('touchstart', this.onClickContext);
            }

            if(event == "resize") {

                window.addEventListener('resize', this.onResize);
            }

        })


    }

    onResize = () => {

        Logger.log("Resizing...");

        this.sceneManager.cameraManager.camera.aspect = window.innerWidth / window.innerHeight;
        this.sceneManager.cameraManager.camera.updateProjectionMatrix();
        this.sceneManager.renderManager.renderer.setSize( window.innerWidth, window.innerHeight );
    }

    onClickContext = () => {

        if(this.sceneManager.listener == null) {
            return;
        }

        Logger.log("Resuming playback...");

        if (this.sceneManager.listener.context.state === 'suspended') {
            this.sceneManager.listener.context.resume().then(() => {
                console.log('Playback resumed');
            });
        }

        document.removeEventListener('click', this.onClickContext);
        document.removeEventListener('touchstart', this.onClickContext);

    }

}