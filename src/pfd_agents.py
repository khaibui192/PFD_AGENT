from agents import Agent
from src.prompts.agent_prompts import CLASSIFIER_AGENT_PROMPT

classifier_agent = Agent(name="classifier_agent",
                   model="gpt-4o-mini",
                   instructions=CLASSIFIER_AGENT_PROMPT)