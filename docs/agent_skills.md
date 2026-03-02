# Agent Skills

Agent Skills allow you to extend Gemini CLI with specialized expertise,
procedural workflows, and task-specific resources. Based on the
[Agent Skills](https://agentskills.io) open standard, a "skill" is a
self-contained directory that packages instructions and assets into a
discoverable capability.

## Overview

Unlike general context files ([`GEMINI.md`](/docs/cli/gemini-md)), which provide
persistent workspace-wide background, Skills represent **on-demand expertise**.
This allows Gemini to maintain a vast library of specialized capabilities—such
as security auditing, cloud deployments, or codebase migrations—without
cluttering the model's immediate context window.

Gemini autonomously decides when to employ a skill based on your request and the
skill's description. When a relevant skill is identified, the model "pulls in"
the full instructions and resources required to complete the task using the
`activate_skill` tool.

## Key Benefits

- **Shared Expertise:** Package complex workflows (like a specific team's PR
  review process) into a folder that anyone can use.
- **Repeatable Workflows:** Ensure complex multi-step tasks are performed
  consistently by providing a procedural framework.
- **Resource Bundling:** Include scripts, templates, or example data alongside
  instructions so the agent has everything it needs.
- **Progressive Disclosure:** Only skill metadata (name and description) is
  loaded initially. Detailed instructions and resources are only disclosed when
  the model explicitly activates the skill, saving context tokens.

## Skill Discovery Tiers

Gemini CLI discovers skills from three primary locations:

1.  **Workspace Skills**: Located in `.gemini/skills/` or the `.agents/skills/`
    alias. Workspace skills are typically committed to version control and
    shared with the team.
2.  **User Skills**: Located in `~/.gemini/skills/` or the `~/.agents/skills/`
    alias. These are personal skills available across all your workspaces.
3.  **Extension Skills**: Skills bundled within installed
    [extensions](/docs/extensions).

**Precedence:** If multiple skills share the same name, higher-precedence
locations override lower ones: **Workspace > User > Extension**.

Within the same tier (user or workspace), the `.agents/skills/` alias takes
precedence over the `.gemini/skills/` directory. This generic alias provides an
intuitive path for managing agent-specific expertise that remains compatible
across different AI agent tools.

## Managing Skills

### In an Interactive Session

Use the `/skills` slash command to view and manage available expertise:

- `/skills list` (default): Shows all discovered skills and their status.
- `/skills link <path>`: Links agent skills from a local directory via symlink.
- `/skills disable <name>`: Prevents a specific skill from being used.
- `/skills enable <name>`: Re-enables a disabled skill.
- `/skills reload`: Refreshes the list of discovered skills from all tiers.

_Note: `/skills disable` and `/skills enable` default to the `user` scope. Use
`--scope workspace` to manage workspace-specific settings._

### From the Terminal

The `gemini skills` command provides management utilities:

```bash
# List all discovered skills
gemini skills list

# Link agent skills from a local directory via symlink
# Discovers skills (SKILL.md or */SKILL.md) and creates symlinks in ~/.gemini/skills
# (or ~/.agents/skills)
gemini skills link /path/to/my-skills-repo

# Link to the workspace scope (.gemini/skills or .agents/skills)
gemini skills link /path/to/my-skills-repo --scope workspace

# Install a skill from a Git repository, local directory, or zipped skill file (.skill)
# Uses the user scope by default (~/.gemini/skills or ~/.agents/skills)
gemini skills install https://github.com/user/repo.git
gemini skills install /path/to/local/skill
gemini skills install /path/to/local/my-expertise.skill

# Install a specific skill from a monorepo or subdirectory using --path
gemini skills install https://github.com/my-org/my-skills.git --path skills/frontend-design

# Install to the workspace scope (.gemini/skills or .agents/skills)
gemini skills install /path/to/skill --scope workspace

# Uninstall a skill by name
gemini skills uninstall my-expertise --scope workspace

# Enable a skill (globally)
gemini skills enable my-expertise

# Disable a skill. Can use --scope to specify workspace or user (defaults to workspace)
gemini skills disable my-expertise --scope workspace
```

## How it Works

1.  **Discovery**: At the start of a session, Gemini CLI scans the discovery
    tiers and injects the name and description of all enabled skills into the
    system prompt.
2.  **Activation**: When Gemini identifies a task matching a skill's
    description, it calls the `activate_skill` tool.
3.  **Consent**: You will see a confirmation prompt in the UI detailing the
    skill's name, purpose, and the directory path it will gain access to.
4.  **Injection**: Upon your approval:
    - The `SKILL.md` body and folder structure is added to the conversation
      history.
    - The skill's directory is added to the agent's allowed file paths, granting
      it permission to read any bundled assets.
5.  **Execution**: The model proceeds with the specialized expertise active. It
    is instructed to prioritize the skill's procedural guidance within reason.

### Skill activation

Once a skill is activated (typically by Gemini identifying a task that matches
the skill's description and your approval), its specialized instructions and
resources are loaded into the agent's context. A skill remains active and its
guidance is prioritized for the duration of the session.

## Creating your own skills

To create your own skills, see the [Create Agent Skills](/docs/cli/creating-skills)
guide.

# Creating Agent Skills

This guide provides an overview of how to create your own Agent Skills to extend
the capabilities of Gemini CLI.

## Getting started: The `skill-creator` skill

The recommended way to create a new skill is to use the built-in `skill-creator`
skill. To use it, ask Gemini CLI to create a new skill for you.

**Example prompt:**

> "create a new skill called 'code-reviewer'"

Gemini CLI will then use the `skill-creator` to generate the skill:

1.  Generate a new directory for your skill (e.g., `my-new-skill/`).
2.  Create a `SKILL.md` file with the necessary YAML frontmatter (`name` and
    `description`).
3.  Create the standard resource directories: `scripts/`, `references/`, and
    `assets/`.

## Manual skill creation

If you prefer to create skills manually:

1.  **Create a directory** for your skill (e.g., `my-new-skill/`).
2.  **Create a `SKILL.md` file** inside the new directory.

To add additional resources that support the skill, refer to the skill
structure.

## Skill structure

A skill is a directory containing a `SKILL.md` file at its root.

### Folder structure

While a `SKILL.md` file is the only required component, we recommend the
following structure for organizing your skill's resources:

```text
my-skill/
├── SKILL.md       (Required) Instructions and metadata
├── scripts/       (Optional) Executable scripts
├── references/    (Optional) Static documentation
└── assets/        (Optional) Templates and other resources
```

### `SKILL.md` file

The `SKILL.md` file is the core of your skill. This file uses YAML frontmatter
for metadata and Markdown for instructions. For example:

```markdown
---
name: code-reviewer
description:
  Use this skill to review code. It supports both local changes and remote Pull
  Requests.
---

# Code Reviewer

This skill guides the agent in conducting thorough code reviews.

## Workflow

### 1. Determine Review Target

- **Remote PR**: If the user gives a PR number or URL, target that remote PR.
- **Local Changes**: If changes are local... ...
```

- **`name`**: A unique identifier for the skill. This should match the directory
  name.
- **`description`**: A description of what the skill does and when Gemini should
  use it.
- **Body**: The Markdown body of the file contains the instructions that guide
  the agent's behavior when the skill is active.