### Instruction

Review the provided @task and the provided code @source, write rootcause to @analysis section, add your @fix_plan and all relevant files under @files.

### source

/usr/local/google/home/guyu/Desktop/gcli/tools/ngtools

### Task

ngtools project during set up should prompt user to enter the root of the source code, which is then stored under .ngtools.yaml file under project.
For example

- folder
    - ngtools
        - .ngtools.yaml
        - issues_1
            - issues_1.md
            - followup_1.md
            - followup_2.md

.ngtools.yaml should store

```
source: "absolute/path/to/source"
procedural_instructions:
    test:
        unit_tests:
            cmd: cmd to run
            override: "run this only when xxx"
        integration_tests:
            cmd to run
```

Further, the ngtools should create issues / projects inside the directory from which it is invoked.

### analysis

The `ngtools.sh` script is the main entry point for the ngtools project. The script is currently designed to create all projects and issues within a `docs` directory that is located in the same directory as the script itself. This means that the tool is not sensitive to the directory from which it is invoked.

The script also lacks a configuration mechanism. There is no way to specify a source code root or define procedural instructions for tests, as requested in the task.

### fix_plan

1.  **Implement a setup process in `ngtools.sh`:**
    *   On startup, the script will check for a `.ngtools.yaml` file in the current working directory.
    *   If the file does not exist, the script will prompt the user to enter the absolute path to the source code root.
    *   The script will then create a `.ngtools.yaml` file in the current directory with the provided source path and a default structure for procedural instructions.

2.  **Modify project and issue creation:**
    *   The script will be modified to use the current working directory as the base for creating new projects and issues. The hardcoded paths pointing to the script's directory will be replaced with paths relative to the current directory.

### files

- tools/ngtools/ngtools.sh
