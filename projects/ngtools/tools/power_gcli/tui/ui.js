
const blessed = require('blessed');
const manager = require('../core/project_manager');

function showUi() {
    const screen = blessed.screen({
        smartCSR: true,
        title: 'Power GCLI'
    });

    const projectList = blessed.list({
        parent: screen,
        top: 0,
        left: 0,
        width: '50%',
        height: '100%',
        items: manager.getProjectList(),
        keys: true,
        vi: true,
        style: {
            selected: {
                bg: 'blue'
            }
        },
        border: {
            type: 'line'
        },
        label: 'Projects'
    });

    const taskList = blessed.list({
        parent: screen,
        top: 0,
        right: 0,
        width: '50%',
        height: '100%',
        keys: true,
        vi: true,
        style: {
            selected: {
                bg: 'blue'
            }
        },
        border: {
            type: 'line'
        },
        label: 'Tasks'
    });

    projectList.on('select', (item) => {
        const projectName = item.getText();
        manager.activateProject(projectName);
        const tasks = manager.listTasks();
        if (tasks.success) {
            taskList.setItems(tasks.tasks);
        } else {
            taskList.setItems([]);
        }
        screen.render();
    });

    screen.key(['escape', 'q', 'C-c'], () => {
        return process.exit(0);
    });

    projectList.focus();
    screen.render();
}

module.exports = { showUi };
