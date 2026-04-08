---
name: refresh-gcli-docs
description: Refresh the Gemini CLI documentation in docs/gcli by pulling the latest from the GitHub repo.
---

# Refresh Gemini CLI Docs

This skill refreshes the Gemini CLI documentation stored in `docs/gcli` by fetching the latest content from the official repository.

## Workflow

When activated, this skill will guide you to run the refresh script or perform the following steps:
1.  Clone the Gemini CLI repository to a temporary directory.
2.  Copy the contents of the `docs` directory to `docs/gcli` in this monorepo.
3.  Clean up the temporary directory.

## Resources

- Script: `scripts/refresh.sh`
