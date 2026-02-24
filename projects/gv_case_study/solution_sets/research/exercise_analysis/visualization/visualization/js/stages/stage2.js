export function initStage2(containerId) {
    const container = document.getElementById(containerId);
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0f172a);

    const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 100);
    camera.position.set(0, 0, 12);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    scene.add(new THREE.AmbientLight(0xffffff, 0.8));

    // Timeline Line
    const lineGeo = new THREE.BoxGeometry(10, 0.1, 0.1);
    const lineMat = new THREE.MeshBasicMaterial({ color: 0x94a3b8 });
    const line = new THREE.Mesh(lineGeo, lineMat);
    scene.add(line);

    // T0 Marker (Vertical Line)
    const t0Geo = new THREE.BoxGeometry(0.1, 4, 0.1);
    const t0Mat = new THREE.MeshBasicMaterial({ color: 0xf59e0b }); // Amber
    const t0 = new THREE.Mesh(t0Geo, t0Mat);
    scene.add(t0);

    // Label for T0
    // (Simplified: just a glowing orb at top of T0)
    const t0Label = new THREE.Mesh(
        new THREE.SphereGeometry(0.3, 16, 16),
        new THREE.MeshBasicMaterial({ color: 0xf59e0b })
    );
    t0Label.position.set(0, 2.2, 0);
    scene.add(t0Label);

    // Data Points
    const points = [];
    const pointGeo = new THREE.SphereGeometry(0.2, 8, 8);
    const validMat = new THREE.MeshBasicMaterial({ color: 0x10b981 }); // Green
    const invalidMat = new THREE.MeshBasicMaterial({ color: 0xef4444 }); // Red

    function spawnPoint() {
        const p = new THREE.Mesh(pointGeo, validMat);
        p.position.set(-6, (Math.random() - 0.5) * 2, 0);
        p.userData = { speed: 0.05 + Math.random() * 0.05 };
        scene.add(p);
        points.push(p);
    }

    function animate() {
        requestAnimationFrame(animate);

        if (Math.random() < 0.05) spawnPoint();

        for (let i = points.length - 1; i >= 0; i--) {
            const p = points[i];
            p.position.x += p.userData.speed;

            // Check T0 crossing
            if (p.position.x > 0) {
                p.material = invalidMat;
                p.scale.multiplyScalar(0.95); // Shrink
            }

            if (p.position.x > 6 || p.scale.x < 0.1) {
                scene.remove(p);
                points.splice(i, 1);
            }
        }

        renderer.render(scene, camera);
    }
    animate();

    window.addEventListener('resize', () => {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    });
}
