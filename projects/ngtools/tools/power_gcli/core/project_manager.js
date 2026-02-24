
const fs = require('fs');
const path = require('path');

const storagePath = path.join(__dirname, '..', '.power-gcli');
const projectsPath = path.join(storagePath, 'projects');
const metadataPath = path.join(storagePath, 'metadata.json');

function ensureStorage() {
    if (!fs.existsSync(storagePath)) {
        fs.mkdirSync(storagePath);
    }
    if (!fs.existsSync(projectsPath)) {
        fs.mkdirSync(projectsPath);
    }
    if (!fs.existsSync(metadataPath)) {
        fs.writeFileSync(metadataPath, JSON.stringify({ activeProject: null, projects: {} }));
    }
}

function getMetadata() {
    const metadata = fs.readFileSync(metadataPath);
    return JSON.parse(metadata);
}

function updateMetadata(newMetadata) {
    fs.writeFileSync(metadataPath, JSON.stringify(newMetadata, null, 2));
}

function createProject(name, sourcePath, baseDir) {
    const projectDir = path.join(projectsPath, name);
    if (fs.existsSync(projectDir)) {
        return { success: false, message: 'Project already exists.' };
    }
    fs.mkdirSync(projectDir);

    const metadata = getMetadata();
    metadata.projects[name] = {
        path: projectDir,
        sourcePath: sourcePath,
        tasks: {}
    };
    updateMetadata(metadata);

    return { success: true, message: `Project ${name} created.` };
}

function getProjectList() {
    const metadata = getMetadata();
    return Object.keys(metadata.projects);
}

function deleteProject(name) {
    const metadata = getMetadata();
    if (!metadata.projects[name]) {
        return { success: false, message: 'Project not found.' };
    }

    const projectDir = metadata.projects[name].path;
    fs.rmSync(projectDir, { recursive: true, force: true });

    delete metadata.projects[name];
    if (metadata.activeProject === name) {
        metadata.activeProject = null;
    }
    updateMetadata(metadata);

    return { success: true, message: `Project ${name} deleted.` };
}

function activateProject(name) {
    const metadata = getMetadata();
    if (!metadata.projects[name]) {
        return { success: false, message: 'Project not found.' };
    }
    metadata.activeProject = name;
    updateMetadata(metadata);
    return { success: true, message: `Project ${name} activated.` };
}

function getActiveProject() {
    const metadata = getMetadata();
    return metadata.activeProject;
}

function createTask(description, baseDir) {
    const activeProject = getActiveProject();
    if (!activeProject) {
        return { success: false, message: 'No active project.' };
    }

    const metadata = getMetadata();
    const project = metadata.projects[activeProject];
    const taskName = `task_${Object.keys(project.tasks).length + 1}`;
    const taskDir = path.join(project.path, taskName);
    fs.mkdirSync(taskDir);

    project.tasks[taskName] = {
        description: description,
        status: 'pending',
        plan: '',
        follow_up: ''
    };
    updateMetadata(metadata);

    return { success: true, message: `Task ${taskName} created in project ${activeProject}.` };
}

function listTasks() {
    const activeProject = getActiveProject();
    if (!activeProject) {
        return { success: false, message: 'No active project.' };
    }

    const metadata = getMetadata();
    const project = metadata.projects[activeProject];
    const taskNames = Object.keys(project.tasks);

    if (taskNames.length === 0) {
        return { success: true, message: 'No tasks in the active project.', tasks: [] };
    }

    return { success: true, message: 'Tasks:', tasks: taskNames };
}

function planTask(taskName) {
    const activeProject = getActiveProject();
    if (!activeProject) {
        return { success: false, message: 'No active project.' };
    }

    const metadata = getMetadata();
    const project = metadata.projects[activeProject];
    if (!project.tasks[taskName]) {
        return { success: false, message: 'Task not found.' };
    }

    const task = project.tasks[taskName];
    const editor = process.env.EDITOR || 'vim';
    const planFilePath = path.join(project.path, taskName, 'plan.md');
    fs.writeFileSync(planFilePath, task.plan);

    return { success: true, message: `Planning task ${taskName}. Please edit the plan file.`, command: `${editor} ${planFilePath}` };
}

function followUpTask(taskName, followUp, baseDir) {
    const activeProject = getActiveProject();
    if (!activeProject) {
        return { success: false, message: 'No active project.' };
    }

    const metadata = getMetadata();
    const project = metadata.projects[activeProject];
    if (!project.tasks[taskName]) {
        return { success: false, message: 'Task not found.' };
    }

    project.tasks[taskName].follow_up = followUp;
    updateMetadata(metadata);

    return { success: true, message: `Follow-up for task ${taskName} recorded.` };
}

function executeTask(taskName) {
    const activeProject = getActiveProject();
    if (!activeProject) {
        return { success: false, message: 'No active project.' };
    }

    const metadata = getMetadata();
    const project = metadata.projects[activeProject];
    if (!project.tasks[taskName]) {
        return { success: false, message: 'Task not found.' };
    }

    const task = project.tasks[taskName];
    const scriptPath = path.join(project.path, taskName, 'execute.sh');
    fs.writeFileSync(scriptPath, task.plan); // Assuming the plan is an executable script for now

    return { success: true, message: `Executing task ${taskName}.`, command: `bash ${scriptPath}` };
}


module.exports = {
    ensureStorage,
    createProject,
    getProjectList,
    deleteProject,
    activateProject,
    getActiveProject,
    createTask,
    listTasks,
    planTask,
    followUpTask,
    executeTask
};
