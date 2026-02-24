# Power GCLI

`power-gcli` is a command-line and terminal-based tool designed to manage projects and tasks for the Gemini CLI, helping to organize and streamline development workflows.

## Installation

1.  Navigate to the tool's directory:
    ```bash
    cd /usr/local/google/home/guyu/Desktop/gcli/tools/power_gcli
    ```
2.  Install the package globally:
    ```bash
    npm install -g .
    ```

## Configuration

The tool stores all project and task data in a configuration directory located in your home folder: `~/.power-gcli`.

## Usage

### 1. Project Management

Projects are the top-level containers for your tasks.

| Command | Description |
| :--- | :--- |
| `power-gcli project create <name>` | Creates a new project. |
| `power-gcli project create <name> -s <path>` | Creates a project and associates it with a source code path. |
| `power-gcli project list` | Lists all available projects. |
| `power-gcli project activate <name>` | Sets the specified project as active. This also sets the `POWER_GCLI_SOURCE_PATH` environment variable for the active project's source code. |
| `power-gcli project delete <name>` | Deletes a project and all its tasks. |

**Example with Source Path:**
```bash
power-gcli project create my-app -s /path/to/my/source/code
power-gcli project activate my-app
```

### 2. Task Management

Tasks are markdown files that follow a specific template for Gemini CLI execution.

| Command | Description |
| :--- | :--- |
| `power-gcli task create "<description>"` | Creates a new task file in the active project's task directory. |
| `power-gcli task list` | Lists all tasks in the active project. |
| `power-gcli task plan <task_name.md>` | Executes the Gemini CLI to generate a plan for the task. |
| `power-gcli task execute <task_name.md>` | Executes the Gemini CLI to implement the task, using the `fix_plan`, `files`, and `analysis` sections from the task file. |
| `power-gcli task follow_up <original_task.md> "<follow-up description>"` | Creates a new task that includes the content of the original task as context. |

### 3. Terminal User Interface (TUI)

Launch the interactive TUI to manage projects and tasks visually.

| Command | Description |
| :--- | :--- |
| `power-gcli ui` | Launches the TUI. Use arrow keys to navigate and **Enter** to activate a project. Press **q** or **Ctrl+C** to exit. |
```bash
power-gcli ui
```