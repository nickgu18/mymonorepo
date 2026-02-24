#!/usr/bin/env node

const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');
const { exec } = require('child_process');
const manager = require('./core/project_manager');
const ui = require('./tui/ui');

const baseDir = __dirname;

// Ensure storage directories exist
manager.ensureStorage(baseDir);

yargs(hideBin(process.argv))
  .command('project <action> [name]', 'Manage projects', (yargs) => {
    yargs
      .positional('action', {
        describe: 'Action to perform on the project',
        choices: ['create', 'list', 'delete', 'activate'],
      })
      .positional('name', {
        describe: 'Name of the project',
        type: 'string',
      })
      .option('source-path', {
        alias: 's',
        describe: 'Absolute path to the project source code directory',
        type: 'string',
      });
  }, (argv) => {
    handleProjectCommand(argv);
  })
  .command('task <action> [arg1] [arg2]', 'Manage tasks', (yargs) => {
    yargs
      .positional('action', {
        describe: 'Action to perform on the task',
        choices: ['create', 'list', 'plan', 'follow_up', 'execute'],
      })
      .positional('arg1', {
        describe: 'Task name or description',
        type: 'string',
      })
      .positional('arg2', {
        describe: 'Follow-up description',
        type: 'string',
      });
  }, (argv) => {
    handleTaskCommand(argv);
  })
  .command('ui', 'Show interactive UI', () => {}, (argv) => {
    ui.showUi();
  })
  .demandCommand(1, 'You need at least one command before moving on')
  .help()
  .argv;

function handleProjectCommand(argv) {
  const { action, name, sourcePath } = argv;

  switch (action) {
    case 'create':
      if (!name) {
        console.error('Project name is required for create action.');
        return;
      }
      const createResult = manager.createProject(name, sourcePath, baseDir);
      console.log(createResult.message);
      break;
    case 'list':
      const projects = manager.getProjectList();
      console.log('Projects:');
      projects.forEach(p => console.log(` - ${p}`));
      break;
    case 'delete':
      if (!name) {
        console.error('Project name is required for delete action.');
        return;
      }
      const deleteResult = manager.deleteProject(name);
      console.log(deleteResult.message);
      break;
    case 'activate':
      if (!name) {
        console.error('Project name is required for activate action.');
        return;
      }
      const activateResult = manager.activateProject(name);
      console.log(activateResult.message);
      break;
  }
}

function handleTaskCommand(argv) {
    const { action, arg1, arg2 } = argv;

    switch (action) {
        case 'create':
            if (!arg1) {
                console.error('Task description is required.');
                return;
            }
            const createResult = manager.createTask(arg1, baseDir);
            console.log(createResult.message);
            break;
        case 'list':
            const listResult = manager.listTasks();
            if (!listResult.success) {
                console.error(listResult.message);
                return;
            }
            console.log(listResult.message);
            if (listResult.tasks) {
                listResult.tasks.forEach(t => console.log(` - ${t}`));
            }
            break;
        case 'plan':
            if (!arg1) {
                console.error('Task name is required.');
                return;
            }
            const planResult = manager.planTask(arg1);
            if (!planResult.success) {
                console.error(planResult.message);
                return;
            }
            console.log(planResult.message);
            exec(planResult.command, (error, stdout, stderr) => {
                if (error) {
                    console.error(`exec error: ${error}`);
                    return;
                }
                console.log(`stdout: ${stdout}`);
                console.error(`stderr: ${stderr}`);
            });
            break;
        case 'follow_up':
            if (!arg1 || !arg2) {
                console.error('Task name and follow-up description are required.');
                return;
            }
            const followUpResult = manager.followUpTask(arg1, arg2, baseDir);
            console.log(followUpResult.message);
            break;
        case 'execute':
            if (!arg1) {
                console.error('Task name is required.');
                return;
            }
            const executeResult = manager.executeTask(arg1);
            if (!executeResult.success) {
                console.error(executeResult.message);
                return;
            }
            console.log(executeResult.message);
            exec(executeResult.command, (error, stdout, stderr) => {
                if (error) {
                    console.error(`exec error: ${error}`);
                    return;
                }
                console.log(`stdout: ${stdout}`);
                console.error(`stderr: ${stderr}`);
            });
            break;
    }
}

