# Instructions

During your interaction with the user, if you find anything reusable in this project (e.g. version of a library, model name), especially about a fix to a mistake you made or a correction you received, you should take note in the 'GEMINI learned' section of the `Lessons` area in this file so you will not make the same mistake again.

Check @memory_bank to find relevant project information.

## Purpose-Driven Development
1. For each implementation, create basic tests that cover the core 'purpose' of the feature
2. Do not modify tests afterwards - keep iterating code until the test passes
3. Tests should focus on the essential functionality, not edge cases

We're building production-quality code together. Your role is to create maintainable, efficient solutions while catching potential issues early.

When you seem stuck or overly complex, I'll redirect you - my guidance helps you stay on track.

## memory_bank

**IMPORTANT**
- **Always** check `docs/agent_procedural_instructions/index.json` for relevant procedural memory before execution
- **Always** check `docs/project_memory` for relevant memory before execution

### Procedural Instructions
For user queries, check if there are relevant procedural instructions in `docs/agent_procedural_instructions` that apply to the situation.
If so, execute the identified instructions.
If not, skip.

At the end, evaluate if the steps taken need to be materialized into procedural instructions based on
1. Are the steps likely to be repeated more than 10 times?
   1. If not, stop.
2. Is there a generic sequence that can be codified?
   1. If not, stop.

If Yes to both, materialize the steps taken into procedural instructions in `docs/agent_procedural_instructions` following `docs/agent_procedural_instructions/template.md`.

### Project Knowledge

Document project specific properties in the `docs/project_memory` directory, following `docs/project_memory/template.md`.

# Lessons

## User Specified Lessons

- Check existing packages before creating new functionality
- Be RUTHLESS when reducing unused code

## GEMINI learned
