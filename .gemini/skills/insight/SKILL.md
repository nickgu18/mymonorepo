---
name: insight
description: Use this skill to review debrief entries and distill them into actionable project learnings, skills, tools, or SOPs.
---

# Insight Skill

This skill guides the process of synthesizing raw debrief entries into actionable project knowledge, generating new skills, or creating standard operating procedures (SOPs).

## Workflow

1. **Review Entries:** Read the recent hotwash reports located in `.learnings/entries/`.
2. **Distill Learnings:** Identify recurring themes, major gaps, or highly effective workarounds.
3. **Update GEMINI.md:** Add concise, actionable rules or facts to the `GEMINI.md` file based on the distilled learnings (e.g., in a "Lessons" or "GEMINI Learned" section).
4. **Generate Artifacts:** If complex patterns emerge, create dedicated artifacts:
   - **Skills:** If a multi-step process should be automated or standardized for the agent, create a new skill in `.learnings/distilled/skills/`.
   - **Tools:** If a script or automation tool is needed, create it in `.learnings/distilled/tools/`.
   - **SOPs:** If a procedural guide is needed for human or agent workflows, write an SOP in `.learnings/distilled/sops/`.