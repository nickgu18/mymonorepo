export function initStage1(containerId) {
    const container = document.getElementById(containerId);
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0f172a); // Match card bg

    const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 100);
    camera.position.set(0, 0, 10);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight.position.set(5, 5, 5);
    scene.add(dirLight);

    // CSV Blocks
    const geometry = new THREE.BoxGeometry(2.5, 3, 0.2);

    function createBlock(color, x, y, z) {
        const material = new THREE.MeshStandardMaterial({ color: color, roughness: 0.3 });
        const mesh = new THREE.Mesh(geometry, material);
        mesh.position.set(x, y, z);

        // Add "lines"
        for (let i = 0; i < 5; i++) {
            const lineGeo = new THREE.BoxGeometry(2, 0.2, 0.05);
            const lineMat = new THREE.MeshBasicMaterial({ color: 0xffffff, opacity: 0.5, transparent: true });
            const line = new THREE.Mesh(lineGeo, lineMat);
            line.position.set(0, 1 - i * 0.5, 0.15);
            mesh.add(line);
        }
        return mesh;
    }

    const csv1 = createBlock(0x3b82f6, -2, 0, 0);
    const csv2 = createBlock(0x8b5cf6, 2, 0, 0);
    scene.add(csv1);
    scene.add(csv2);

    function animate() {
        requestAnimationFrame(animate);
        csv1.rotation.y = Math.sin(Date.now() * 0.001) * 0.3;
        csv2.rotation.y = Math.sin(Date.now() * 0.001 + 1) * 0.3;
        renderer.render(scene, camera);
    }
    animate();

    // Handle Resize
    window.addEventListener('resize', () => {
        if (!container) return;
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    });
}
