export function initStage8(containerId) {
    const container = document.getElementById(containerId);
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0f172a);

    const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 100);
    camera.position.set(0, 0, 15);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    scene.add(new THREE.AmbientLight(0xffffff, 0.5));
    const light = new THREE.DirectionalLight(0xffffff, 0.8);
    light.position.set(0, 5, 5);
    scene.add(light);

    // Ranking Bars
    const bars = [];
    const numBars = 5;
    const geometry = new THREE.BoxGeometry(4, 0.5, 0.5);

    for (let i = 0; i < numBars; i++) {
        const material = new THREE.MeshStandardMaterial({ color: 0xa855f7 });
        const bar = new THREE.Mesh(geometry, material);
        bar.position.y = (i - numBars / 2) * 1.2;
        bar.userData = {
            baseY: bar.position.y,
            offset: Math.random() * 100
        };
        scene.add(bar);
        bars.push(bar);
    }

    function animate() {
        requestAnimationFrame(animate);

        // Gentle floating and reordering illusion
        bars.forEach((bar, i) => {
            bar.position.y = bar.userData.baseY + Math.sin((Date.now() + bar.userData.offset) * 0.002) * 0.2;
        });

        renderer.render(scene, camera);
    }
    animate();

    window.addEventListener('resize', () => {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    });
}
