Create a node tool, 'power-gcli' that I can use in the following way:

Overall workflow
1. Project
    - create
    - list
    - delete
    - activate
2. Task
    - create
    - list
    - plan
    - follow_up
    - execute

1. project
npx power-gcli project create $project_name
npx power-gcli project list
npx power-gcli project delete $project_name

2. task
npx power-gcli task create "task description"
> This command creates a task and fills in the task section of template `tools/power_gcli/template.md`
> the file name is first 10 letters of the task

npx power-gcli task plan $task_name
> this sends the task to gemini cli with the prompt "Execute @task_name.md, no code change"

npx power-gcli task list
> lists all tasks

npx power-gcli task $task_name follow_up "follow up"
> creates a new task with follow up, only difference is it will add the content of selected task to the follow up as context

npx power-gcli task execute $task_name
> executes the task with the prompt "implement the $task_name.md"
> will throw error if fix_plan, related_files, analysis is empty