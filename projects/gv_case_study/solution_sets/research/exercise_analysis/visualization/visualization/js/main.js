// Main Orchestrator
import { initStage1 } from './stages/stage1.js';
import { initStage2 } from './stages/stage2.js';
import { initStage3 } from './stages/stage3.js';
import { initStage4 } from './stages/stage4.js';
import { initStage5 } from './stages/stage5.js';
import { initStage8 } from './stages/stage8.js';

document.addEventListener('DOMContentLoaded', () => {
    console.log("Initializing visualizations...");

    // Initialize each stage if the container exists
    if (document.getElementById('canvas-stage-1')) initStage1('canvas-stage-1');
    if (document.getElementById('canvas-stage-2')) initStage2('canvas-stage-2');
    if (document.getElementById('canvas-stage-3')) initStage3('canvas-stage-3');
    if (document.getElementById('canvas-stage-4')) initStage4('canvas-stage-4');
    if (document.getElementById('canvas-stage-5')) initStage5('canvas-stage-5');
    if (document.getElementById('canvas-stage-8')) initStage8('canvas-stage-8');
});
