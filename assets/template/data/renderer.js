import * as THREE from 'three';
import Utility from './utility';
import { 
    BloomEffect,
    EffectComposer,
    EffectPass,
    RenderPass,
    FXAAEffect,
    SMAAEffect,
    KawaseBlurPass,
    BlurPass,
    ToneMappingEffect } from "postprocessing";
import { HalfFloatType } from "three";

import * as POSTPROCESSING from "postprocessing"
//import { SSREffect, defaultSSROptions, SSGIEffect, HBAOEffect, TRAAEffect, MotionBlurEffect, VelocityDepthNormalPass } from "realism-effects"
import Logger from './logger';

export default class RenderManager {

    constructor(scene, options, xr) {

        this.scene = scene;
        this.camera = null;
        this.composerFlag = false;

        //Temporary check if device is mobile
        if(Utility.isMobileDevice()){
            Logger.log("Mobile device detected, using mobile renderer");
            this.renderer = this.createPerformanceRenderer(options);
        } else {
            Logger.log("Desktop device detected, using desktop renderer");
            this.renderer = this.createDefaultRenderer(options);
        }

        //this.renderer = this.createFlexibleRenderer(options);
        //this.renderer = this.createDefaultRenderer(options);
        //this.renderer = this.createPerformanceRenderer(options);
        this.composer = null;

        document.body.appendChild(this.renderer.domElement);

    }

    createFlexibleRenderer(options) {

        const renderer = new THREE.WebGLRenderer({
            canvas: this.renderer,
            powerPreference: "high-performance",
            premultipliedAlpha: false,
            depth: false,
            stencil: false,
            antialias: false,
            preserveDrawingBuffer: true
        });
        renderer.outputEncoding = THREE.sRGBEncoding;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.4;
        renderer.setPixelRatio(window.devicePixelRatio);
        renderer.setSize(window.innerWidth, window.innerHeight);

        /*
        const rendererx = new THREE.WebGLRenderer({
            canvas: this.renderer,
            powerPreference: "high-performance",
            premultipliedAlpha: false,
            stencil: false,
            antialias: false,
            alpha: false,
            preserveDrawingBuffer: true
        })

        let renderer = new THREE.WebGLRenderer();
        renderer.outputColorSpace = THREE.SRGBColorSpace;
        renderer.setPixelRatio(window.devicePixelRatio * 1.0);
        renderer.setSize( window.innerWidth, window.innerHeight );
        renderer.autoClear = false;
        */

        this.composerFlag = true;

        return renderer;

    }

    createComposer () {


        const composer = new POSTPROCESSING.EffectComposer(this.renderer);

        const options = {
            enabled: true,
            resolutionScale: 1,
            velocityResolutionScale: 1,
            correctionRadius: 2,
            blend: 0.95,
            correction: 0.1,
            blur: 0,
            blurSharpness: 10,
            blurKernel: 1,
            distance: 10,
            intensity: 1,
            exponent: 1.75,
            maxRoughness: 0.99,
            jitter: 0,
            jitterRoughness: 2,
            roughnessFade: 1,
            fade: 1.03,
            thickness: 3.5,
            ior: 1.75,
            fade: 0,
            steps: 5,
            refineSteps: 6,
            maxDepthDifference: 50,
            missedRays: false
        }

        const ssrEffect = new SSREffect(app.sceneManager.scene3D, app.sceneManager.cameraManager.camera, options);

        const ssrPass = new POSTPROCESSING.EffectPass(app.sceneManager.cameraManager.camera, ssrEffect);

        //composer.addPass(new RenderPass(this.scene, app.sceneManager.cameraManager.camera));
        //const velocityDepthNormalPass = new VelocityDepthNormalPass(app.sceneManager.scene3D, app.sceneManager.cameraManager.camera);
        //composer.addPass(velocityDepthNormalPass);
        
        // SSGI
        //const ssgiEffect = new SSGIEffect(scene, camera, velocityDepthNormalPass, options?)
        
        // TRAA
        //const traaEffect = new TRAAEffect(app.sceneManager.scene3D, app.sceneManager.cameraManager.camera);
        
        // Motion Blur
        //const motionBlurEffect = new MotionBlurEffect(velocityDepthNormalPass);
        
        // HBAO
        //const hbaoEffect = new HBAOEffect(composer, app.sceneManager.cameraManager.camera, app.sceneManager.scene3D);
        
        //const effectPass = new POSTPROCESSING.EffectPass(app.sceneManager.cameraManager.camera, hbaoEffect, traaEffect, motionBlurEffect);
        //const effectPass = new POSTPROCESSING.EffectPass(app.sceneManager.cameraManager.camera, hbaoEffect, traaEffect);
        
        composer.addPass(ssrPass);

        this.composer = composer;




        //https://pmndrs.github.io/postprocessing/public/docs/class/src/effects/FXAAEffect.js~FXAAEffect.html
        //Implement High-Quality bloom: https://github.com/armory3d/armory/pull/2725/files

        //TODO - Create composer based on input from Blender (like a stack)

        console.log("Composer");

        //const composer = new EffectComposer(this.renderer, {frameBufferType: HalfFloatType});
        //composer.addPass(new RenderPass(this.scene, app.sceneManager.cameraManager.camera));
        
        //const blurPass = new KawaseBlurPass({
            // Set your blur options here
            // For example, you can set the height, kernelSize, etc.
        //});
    
        // Add the BlurPass to the composer
        //composer.addPass(blurPass);
        
        //composer.addPass(new EffectPass(app.sceneManager.cameraManager.camera, new SMAAEffect()));
    
        //composer.addPass(new EffectPass(app.sceneManager.cameraManager.camera, new KawaseBlurPass(0.5, 4.0)));
        //composer.addPass(new EffectPass(app.sceneManager.cameraManager.camera, new BloomEffect()));
        //composer.addPass(new EffectPass(app.sceneManager.cameraManager.camera, new ToneMappingEffect()));
        

        //this.composer = composer; // Store the composer in the class

    }


    createPerformanceRenderer = (options) => {

        const renderer = new THREE.WebGLRenderer({
            powerPreference: "high-performance",
            antialias: true,
            stencil: false,
            depth: true
        });
        renderer.setPixelRatio(window.devicePixelRatio * 0.2);
        renderer.setSize( window.innerWidth, window.innerHeight );
        /*
        renderer.physicallyCorrectLights = true;
        renderer.shadowMap.enabled = true;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap; // default THREE.PCFShadowMap
        renderer.toneMappingExposure = 0.02;
        */

        return renderer;

    }

    createDefaultRenderer(options) {
        
        let renderer = new THREE.WebGLRenderer({ antialias: options.graphics.antialiasing });

        if(options.video.fullscreen){
            renderer.setPixelRatio(window.devicePixelRatio * 1.0);
            renderer.setSize(window.innerWidth, window.innerHeight);
        } else {
            renderer.setSize(options.video.width, options.video.height);
            renderer.setPixelRatio(1.0);
        }

        renderer.physicallyCorrectLights = true;
        renderer.shadowMap.enabled = true;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap; // default THREE.PCFShadowMap
        renderer.toneMappingExposure = 1.0;

        return renderer;

    }



}