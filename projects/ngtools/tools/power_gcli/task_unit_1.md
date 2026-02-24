#### unit_1

**task**: I need a gui for this project, where user can see the project and tasks visually. user can activate project by pressing buttons.

**plan**:
- [x] **Complete Core Logic Refactoring:**
    - [x] The `index.js` file has been partially refactored to import from `core/project_manager.js`, but the file and directory do not exist.
    - [x] Create a new directory `core`.
    - [x] Create a new file `core/project_manager.js`.
    - [x] Move all project and task management logic (currently in `handleProjectCommand` and `handleTaskCommand` in `index.js`) into exported functions within `core/project_manager.js`.
    - [x] These functions should handle the core logic and return results, leaving `index.js` responsible only for command-line parsing and I/O.
- [x] **TUI Implementation:**
    - [x] **Dependencies:** Add `blessed` to `package.json` dependencies.
    - [x] **Entry Point:** Create a new file `tui/ui.js` to contain the TUI logic.
    - [x] **CLI Integration:** Modify `index.js` to add a new top-level command: `power-gcli ui`, which will launch the TUI.
    - [x] **UI Structure:** In `tui/ui.js`, initialize a `blessed.screen`.
        - [x] Create a `blessed.list` to display projects.
        - [x] Create another `blessed.list` or `blessed.box` to display tasks for the selected project.
    - [x] **Interaction:**
        - [x] Use arrow keys for navigation.
        - [x] Bind a key (e.g., 'enter') to activate a project.
        - [x] Bind a key (e.g., 'q') to quit the TUI.