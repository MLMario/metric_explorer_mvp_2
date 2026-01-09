import asyncio
import os
from pathlib import Path
import sys
import uuid
from datetime import date
import shutil
import json

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AgentDefinition, HookMatcher, query

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Settings


#1 )initialize unique session 
ui  = str( uuid.uuid4())[:4]
today_date = date.today().isoformat() 
api_key = Settings.ANTHROPIC_KEY.get_secret_value()


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
user_input_dir = Path(__file__).parent.parent / "user_input"


#3) Loads prompts for lead agend and subagents and ads user input

## Load prompts from text files
lead_agent_prompt = (prompts_dir / "lead_agent_prompt.txt").read_text(encoding = "utf-8")
csv_analyzer_prompt = (prompts_dir / "csv_analyzer_prompt.txt").read_text(encoding = "utf-8")
hypothesis_generator_prompt = (prompts_dir / "hypothesis_generator_prompt.txt").read_text(encoding = "utf-8")    
analyst_prompt = (prompts_dir / "analyst_prompt.txt").read_text(encoding = "utf-8")
report_generator_prompt = (prompts_dir / "report_generator_prompt.txt").read_text(encoding = "utf-8")

##loads user input from json file

with open(user_input_dir / 'user_input.json', 'r', encoding="utf-8") as f:
    user_input = json.load(f)

ui_business_context= user_input.get('business_context','Not Provided'),
ui_target_metric=user_input.get('target_metric','Not Provided'),
ui_target_metric_calculation=user_input.get('target_metric_calculation','Not Provided'),
ui_change_to_analyse=user_input.get('change_to_analyse','Not Provided'),
ui_why_is_this_suspicious=user_input.get('why_is_this_suspicious','Not Provided'),
ui_date_of_change=user_input.get('date_of_change','Not Provided'),
ui_potential_explanation=user_input.get('potential_explanation','Not Provided'),
ui_suggested_analysis=user_input.get('suggested_analysis','Not Provided'),

##Updates Prompts with user input

csv_analyzer_prompt = csv_analyzer_prompt.format(
    business_context=ui_business_context,
    target_metric=ui_target_metric,
    target_metric_calculation=ui_target_metric_calculation,
    change_to_analyse=ui_change_to_analyse,
    why_is_this_suspicious=ui_why_is_this_suspicious,
    date_of_change=ui_date_of_change,
    potential_explanation=ui_potential_explanation,
    suggested_analysis=ui_suggested_analysis,
)

hypothesis_generator_prompt = csv_analyzer_prompt.format(
    business_context=ui_business_context,
    target_metric=ui_target_metric,
    target_metric_calculation=ui_target_metric_calculation,
    change_to_analyse=ui_change_to_analyse,
    why_is_this_suspicious=ui_why_is_this_suspicious,
    date_of_change=ui_date_of_change,
    potential_explanation=ui_potential_explanation,
    suggested_analysis=ui_suggested_analysis,
)

analyst_prompt = csv_analyzer_prompt.format(
    business_context=ui_business_context,
    target_metric=ui_target_metric,
    target_metric_calculation=ui_target_metric_calculation,
    change_to_analyse=ui_change_to_analyse,
    why_is_this_suspicious=ui_why_is_this_suspicious,
    date_of_change=ui_date_of_change,
    potential_explanation=ui_potential_explanation,
    suggested_analysis=ui_suggested_analysis,
)

report_generator_prompt = csv_analyzer_prompt.format(
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
shutil.copy2(src_csv, dst_csv)