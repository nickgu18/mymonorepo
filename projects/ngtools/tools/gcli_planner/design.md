The idea is to create a gui based interface for gemini cli, where user can interact with gemini cli to perform planning.

See `agent-prototypes/agent_prototypes/utils` on how gemini cli is invoked.

Plan mode gives the model new tools to create and update plans, as well as an interactive editor to modify plans inline. Most new features at gplanner now begin with Agent writing a plan. We’ve seen this significantly improve the code generated.

When you prompt Agent to create a plan, gplanner researches your codebase to find relevant files, review docs, and ask clarifying questions. When you’re happy with the plan, it creates a Markdown file with file paths and code references. You can edit the plan directly, including adding or removing to-dos.

How to use Plan Mode
Start planning by pressing Shift + Tab in the agent input.
Answer clarifying questions on your requirements for the best output quality.
Review or edit the detailed plan, then build directly from your plan when ready.
Optionally, save the plan as a Markdown file in your repository for future reference.
gplanner will also suggest plan mode automatically when you describe complex tasks.