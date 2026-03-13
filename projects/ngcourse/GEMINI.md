# Instructions

During your interaction with the user, if you find anything reusable in this project (e.g. version of a library, model name), especially about a fix to a mistake you made or a correction you received, you should take note in the `Lessons` section in this file so you will not make the same mistake again. 

## 10 commandments

1.  **Thou shalt lint thy code:** Always run a linter (like `pylint`) on your code to catch potential bugs and style issues. Suppress warnings only when absolutely necessary and with a clear explanation.
2.  **Thou shalt import with clarity:** Use `import module` for packages and modules. Use `from module import name` for specific items, and `from module import name as alias` only when necessary to avoid conflicts or for brevity with standard abbreviations. Avoid relative imports.
3.  **Thou shalt handle exceptions with care:** Use built-in exceptions when appropriate. Do not use `assert` for critical logic. Avoid broad `except:` clauses, and minimize code within `try` blocks. Use `finally` for cleanup.
4.  **Thou shalt avoid mutable global state:** Global mutable variables can lead to unpredictable behavior. If necessary, use them sparingly and document them clearly.
5.  **Thou shalt keep lines concise:** Adhere to the 80-character line limit. Use Python's implicit line joining within parentheses, brackets, and braces for longer expressions.
6.  **Thou shalt indent with 2 spaces:** Use 2 spaces for indentation, and never tabs. Align wrapped code logically, either vertically or with a hanging indent.
7.  **Thou shalt document thy code:** Write clear docstrings for modules, classes, functions, and methods. Use `Args:`, `Returns:`, and `Raises:` sections as needed. Add comments only for complex or non-obvious code.
8.  **Thou shalt name descriptively:** Use clear, descriptive names for all entities. Avoid single-character names (except for specific cases like loop counters) and abbreviations. Follow established naming conventions for modules, classes, functions, variables, and constants.
9.  **Thou shalt manage resources explicitly:** Always close files, sockets, and other stateful resources. Prefer the `with` statement for automatic resource management.
10. **Thou shalt embrace modern Python and type hints:** Use `from __future__ import` statements for modern syntax. Annotate your code with type hints and use a type checker like `pytype` to catch errors early.

## Working Memory Management

You should always begin your work by documenting your plan in the TODO.md file.

### Maintain TODO.md:

```markdown
## Current Task

- [ ] What we're doing RIGHT NOW
- [ ] Package/file we're working in

## Completed

- [x] What's actually done and tested
- [x] Tests passing

## Next Steps

- [ ] What comes next
- [ ] Which packages need updates
```

# Tools

Note all the tools are in python3. So in the case you need to do batch processing, you can always consult the python files and write your own script.

## Skills

Skills are located in the `/usr/local/google/home/guyu/Desktop/mymonorepo/ng-skills-bundle` directory. You can use them to perform specific tasks. To invoke a skill, use the following command:

```bash
/usr/local/google/home/guyu/Desktop/mymonorepo/ng-skills-bundle/<skill-name>/procedure.sh <arguments>
```

### Gemini API

You can use the `gemini-api` skill to interact with the Gemini API.

# Lessons

## User Specified Lessons

- You have a python venv in ./venv. Always use (activate) it when doing python development. First, to check whether 'uv' is available, use `which uv`. If that's the case, first activate the venv, and then use `uv pip install` to install packages. DO NOT USE pip.

## GEMINI learned

# Scratchpad