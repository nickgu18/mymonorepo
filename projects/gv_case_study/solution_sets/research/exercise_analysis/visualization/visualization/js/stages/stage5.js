export function initStage5(containerId) {
    const container = document.getElementById(containerId);
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0f172a);

    const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 100);
    camera.position.set(0, 0, 15);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    scene.add(new THREE.AmbientLight(0xffffff, 0.5));
    const light = new THREE.PointLight(0xffffff, 1);
    light.position.set(5, 5, 5);
    scene.add(light);

    // Tree Structure
    const treeGroup = new THREE.Group();

    // Root
    const nodeGeo = new THREE.SphereGeometry(0.5, 16, 16);
    const nodeMat = new THREE.MeshStandardMaterial({ color: 0x22c55e });
    const root = new THREE.Mesh(nodeGeo, nodeMat);
    root.position.set(0, 3, 0);
    treeGroup.add(root);

    // Level 1
    const l1a = new THREE.Mesh(nodeGeo, nodeMat); l1a.position.set(-2, 1, 0);
    const l1b = new THREE.Mesh(nodeGeo, nodeMat); l1b.position.set(2, 1, 0);
    treeGroup.add(l1a, l1b);

    // Level 2
    const l2a = new THREE.Mesh(nodeGeo, nodeMat); l2a.position.set(-3, -1, 0);
    const l2b = new THREE.Mesh(nodeGeo, nodeMat); l2b.position.set(-1, -1, 0);
    const l2c = new THREE.Mesh(nodeGeo, nodeMat); l2c.position.set(1, -1, 0);
    const l2d = new THREE.Mesh(nodeGeo, nodeMat); l2d.position.set(3, -1, 0);
    treeGroup.add(l2a, l2b, l2c, l2d);

    // Lines
    const lineMat = new THREE.LineBasicMaterial({ color: 0xffffff, opacity: 0.3, transparent: true });
    function connect(p1, p2) {
        const geo = new THREE.BufferGeometry().setFromPoints([p1, p2]);
        return new THREE.Line(geo, lineMat);
    }
    treeGroup.add(connect(root.position, l1a.position));
    treeGroup.add(connect(root.position, l1b.position));
    treeGroup.add(connect(l1a.position, l2a.position));
    treeGroup.add(connect(l1a.position, l2b.position));
    treeGroup.add(connect(l1b.position, l2c.position));
    treeGroup.add(connect(l1b.position, l2d.position));

    scene.add(treeGroup);

    // Data flowing down
    const particleGeo = new THREE.SphereGeometry(0.2, 8, 8);
    const particleMat = new THREE.MeshBasicMaterial({ color: 0xffff00 });
    const particles = [];

    function spawnParticle() {
        const p = new THREE.Mesh(particleGeo, particleMat);
        p.position.copy(root.position);
        p.userData = { target: l1a.position.clone(), stage: 1 };
        if (Math.random() > 0.5) p.userData.target = l1b.position.clone();
        scene.add(p);
        particles.push(p);
    }

    function animate() {
        requestAnimationFrame(animate);

        if (Math.random() < 0.05) spawnParticle();

        for (let i = particles.length - 1; i >= 0; i--) {
            const p = particles[i];
            const dir = new THREE.Vector3().subVectors(p.userData.target, p.position).normalize();
            p.position.add(dir.multiplyScalar(0.1));

            if (p.position.distanceTo(p.userData.target) < 0.1) {
                if (p.userData.stage === 1) {
                    p.userData.stage = 2;
                    // Pick next target
                    if (p.userData.target.x < 0) { // Left branch
                        p.userData.target = (Math.random() > 0.5) ? l2a.position.clone() : l2b.position.clone();
                    } else { // Right branch
                        p.userData.target = (Math.random() > 0.5) ? l2c.position.clone() : l2d.position.clone();
                    }
                } else {
                    scene.remove(p);
                    particles.splice(i, 1);
                }
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
