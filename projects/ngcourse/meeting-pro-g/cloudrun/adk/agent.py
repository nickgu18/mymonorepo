from typing import AsyncGenerator
from google.adk.agents import BaseAgent, LlmAgent, InvocationContext
from google.adk.events import Event
from google.adk.utils.context_utils import Aclosing
from . import tools

# 1. Triage Agent
triage_agent = LlmAgent(
    name="triage_agent",
    model="gemini-2.5-flash",
    instruction="""
    Task: Analyze the conversation context and classify the User's Latest Intent.
    
    Success Criteria:
    - Accurately identify if the user wants to schedule, reschedule, confirm, or cancel.
    - Identify spam or irrelevant messages.
    
    Output ONE of these intents:
    - schedule_meeting: User wants to book a new meeting.
    - reschedule_meeting: User wants to change an existing meeting.
    - confirm_meeting: User is confirming a proposed time.
    - cancel_meeting: User wants to cancel.
    - spam: Irrelevant or automated noise.
    - unknown: Ambiguous or none of the above.
    """
)

# 2. Scheduling Agent
scheduling_agent = LlmAgent(
    name="scheduling_agent",
    model="gemini-2.5-flash",
    instruction="""
    Task: Check availability or book slots using Calendar tools based on the intent.
    
    Context: token='0' and thread_id='0' are available.
    
    Tools:
    - fetch_calendar_events: Check busy times.
    - create_calendar_event: Book a slot (Draft/Tentative).
    
    Logic:
    - If intent is 'schedule_meeting' or 'reschedule_meeting':
      1. Check calendar for the relevant date range.
      2. Suggest 3 free slots.
    - If intent is 'confirm_meeting':
      1. Book the event.
    - If intent is 'cancel_meeting':
      1. (Optional) Try to find and cancel the event (Not implemented in MVP tools yet, just acknowledge).
      
    Success Criteria:
    - Return a actionable summary (e.g., list of slots, confirmation of booking) for the Author Agent.
    """,
    tools=[
        tools.fetch_calendar_events,
        tools.create_calendar_event
    ]
)

# 3. Author Agent
author_agent = LlmAgent(
    name="author_agent",
    model="gemini-2.5-flash",
    instruction="""
    Task: Draft a polite, professional reply based on the Scheduler's output.
    
    Tools:
    - create_draft_reply: Use this to save the draft.
    
    Logic:
    - Take the summary from the Scheduling Agent.
    - Draft a response in the user's voice (Professional, Concise).
    - If needed (e.g., 'unknown' intent), ask for clarification.
    - Use `create_draft_reply` to save it to Gmail.

    Success Criteria:
    - A draft email is created in Gmail.
    - The tone is professional and appropriate for the intent.
    """,
    tools=[
        tools.create_draft_reply
    ]
)

# 4. Custom Root Agent
class MeetingOrchestrator(BaseAgent):
    """Custom orchestrator to allow conditional verification."""
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # 1. Triage
        triage_output = ""
        # Use Aclosing to safely handle generator context
        async with Aclosing(triage_agent.run_async(ctx)) as agen:
            async for event in agen:
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            triage_output += part.text
                yield event
        
        # 2. Analyze Intent from Triage Output
        intent = triage_output.lower().strip()
        scheduling_needed = any(k in intent for k in ["schedule", "reschedule", "confirm"])
        spam = "spam" in intent
        
        if spam:
            return

        # 3. Conditional Scheduling
        if scheduling_needed:
            async with Aclosing(scheduling_agent.run_async(ctx)) as agen:
                async for event in agen:
                    yield event
        
        # 4. Authoring (Always run unless spam, even for unknown/help)
        async with Aclosing(author_agent.run_async(ctx)) as agen:
            async for event in agen:
                yield event

root_agent = MeetingOrchestrator(
    name="meeting_scheduler_root",
    sub_agents=[triage_agent, scheduling_agent, author_agent]
)
