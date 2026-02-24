# Deep Analysis of Yage’s AI Perspective Evolution (2017–2025)

## 1. Research Notes
- **Document scope:** Systematically reviewed 66 Chinese-language posts tagged “AI” on Yage’s blog from 26 March 2017 to 17 October 2025, excluding English versions.
- **Methodology:** Followed the “Wide Research Multi-Instance Orchestration Prompt” workflow: the lead agent organized the index → 66 sub-agents (Codex + Tavily MCP) read each article and produced structured summaries → programmatic aggregation, quality checks, and manual synthesis of insights.
- **Analytical lens:** Tracked Yage’s evolving views on AI/Agentic AI, methodological frameworks, and organizational practices, with special focus on the systematic architecture formed in 2024–2025.

## 2. Timeline of Perspective Shifts
### 2.1 2017: Practice-Oriented Chatbots and Data Structuring
- The series “A WeChat bot that understands chat logs” (26–28 March 2017) argues that “the true value of chatbots is organizing conversations,” using cross-group forwarding, tag clouds, and meme recognition to showcase practical NLP/vision capabilities.
- Core message that year: keep AI close to concrete pain points (WeChat information overload) and convert unstructured chatter into knowledge assets through engineering.

### 2.2 2020–2022: Embedded Vision and IoT Experiments
- Pieces like “Building an intelligent camera on Raspberry Pi” (4 June 2020) extend into low-cost hardware, showing how convolutional models and microcomputers enable real-time monitoring.
- AI remains “tools + hardware,” emphasizing edge deployment and self-built systems—more maker-style experimentation than large-scale products.

### 2.3 2023: GPT-Era Cognitive Leap and Collaboration Methodology
- “Some thoughts on artificial intelligence” (4 Feb 2023) marks a systematic reflection on ChatGPT, focusing on intent comprehension, formatting stability, and prompt structure.
- “Efficient Prompt Engineering Guide” and “AI Comment Oriented Programming” (4 and 17 Mar 2023) lock in the method of “write comments → AI completion → human review,” reframing AI as a partner rather than a one-off query tool.
- Yage begins discussing knowledge management and documentation workflows, treating AI as an “augmented teammate.”

### 2.4 2024: Emergence of Agentic AI and Multi-Model Ecosystems
- Article volume spikes (21 posts in the year), covering multi-model platforms like Poe, Cursor, OpenWebUI, and real-time voice APIs; the central theme is “toolchains, workflows, and multi-agent coordination.”
- “Connecting AI to robots to influence the world” (1 Mar 2024) extends AI into the physical realm, proposing sandboxing, AST audits, and other engineering safeguards while noting that “humans are the real risk bottleneck.”
- Year-end “From sages to doers—paradigm shifts and architecture of Agentic AI” (13 Dec 2024) summarises a three-layer division of labor and implementation stack, upgrading “hands-on tinkering” into a full-fledged product/engineering framework.

### 2.5 2025: Systematic Deployment, Organizational Upgrade, and Wide Research
- In 2025 (35 posts), Yage jumps from personal efficiency to team/organizational perspectives:
  - **Life API series (24 Apr–3 May 2025):** Abstracts the real world into callable interfaces, stressing data pipelines, task decomposition, and AI initiative.
  - **AI management theme** (e.g., “When AI becomes your subordinate,” 1 Feb 2025; “Managing AI: the most important promotion in your career,” 5 Sep 2025) frames AI as interns, with situational leadership, process control, audits, and organizational design.
- **Wide Research framework** (“How to keep AI from slacking,” 17 Oct 2025) applies multi-agent division, context isolation, and Tavily MCP to solve long-chain “laziness,” enabling AI self-iteration and reliable execution.
- Conclusion: focus shifts from “how to use AI” to “how to orchestrate an AI team,” forming a reusable Agentic AI operating system.

## 3. Representative Works in Depth
1. **26 Mar 2017 – “A WeChat bot that understands chat logs”**: Casts the bot as a “group knowledge organizer,” introducing cross-group sync, tag clouds, and image recognition—an early focus on data structuring and multimodal fusion that seeds the later “information → structure → decision” workflow.
2. **17 Mar 2023 – “From object-oriented to comment-oriented: AI Comment Oriented Programming”**: Rebuilds development into “write robust comments → AI fills code → humans review,” institutionalizing “treat AI as a colleague” and pushing prompt engineering toward standard operating procedures.
3. **1 Mar 2024 – “Connecting AI to robot systems to influence the world”**: Shifts the lens to physical execution, detailing robotics + LLM safety (restricted Python, AST audits, allowlist sandboxes), and concluding “AI safety depends on human governance” while laying out actionable engineering rules.
4. **24 Apr 2025 – “When the real world becomes an API AI can call” (Life API I)**: Uses sensors and automation to convert household/life scenarios into APIs, highlighting task splitting, state synchronization, and human-AI co-learning for continuous real-world improvement.
5. **17 Oct 2025 – “How to keep AI from slacking: building systematic Wide Research capabilities for Codex”**: Summarizes a multi-agent divide-and-conquer playbook, diagnoses long-output failure, and prescribes “task sharding + context isolation + Tavily MCP + self-iterating prompts,” elevating Agentic AI into a replicable methodology.

## 4. Integrated Insights
- **Five engineering principles for Agentic AI:** Divide-and-conquer (Manus and Wide Research frameworks), role isolation (lead agent vs. sub-agents), layered tooling (Tavily for search, Codex for execution), self-diagnosis (prompt reflection and auto-rewriting), and result merging (structured templates plus QA).
- **Role transformation and organizational design:** From “AI as collaborator” in 2023 to “AI as team member/intern” in 2025, Yage highlights managerial duties—define objectives, provide safety rails, enforce reviews, and build knowledge repositories.
- **Ecosystem and platform strategy:** Multi-model platforms (Poe, Cursor, OpenWebUI), specialist models (DeepSeek r1, o3), and third-party tools (MCP, Tavily) assemble into an “AI tech stack,” emphasizing openness and plug-and-play capability.
- **Reliability and self-iteration:** Long-chain success relies on prompting AI to identify bottlenecks, rewrite prompts, and then letting the lead agent verify outcomes—a loop proven in Life API and Wide Research projects.
- **Future focus areas:** Real-world APIs, finance automation, and vertical deep dives (management, investing, product) show Yage steering AI toward business closure; key hurdles remain auditability and mature collaboration tooling.

## 5. Appendix: Complete AI Article Index (Chronological)
- 2017-03-26 | A WeChat Bot That Understands Chat Logs | Chatbots should leverage conversation history advantages. | https://yage.ai/wechat-bot.html
- 2017-03-27 | A WeChat Bot That Understands Chat Logs (Part 2) | Tag clouds and activity stats boost group engagement. | https://yage.ai/wechat-bot-2.html
- 2017-03-28 | A WeChat Bot That Understands Chat Logs (Part 3) | Using Caffe features quickly enables meme-battle bots. | https://yage.ai/wechat-bot-3.html
- 2020-06-04 | Intelligent Object-Detection Camera on Raspberry Pi | Raspberry Pi enables low-cost remote monitoring and detection. | https://yage.ai/raspberry-pi-object-detection.html
- 2023-02-04 | Some Thoughts on Artificial Intelligence | ChatGPT shines at intent, context, and stable formatting. | https://yage.ai/AI-thoughts.html
- 2023-03-31 | Boosting Writing Efficiency with GPT-4 and Whisper API | The bottleneck shifts to input speed rather than ideation. | https://yage.ai/GPT-API-usage-creation.html
- 2023-04-07 | Iterating the GPT Voice Dictation Tool | Evolves voice notes into an idea-centered workflow. | https://yage.ai/GPT-product-iteration.html
- 2023-04-09 | Terrified by GPT | GPT cuts natural-language editor build time by 100×. | https://yage.ai/GPT-scared-me.html
- 2023-04-16 | Third Iteration of the GPT Knowledge Management Tool | The tool must grow into a platform for multi-step flows. | https://yage.ai/GPT-shortcut.html
- 2023-04-17 | What Exactly Has Happened in AI Lately? | General foundation models are replacing task-specific solutions. | https://yage.ai/recent-AI-advancement.html
- 2024-01-23 | Squeezing AI Coding—How to Be the First Casualty of the Robot Revolution | AI as a multiplier slashes end-to-end development time. | https://yage.ai/ai-coding.html
- 2024-03-01 | Connecting AI to Robot Systems to Influence the World | Depending on humans as proxies is the bottleneck for AI impact. | https://yage.ai/ai-robot.html
- 2024-03-03 | The Profound Impact of AI on IT | AI makes scripting one-off tasks cost-effective. | https://yage.ai/ai-it-impact.html
- 2024-03-04 | Efficient Prompt Engineering Guide | Match task complexity to LLM strengths and weaknesses. | https://yage.ai/prompt-engineering-guide.html
- 2024-03-13 | When and How *Not* to Use AI | Using AI isn’t binary—choose the right intervention level. | https://yage.ai/ai-writing-limit.html
- 2024-03-17 | From Object-Oriented to Comment-Oriented—Managing AI to Assist Coding | In the AI era, high-quality comments become the core deliverable. | https://yage.ai/ai-comment-oriented-programming.html
- 2024-06-18 | Add Cloud Coverage Detection to an All-Day Camera in 5 Minutes | AI brings visible-light cloud detection within easy reach. | https://yage.ai/cloud-coverage-ai.html
- 2024-06-29 | Power Imbalance Between Huashan Sword and Qi Branches: A Multidimensional Study | Misaligned Huashan factions require multidisciplinary analysis. | https://yage.ai/ai-jinyong-paper.html
- 2024-08-04 | After Canceling ChatGPT, I Switched to Poe | Declining ChatGPT experience prompted a move to Poe. | https://yage.ai/poe.html
- 2024-08-06 | From a Historical Lens, Where Do Foundation Models Draw Their Power? | Foundation models hinge on few-shot adaptability. | https://yage.ai/foundation-models.html
- 2024-08-10 | Redefining AI Tools with the Builder’s Mindset | Builder’s Mindset turns users from consumers into creators. | https://yage.ai/builders-mindset.html
- 2024-09-02 | AssemblyAI Speech Recognition API Trial | OpenAI still leads in speech recognition speed. | https://yage.ai/assemblyai-speech-recognition-api-review.html
- 2024-10-27 | Zero-Latency AI-Assisted Writing with GPT Real-Time Voice API | Real-time voice APIs slash speech input delay. | https://yage.ai/realtime-gpt.html
- 2024-11-23 | Rediscovering the Joy of OpenWebUI | Local OpenWebUI rivals mainstream closed platforms. | https://yage.ai/open-webui.html
- 2024-12-12 | [Agentic AI] Devin vs. Agent Cursor | Devin’s global planning frames it as an intern-level agent. | https://yage.ai/devin-vs-agent-cursor.html
- 2024-12-13 | [Agentic AI] From Sage to Doer—Agentic AI Paradigm Shift and Architecture | Agentic AI pushes toward an “I tell you, you execute” paradigm. | https://yage.ai/agentic-ai.html
- 2024-12-17 | [Agentic AI] Turning $20 into $500: Modding Cursor into Devin in One Hour | Tweaking `.cursorrules` gives Cursor Devin-like planning. | https://yage.ai/cursor-to-devin.html
- 2024-12-19 | [Agentic AI] Using Cursor as a Universal AI Entry Point | Cursor makes “I say, you do” agent workflows smooth. | https://yage.ai/cursor-ai-entry.html
- 2024-12-23 | From Prompts to Fine-Tuning: Making AI More Like “Me” | Prompt tuning fails without a fine-grained personal corpus. | https://yage.ai/finetuning.html
- 2024-12-29 | From Fragmented Logs to Deep Reflection: AI’s 2024 Year-End Review | The AI year-end review reveals a multi-threaded life. | https://yage.ai/2024-year-end.html
- 2024-12-30 | Paying $200 for a Mentor: Why I Renewed o1 Pro | o1 Pro delivers insights beyond basic information lookup. | https://yage.ai/o1-pro.html
- 2025-01-02 | Agentic AI’s Chicken-Rib Crisis: How to Break the Deployment Deadlock | Agentic AI still needs heavy human cleanup in many scenarios. | https://yage.ai/agentic-ai-crisis.html
- 2025-01-14 | Reflections on the “From Users to Builders” AI Course | The course helps learners overcome AI stereotypes. | https://yage.ai/reflection-ai-course.html
- 2025-01-23 | Using Multi-Agent to Level Up Cursor’s Intelligence | Splitting planner and executor eases context overload. | https://yage.ai/multi-agent.html
- 2025-02-01 | When AI Becomes Your Direct Report: Three Management Traps for Technologists | Engineers must resist jumping in to debug so AI can grow. | https://yage.ai/ai-management.html
- 2025-02-08 | Notes on Using DeepSeek r1 | DeepSeek r1 still trails OpenAI o1 in overall intelligence. | https://yage.ai/deepseek-r1.html
- 2025-02-08 | From General Hospital to Smart Triage: Understanding DeepSeek’s Evolution | Hospital triage analogies explain DeepSeek v3’s architecture. | https://yage.ai/deepseek-hospital.html
- 2025-02-16 | Why the First Step in Learning Agentic AI Is Forgetting All Frameworks | Rigid frameworks impose risky worldviews at this stage. | https://yage.ai/why-forget-all-frameworks.html
- 2025-02-17 | From Data Mining to Cognitive Alchemy: Simulated Car-Buying with OpenAI Deep Research | Deep Research drastically compresses studies in unfamiliar domains. | https://yage.ai/deep-research-car-buying.html
- 2025-03-06 | Behind Manus’ Viral Moment: How Agentic AI Products Build Durable Advantage | Manus thrives by connecting research-to-output across the agentic chain. | https://yage.ai/manus.html
- 2025-03-09 | From Context Amnesia to Document-Driven Development | Agentic AI breaks down on 5K+ line projects due to context limits. | https://yage.ai/agentic-memory.html
- 2025-03-22 | The Lure of a Unified Tool Protocol: Business and Tech Chess Around MCP | MCP resolves adapter pain from fragmented LLM tool interfaces. | https://yage.ai/mcp.html
- 2025-03-27 | Toy or Productivity Tool? Four Steps to Commercial-Grade GPT Text-to-Image Diagrams | GPT text-image prompts greatly improve diagram controllability. | https://yage.ai/gpt-image.html
- 2025-04-15 | Letting AI Read Three Years of WeChat Logs to Write an Unexpected Book | Incomplete inputs keep AI from grasping fragmented organizational knowledge. | https://yage.ai/ai-book.html
- 2025-04-18 | Stop Asking Whether AI Replaces You—Ask Whether You Can Lead It | True agents need tool invocation plus autonomous decisions. | https://yage.ai/agentic-ai-202504.html
- 2025-04-20 | It’s Not That I Prefer o3—It Finally Started Acting on Its Own | o3’s initiative spike made it the main daily assistant. | https://yage.ai/o3.html
- 2025-04-20 | You Don’t Need Finance Expertise to Unpack Structured Notes with AI | AI quickly unpacks the composition logic of structured notes. | https://yage.ai/structured-notes.html
- 2025-04-24 | When the Real World Becomes an API AI Can Call | Low-end hardware plus top models already outperform human hearing. | https://yage.ai/life-api.html
- 2025-04-27 | From Real-World APIs to Cognitive Partners: My AI-Centric Experiment, Chapter 2 | Real-world data streams must map into intent and timing frames. | https://yage.ai/life-api-part2.html
- 2025-04-28 | AI Helps Me Reflect Thrice Daily: AI-Centric Experiment, Chapter 3 | Full-life transcription lowers friction for daily reflection. | https://yage.ai/life-api-part3.html
- 2025-05-03 | You’re Not Assigning Tasks—You’re Building a World Where AI Gets Smarter | Prompts construct the habitat where AI can grow sharper. | https://yage.ai/life-api-part4.html
- 2025-05-04 | After a Thousand Failures, It Picked the One You Saw | Instruction-following bias leaves today’s AI short on creativity. | https://yage.ai/ai-creativity.html
- 2025-05-08 | The Last Article Fell Apart—and It Wasn’t AI’s Fault | AI drafts flow smoothly yet lack the author’s depth and evidence. | https://yage.ai/life-api-part4-followup.html
- 2025-05-22 | AI, Hydroponics, Bubble Blowing, and Coffee | AI guidance shows hydroponics must watch KH/GH. | https://yage.ai/water-quality.html
- 2025-05-25 | Stronger Models, Same Experience: The Misalignment of AI Products | Models advanced to multimodal, long-horizon autonomy while UX lagged. | https://yage.ai/ai-products.html
- 2025-06-07 | Three Clumsy Ways to Distill Ten Million Words of *A Record of a Mortal’s Journey to Immortality* into a Knowledge Graph | Skip perfectionism—start with rough, full data as the base. | https://yage.ai/fanren.html
- 2025-06-08 | Age of Exploration: Stop Rowing Against AI | AI devalues “rowing” skills and rewrites job logic. | https://yage.ai/ai-paddler.html
- 2025-06-18 | Survival Guide for the Post-Intelligence Era | Commoditized intellect will reshape social order. | https://yage.ai/ai-society.html
- 2025-07-06 | My Cyber Immortality Quest: Expanding Life’s Boundaries with AI | AI power is capped by context bandwidth—reduce input friction. | https://yage.ai/ai-eternity.html
- 2025-07-12 | Kimi K2: A Deep Review Beyond the Chat Box | Kimi K2’s agentic core needs evaluation beyond chat UIs. | https://yage.ai/kimi-k2.html
- 2025-07-17 | When AI Gets Stuck in a Loop: A Collaboration Strategy Retrospective | Multi-agent work demands perspective shifts when blocked. | https://yage.ai/ai-unlearn.html
- 2025-08-07 | Beyond the Chat Box: A Quick Look at GPT-5 | GPT-5 feels like an API-oriented product upgrade. | https://yage.ai/gpt-5.html
- 2025-08-14 | When AI Doesn’t Work: How I Finally Automated Financial Closing | Reflects on a decade of manual closing pain points. | https://yage.ai/ai-finance.html
- 2025-09-05 | Managing AI: The Most Important Promotion of Your Career | Treat AI as interns to cultivate, not precision instruments. | https://yage.ai/ai-management-2.html
- 2025-10-07 | Why OpenAI Apps SDK Support Is a Crisis for MCP | Apps SDK’s `_meta` support undermines MCP orthodoxy. | https://yage.ai/mcp-revisited.html
- 2025-10-17 | How to Keep AI from Slacking: Building Systematic Wide Research for Codex | Wide divide-and-conquer architecture fixes long-output failures. | https://yage.ai/wide-research.html
