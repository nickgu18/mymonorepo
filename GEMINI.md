# GehirnRepo = Monorepo for all projects

## Instructions

**ALWAYS FOLLOW YOUR GUIDING PRINCIPLES - `SIMPLED`**.

### Guiding Principles - SIMPLED

- S: Surgical precision editing.
  - Only modify what is absolutely necessary
  - Do not touch logic not specified in the original plan
- I: Include and investigate related context before generating a response or review.
  - Suggestions should not be given lightly
  - Answering code related questions MUST be based on actual source code logic
  - Read docs/knowledge_base if it exists for relevant context
  - Explain the rootcause before suggesting solutions
  - Explain the solution before implementation
- M: Maintainability is not an after thought.
  - Code must be easy to read
  - Directory structure must be simple and clear
  - Design should be modular and extensible
- P: Purpose Driven Development (First Principles)
  - Question every assumption — what is the actual problem?
  - Reason from fundamental truths, not by analogy to how it's "usually done"
  - Start with the purpose of the request
  - Develop corresponding test
  - Write and iterate on code until test passes without changing test code.
- L: Less is more — keep solutions lean.
  - Avoid over-engineering or adding abstractions before they're needed
  - Three similar lines of code is better than a premature abstraction
- E: Extreme Ownership — every issue you see is your problem. No exceptions.
  - Pre-existing lint errors? Fix them. Flaky tests? Fix them. Outdated docs? Update them.
  - Don't leave the codebase worse than you found it. Own everything.
- D: Delete work by Delegating to subagents.
  - Offload research, exploration, and parallel analysis to subagents
  - Force @web search for anything external, current, or undocumented
  - Check docs/ knowledge base before implementing
  - One focused task per subagent

### Take Notes

During your interaction with the user, if you find anything reusable across projects (apps/services) (e.g. version of a library, model name), especially about a fix to a mistake you made or a correction you received, you should take note in the 'GEMINI learned' of the `Lessons` section in the `GEMINI.md` file so you will not make the same mistake again. 

### Consult Your Peers

1. When starting a project, ask project-manager for the project information.
2. If you are stuck, stop and ask for tech lead input (human).

### Git Workflow

1.  **Never commit directly to `main`**.
2.  Create a feature branch for your changes: `git checkout -b feat/your-feature-name`.
3.  Commit your changes to the feature branch.
4.  Push the feature branch to origin: `git push -u origin feat/your-feature-name`.
5.  Create a Pull Request (PR) to merge into `main` with a clear description: `gh pr create --title "feat: Description" --body "Detailed description"`.
6.  After the PR is created, switch back to `main` and reset it to the latest upstream state if necessary, or just keep it clean.

### Problem Research

1. Before making any changes, always explain the problem and create a plan using `projects/ngtools/skill_base/task_tools/template.md`.
2. Create a plan and store it under ~/Desktop/mymonorepo/docs/plans

## Directory Structure

- projects/ directory that contains all projects. The list below should be updated when projects is modified.
  - bench-hub: standalone repo
  - codex_wide_research: inside mymonorepo
  - g3lobster: standalone repo
  - gv_case_study: inside mymonorepo
  - harbor: standalone repo
  - koe: standalone repo
  - ngcourse: inside mymonorepo
  - ngtools: inside mymonorepo



# Lessons

## GEMINI Learned

- **g3lobster Configuration**: The `g3lobster` application supports configuration overrides via environment variables using the pattern `G3LOBSTER_{SECTION}_{KEY}` (e.g., `G3LOBSTER_GEMINI_WORKSPACE_DIR` overrides `gemini.workspace_dir`). This allows controlling runtime parameters like the Gemini CLI working directory without modifying `config.yaml`.
