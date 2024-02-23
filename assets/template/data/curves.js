import * as THREE from 'three';
import Logger from './logger';

export default class CurveManager {

    constructor(engine, scene, curveData) {
        
        this.scene = scene;
        this.curveData = curveData;
        this.engine = engine;

        this.curves = [];

    }

    setupCurves() {
        this.curveData.forEach((cData) => {
            // Ensure that spline_data exists and has at least one item
            if (cData.spline_data && cData.spline_data.length > 0) {
                // Assuming spline_data is an array of objects, where each object represents a set of points
                // and you want to create a curve for the first set of points
                // You might need to iterate over spline_data if you have multiple sets of points for each curve
                this.createCurve(cData.spline_data[0].points);
            } else {
                // Log an error or handle cases where spline_data is not as expected
                console.error('Invalid or missing spline_data in curveData', cData);
            }
        });
    }



    createCurve(pointsData) { // Now expecting pointsData to be an array of points
        let curvePath = new THREE.CurvePath();
    
        pointsData.forEach((point, index) => {
            if (index < pointsData.length - 1) {
                let start = new THREE.Vector3(...point.co);
                let end = new THREE.Vector3(...pointsData[index + 1].co);
                let control1 = new THREE.Vector3(...point.handle_right);
                let control2 = new THREE.Vector3(...pointsData[index + 1].handle_left);
    
                let curve = new THREE.CubicBezierCurve3(start, control1, control2, end);
                curvePath.add(curve);
            }
        });

        // Create a geometry from the CurvePath
        let geometry = new THREE.TubeGeometry(curvePath, 20, 0.1, 8, false);
        let material = new THREE.MeshBasicMaterial({ color: 0xff0000 });
        let mesh = new THREE.Mesh(geometry, material);

        // Add the mesh to your scene
        this.scene.add(mesh);

    }

}