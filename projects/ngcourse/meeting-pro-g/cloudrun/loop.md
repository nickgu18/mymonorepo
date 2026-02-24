In the Google Agent Development Kit (ADK), the  is designed to run all its sub-agents in a fixed, strict order. It does not have a built-in "break" or short-circuit mechanism based on an if condition in the same way a standard programming loop does. [1, 2, 3]  
To achieve conditional execution flow and break a sequence, the recommended approaches involve using a custom agent or leveraging the  with an escalation mechanism. [1]  
Recommended Approaches for Conditional Breaks 
Here are the primary ways to implement conditional breaks in an ADK workflow: 
1. Create a Custom Agent (Recommended for complex logic) The most flexible and robust method is to create a custom agent by inheriting from  and manually implementing the execution logic within the  method. This gives you explicit programmatic control over when to call the next sub-agent. 

• Logic: 

	• Manually call each sub-agent's  method in sequence. 
	• After each sub-agent runs, check the session state, the last event, or the agent's output for your specified condition. 
	• If the condition is met, use a  statement in your custom agent's method to stop further execution. 

• Example (Python conceptual): [1, 5, 6, 7, 8]  

2. Use a  with  While designed for looping, the  offers a direct mechanism for early termination via "escalation" which can be repurposed for a conditional break within a single iteration. 

• Logic: 

	• Wrap your sequence of sub-agents within a . 
	• Include a "condition evaluator" sub-agent. 
	• This evaluator agent, when its condition is met, calls  (if using a tool) or generates an  with . 
	• The  runtime interprets this signal as an immediate break condition and stops the current iteration (or the entire loop if configured). 

• Considerations: Using  works to exit a , but note that a user in a GitHub discussion mentioned it might not stop a parent  that the  is nested within, and might have unexpected side effects in specific ADK versions. The most reliable method remains the custom agent approach. [9, 10, 11, 12, 13]  

Summary of Differences 

| Feature [1, 2, 9, 14, 15] |  |  | with Escalate  |
| --- | --- | --- | --- |
| Execution | Runs all sub-agents deterministically | Programmatically controlled | Iterative, but can stop early  |
| Break Condition | No built-in mechanism | statement in custom code | via event/tool  |
| Flexibility | Rigid order | Highly flexible | Designed for iterations/exit criteria  |

AI responses may include mistakes.

[1] https://github.com/google/adk-python/discussions/2290
[2] https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/
[3] https://github.com/google/adk-python/discussions/2350
[4] https://google.github.io/adk-docs/agents/custom-agents/
[5] https://google.github.io/adk-docs/agents/workflow-agents/loop-agents/
[6] https://github.com/google/adk-python/discussions/2290
[7] https://ai.plainenglish.io/agents-md-a-comprehensive-guide-to-agentic-ai-collaboration-571df0e78ccc
[8] https://documentation.sas.com/doc/en/edmbldrug/latest/n055qpigyrj01hn1r56e221prj27.htm
[9] https://glaforge.dev/posts/2025/07/28/mastering-agentic-workflows-with-adk-loop-agents/
[10] https://google.github.io/adk-docs/agents/multi-agents/
[11] https://google.github.io/adk-docs/agents/workflow-agents/loop-agents/
[12] https://github.com/google/adk-python/issues/1376
[13] https://www.scaler.com/topics/break-in-r/
[14] https://google.github.io/adk-docs/agents/workflow-agents/loop-agents/
[15] https://medium.com/@montasserdev20/php-break-statement-the-complete-guide-with-examples-92bd0b779a4d

