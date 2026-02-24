export function initStage4(containerId) {
    const container = document.getElementById(containerId);
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0f172a);

    const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 100);
    camera.position.set(0, 0, 12);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    scene.add(new THREE.AmbientLight(0xffffff, 0.8));

    // Bar Chart (MOIC)
    const barGroup = new THREE.Group();
    const barGeo = new THREE.BoxGeometry(1, 1, 1);
    const barMat = new THREE.MeshStandardMaterial({ color: 0xf97316 });

    const bar1 = new THREE.Mesh(barGeo, barMat);
    bar1.scale.y = 2;
    bar1.position.set(-2, 0, 0);

    const bar2 = new THREE.Mesh(barGeo, barMat);
    bar2.scale.y = 5;
    bar2.position.set(0, 1.5, 0);

    const bar3 = new THREE.Mesh(barGeo, barMat);
    bar3.scale.y = 1;
    bar3.position.set(2, -0.5, 0);

    barGroup.add(bar1, bar2, bar3);
    scene.add(barGroup);

    // Labels (Spheres above bars)
    const labelGeo = new THREE.SphereGeometry(0.4, 16, 16);
    const labelMat = new THREE.MeshBasicMaterial({ color: 0xffffff });

    const l1 = new THREE.Mesh(labelGeo, labelMat);
    l1.position.set(-2, 2, 0);

    const l2 = new THREE.Mesh(labelGeo, labelMat);
    l2.position.set(0, 4.5, 0);

    const l3 = new THREE.Mesh(labelGeo, labelMat);
    l3.position.set(2, 0.5, 0);

    barGroup.add(l1, l2, l3);

    function animate() {
        requestAnimationFrame(animate);
        barGroup.rotation.y = Math.sin(Date.now() * 0.0005) * 0.2;
        renderer.render(scene, camera);
    }
    animate();

    window.addEventListener('resize', () => {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    });
}
