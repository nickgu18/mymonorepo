export function initStage3(containerId) {
    const container = document.getElementById(containerId);
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0f172a);

    const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 100);
    camera.position.set(0, 0, 12);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(2, 2, 5);
    scene.add(light);
    scene.add(new THREE.AmbientLight(0x404040));

    // "Raw" Text Representation (Cube)
    const rawGeo = new THREE.BoxGeometry(2, 2, 2);
    const rawMat = new THREE.MeshStandardMaterial({ color: 0xf43f5e, wireframe: true });
    const rawObj = new THREE.Mesh(rawGeo, rawMat);
    rawObj.position.set(-3, 0, 0);
    scene.add(rawObj);

    // Arrow
    const arrowGeo = new THREE.ConeGeometry(0.5, 1, 32);
    const arrowMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
    const arrow = new THREE.Mesh(arrowGeo, arrowMat);
    arrow.rotation.z = -Math.PI / 2;
    arrow.position.set(0, 0, 0);
    scene.add(arrow);

    // "Feature" Vector (Sphere)
    const featGeo = new THREE.SphereGeometry(1.2, 32, 32);
    const featMat = new THREE.MeshStandardMaterial({ color: 0x10b981 });
    const featObj = new THREE.Mesh(featGeo, featMat);
    featObj.position.set(3, 0, 0);
    scene.add(featObj);

    function animate() {
        requestAnimationFrame(animate);

        rawObj.rotation.x += 0.01;
        rawObj.rotation.y += 0.01;

        // Pulse effect for feature
        const scale = 1 + Math.sin(Date.now() * 0.003) * 0.1;
        featObj.scale.set(scale, scale, scale);

        renderer.render(scene, camera);
    }
    animate();

    window.addEventListener('resize', () => {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    });
}
