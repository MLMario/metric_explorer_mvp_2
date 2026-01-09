import asyncio
import os
from pathlib import Path
import sys
import uuid
from datetime import date
import shutil
import json
from string import Template

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AgentDefinition, HookMatcher, query

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Settings


#1 )initialize unique session 
ui  = str( uuid.uuid4())[:4]

api_key = Settings.ANTHROPIC_KEY.get_secret_value()

print(f"Starting new session: {ui}")


#2)creates relevant session directories and new folders

## Session directory
new_session_folder_dir = Path(__file__).parent / "session" / f"session_{ui}"
new_session_files = new_session_folder_dir / "files"
new_session_memory = new_session_folder_dir / "memory"
new_session_report_dir = new_session_folder_dir / "reports"

new_session_folder_dir.mkdir(exist_ok=True)
new_session_files.mkdir(exist_ok=True)
new_session_memory.mkdir(exist_ok=True)
new_session_report_dir.mkdir(exist_ok=True)

# Prompts and user input directories
prompts_dir = Path(__file__).parent / "prompts"
prompts_dir_str = str(prompts_dir)
user_input_dir = Path(__file__).parent.parent / "user_input"

print("Directories created")
print(str(new_session_folder_dir))
print(new_session_folder_dir)

#3) Loads prompts for lead agend and subagents and ads user input

## Load prompts from text files
lead_agent_prompt = (prompts_dir / "lead_agent_prompt_workaround.txt").read_text(encoding = "utf-8")

#4) Load files into session files directory

#4.1 csv data copy
src_csv = user_input_dir / "sessions_dec_2024.csv" #test file path / should come from Database down the line
dst_csv = new_session_files / "sessions_dec_2024.csv" #copy to session files directory

#4.2 user input copy

user_input_json = user_input_dir / "user_input.json"
dst_json = new_session_files / "user_input.json"


#4.3 copy prompts to session directory for record keeping
csv_analyzer_prompt_src = prompts_dir / "csv_analyzer_prompt.txt"
hypothesis_generator_prompt_src = prompts_dir / "hypothesis_generator_prompt.txt"
analyst_prompt_src = prompts_dir / "analyst_prompt.txt"
report_generator_prompt_src = prompts_dir / "report_generator_prompt.txt"

csv_analyzer_prompt_dst = new_session_files / "csv_analyzer_prompt.txt"
hypothesis_generator_prompt_dst = new_session_files / "hypothesis_generator_prompt.txt"    
analyst_prompt_dst = new_session_files / "analyst_prompt.txt"
report_generator_prompt_dst = new_session_files / "report_generator_prompt.txt"

if src_csv.exists():
    shutil.copy2(src_csv, dst_csv)
    shutil.copy2(user_input_json, dst_json)
    shutil.copy2(csv_analyzer_prompt_src, csv_analyzer_prompt_dst)
    shutil.copy2(hypothesis_generator_prompt_src, hypothesis_generator_prompt_dst)
    shutil.copy2(analyst_prompt_src, analyst_prompt_dst)
    shutil.copy2(report_generator_prompt_src, report_generator_prompt_dst)

    print(f"Copied {src_csv} to {dst_csv}")
    print(f"Copied {user_input_json} to {dst_json}")
    print(f"Copied prompts to {new_session_folder_dir}")

else:
    raise FileNotFoundError(f"Missing {src_csv}")


#5) Set up Claude Options and Model


options = ClaudeAgentOptions(
    permission_mode="bypassPermissions",
    system_prompt=lead_agent_prompt,
    allowed_tools=["Task","Glob", "Read"],
    agents={},
    model="haiku",
    cwd=str(new_session_folder_dir)
)

async def run_agent():
    attempts = 0
    try:
        async with ClaudeSDKClient(options=options) as client:
            while attempts < 1: 
                await client.query(prompt="Start the workflow defined in the system prompt.")

                async for msg in client.receive_response():
                    if type(msg).__name__ == 'AssistantMessage':
                        print(msg)

                attempts += 1

    finally:
        print("Agent session ended.")

if __name__ == "__main__":
    asyncio.run(run_agent())