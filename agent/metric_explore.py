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
lead_agent_prompt = (prompts_dir / "lead_agent_prompt.txt").read_text(encoding = "utf-8")

## Generate templates to then replace user values
csv_analyzer_template = Template((prompts_dir / "csv_analyzer_prompt.txt").read_text(encoding = "utf-8"))
hypothesis_generator_template = Template((prompts_dir / "hypothesis_generator_prompt.txt").read_text(encoding = "utf-8"))    
analyst_template = Template((prompts_dir / "analyst_prompt.txt").read_text(encoding = "utf-8"))
report_generator_template = Template((prompts_dir / "report_generator_prompt.txt").read_text(encoding = "utf-8"))

##loads user input from json file

with open(user_input_dir / 'user_input.json', 'r', encoding="utf-8") as f:
    user_input = json.load(f)


ui_business_context = user_input.get('business_context', 'Not Provided')
ui_target_metric = user_input.get('target_metric', 'Not Provided')
ui_target_metric_calculation = user_input.get('target_metric_calculation', 'Not Provided')
ui_change_to_analyse = user_input.get('change_to_analyse', 'Not Provided')
ui_why_is_this_suspicious = user_input.get('why_is_this_suspicious', 'Not Provided')
ui_date_of_change = user_input.get('date_of_change', 'Not Provided')
ui_potential_explanation = user_input.get('potential_explanation', 'Not Provided')
ui_suggested_analysis = user_input.get('suggested_analysis', 'Not Provided')

##Updates Prompts with user input

csv_analyzer_prompt = csv_analyzer_template.substitute(
    business_context=ui_business_context,
    target_metric=ui_target_metric,
    target_metric_calculation=ui_target_metric_calculation,
    change_to_analyse=ui_change_to_analyse,
    why_is_this_suspicious=ui_why_is_this_suspicious,
    date_of_change=ui_date_of_change,
    potential_explanation=ui_potential_explanation,
    suggested_analysis=ui_suggested_analysis,
)

hypothesis_generator_prompt = hypothesis_generator_template.substitute(
    business_context=ui_business_context,
    target_metric=ui_target_metric,
    target_metric_calculation=ui_target_metric_calculation,
    change_to_analyse=ui_change_to_analyse,
    why_is_this_suspicious=ui_why_is_this_suspicious,
    date_of_change=ui_date_of_change,
    potential_explanation=ui_potential_explanation,
    suggested_analysis=ui_suggested_analysis,
)

analyst_prompt = analyst_template.substitute(
    business_context=ui_business_context,
    target_metric=ui_target_metric,
    target_metric_calculation=ui_target_metric_calculation,
    change_to_analyse=ui_change_to_analyse,
    why_is_this_suspicious=ui_why_is_this_suspicious,
    date_of_change=ui_date_of_change,
    potential_explanation=ui_potential_explanation,
    suggested_analysis=ui_suggested_analysis,
)

report_generator_prompt = report_generator_template.substitute(
    business_context=ui_business_context,
    target_metric=ui_target_metric,
    target_metric_calculation=ui_target_metric_calculation,
    change_to_analyse=ui_change_to_analyse,
    why_is_this_suspicious=ui_why_is_this_suspicious,
    date_of_change=ui_date_of_change,
    potential_explanation=ui_potential_explanation,
    suggested_analysis=ui_suggested_analysis,
)


#4) Load files into session files directory

src_csv = user_input_dir / "sessions_dec_2024.csv" #test file path / should come from Database down the line
dst_csv = new_session_files / "sessions_dec_2024.csv" #copy to session files directory
if src_csv.exists():
    shutil.copy2(src_csv, dst_csv)
else:
    raise FileNotFoundError(f"Missing {src_csv}")


#5) Set up Claude Subsgent Options and Model

agents = {
    "csv_analyzer": AgentDefinition(
        description=(
            f"Validates CSV files and documents the data model. Reads files from /files, checks for target metric data, and outputs data_model.md to /memory."
        ),
        tools=["Glob", "Read", "Write"],
        prompt= f"Read csv_analyzer_prompt.txt inside prompts folder locate at {prompts_dir_str}",
        model="haiku"

    ),
    "hypothesis_generator": AgentDefinition(
        description=(
            f"Generates testable hypotheses explaining the metric change. Reads data_model.md from /memory and outputs hypothesis.json to /memory."
        ),
        tools=["Glob", "Read", "Write"],
        prompt= hypothesis_generator_prompt,
        model="haiku"
    ),
    "analyst": AgentDefinition(
        description=(
            "Tests a single hypothesis through iterative data analysis using Python/pandas. Reads data from /files, outputs finding_*.json to /memory."
        ),
        tools=["Glob", "Read", "Write","Bash"],
        prompt= analyst_prompt,
        model="sonnet"
    ),
    "report_generator": AgentDefinition(
        description=(
            "Compiles all findings into final reports. Reads finding_*.json files from /memory, outputs findings.md and user_report.md to /memory"
        ),
        tools=["Glob", "Read", "Write"],
        prompt= report_generator_prompt,
        model="haiku"
    )
}

options = ClaudeAgentOptions(
    permission_mode="bypassPermissions",
    system_prompt=lead_agent_prompt,
    allowed_tools=["Task","Glob", "Read"],
    agents=agents,
    model="haiku",
    cwd=str(new_session_folder_dir)
)

print(f"Registered agents: {list(agents.keys())}")  # Debug line
#print(f"Options agents: {options.agents}")
#print(f"Options model: {options.model}")



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