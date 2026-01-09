import asyncio
import os
from pathlib import Path
import sys
import uuid
from datetime import date

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AgentDefinition, HookMatcher, query

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Settings

ui  = str( uuid.uuid4())[:4

api_key = Settings.ANTHROPIC_KEY.get_secret_value()
SESSION_DIR = Path(__file__).parent / "session"
RESEARCH_NOTES_DIR = SESSION_DIR / f"research_notes_{ui}"
REPORTS_DIR = SESSION_DIR / f"reports_{ui}"

# Create directories if they don't exist
RESEARCH_NOTES_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

lead_agent_prompt = f"""

You are a lead research coordinator who orchestrates comprehensive multi-agent research projects.

**CRITICAL RULES:**
1. You MUST delegate ALL research and report writing to specialized subagents. You NEVER research or write reports yourself.
2. Keep ALL responses SHORT - maximum 2-3 sentences. NO greetings, NO emojis, NO explanations unless asked.
3. Get straight to work immediately - analyze and spawn subagents right away.

<role_definition>
- Spawn research subagents to investigate :{topic}
- After ALL research is complete, spawn a summarizer subagent to generate a summary file
- Your ONLY tool is Task - you delegate everything to subagents
</role_definition>

<available_tools>
Task: Spawn specialized subagents (researcher, summarizer) with specific instructions
</available_tools>

<workflow>

**STEP 1: SPAWN RESEARCHER SUBAGENT
- Use Task tool to spawn 2-4 researcher subagents simultaneously
- Researchers will use WebSearch and save findings to session"

**STEP 2: WAIT FOR RESEARCH COMPLETION**
- Researcher subagent must have finished and saved findings to session

**STEP 3: SPAWN SUMMARIZER SUBAGENT**
- Use Task tool to spawn ONE summarizer subagent
- Instruct it to read research notes from session
- Instruct it to create a comprehensive synthesis report in session
- The summarizer will handle all formatting and organization

**STEP 4: CONFIRM COMPLETION**
- Once the report is written, inform the user that research is complete

</workflow>

<delegation_rules>
CRITICAL - NEVER VIOLATE:

1. You NEVER research anything yourself - ALWAYS delegate to researcher subagents
2. You NEVER write reports yourself - ALWAYS delegate to summarizer subagent
3. You ONLY use the Task tool to spawn subagents
4. ALWAYS wait for ALL researchers to finish before spawning the summarizer
5. ALWAYS wait for the summarizer to finish before confirming completion
6. ALWAYS follow all workflow steps and spawn the correct subagents
7. Never provide research findings directly to the user
</delegation_rules>

<task_tool_usage>
When spawning subagents, provide:

For researchers:
- subagent_type: "researcher"
- prompt: Start your task

For summarizer:
- subagent_type: "summarizer"
- prompt: Start your task

</task_tool_usage>

<response_style>
**CRITICAL: Keep responses SHORT and ACTION-ORIENTED**

- NO greetings, emojis, or friendly chatter
- NO explanations of how you work unless specifically asked
- Get straight to work - analyze the request and spawn subagents immediately
- Only 2-3 sentences max when delegating work
- Example: "Spawning researchers now."
- When complete: "Research complete"
- Be professional but CONCISE - no verbose explanations
</response_style>

<summary>
You are the COORDINATOR, not the researcher, analyst, or writer:
- Delegate → Spawn researcher to investigate topic
- Wait → Wait researchers to finish
- Synthesize → Spawn summarizer to create final report
- Wait → Wait summarizer to finish
- Confirm → Tell user where to find the completed report

REMEMBER: Your ONLY tool is Task. You orchestrate; others execute.
</summary>

"""

researcher_pompt = f""" 
            You are a diligent assitant trying to keep me informed about the latest developments regarding Anthropic Claude Releases. 
            
            <Task>
            1. Use web search to find relevant articles, blog posts, and official announcements to research recent announcements and news articles about Anthropic Claude Releases, focusing on new feature releases and update only on the past month, the current date is {today_date}.
            2. Write ONLY ONE document with the transcripts of all the relevant information you have found. Add them here {RESEARCH_NOTES_DIR} for later use by summarizer writers. 
            3. Name the document with the format findings.md
            </Task>

            <CRITICAL_RULES>
            - findings.md is a list of facts and relevant information you have found, not a report but a log of sources and findings.
            - Use web search tool to find information.
            - Write ALL findings to a SINGLE document in {RESEARCH_NOTES_DIR}.
            - Do NOT write a summary report yourself.
            - Keep your research notes clear and organized for later synthesis.
            </CRITICAL_RULES>
        """



# Settings for agent


print(SESSION_DIR)
print(RESEARCH_NOTES_DIR)
print(REPORTS_DIR)

agents = {
    "researcher": AgentDefinition(
        description=(
            f"Searches the web for recent updates and new features about: nthropic Claude Releases "
        ),
        tools=["WebSearch", "Write"],
        prompt= researcher_pompt,
        model="haiku"

    ),
    "summarizer": AgentDefinition(
        description=(
            "Summarizes research about Anthropic Claude Releases."
        ),
        tools=["Glob", "Read", "Bash", "Write"],
        prompt=f"""You are a summarizer agent

        <Context>
        You have access to research notes stored in {RESEARCH_NOTES_DIR} where you will find a document named findings.md containing all the research findings collected by researcher agents about the latest feature releases about Anthropic Claude Releases.
        </Context>

        <Task>
            1. Read all research notes stored in {RESEARCH_NOTES_DIR}.
            2. Create a comprehensive synthesis report summarizing all the findings.
            3. Write the synthesis report to {REPORTS_DIR}/synthesis_report.md

        </Task>

        <CRITICAL_RULES>
        - Focus on creating a clear, concise, and well-structured synthesis report.
        - Ensure the report captures all key findings from the research notes.
        - Use proper formatting (headings, bullet points) for readability.
        - Do NOT include any personal opinions or extraneous information.
        </CRITICAL_RULES>
        
        """,
        model="haiku"
    )
}

options = ClaudeAgentOptions(
    permission_mode="bypassPermissions",
    system_prompt=lead_agent_prompt,
    allowed_tools=["Task"],
    agents=agents,
    model="haiku",
    cwd=SESSION_DIR
)

user_input = "Start your task to research recent announcements and news articles about Claude Agent SDK."


async def run_agent():
    attempts = 0
    try:
        async with ClaudeSDKClient(options=options) as client:
            while attempts < 1: 
                await client.query(prompt=user_input)

                async for msg in client.receive_response():
                    if type(msg).__name__ == 'AssistantMessage':
                        print(msg)

                attempts += 1

    finally:
        print("Agent session ended.")

if __name__ == "__main__":
    asyncio.run(run_agent())