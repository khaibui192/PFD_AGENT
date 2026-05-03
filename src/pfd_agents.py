from agents import Agent
from src.prompts.fuel_cell_prompts import SYSTEM_PROMPT
from src.prompts.agent_prompts import ROOT_AGENT_PROMPT, INSPECTION_AGENT_PROMPT, PFD_AGENT_PROMPT, CLASSIFIER_AGENT_PROMPT


classifier_agent = Agent(name="classifier_agent",
                   model="gpt-4o-mini",
                   instructions=CLASSIFIER_AGENT_PROMPT)

inspection_agent = Agent(name="inspector_agent", 
                   model="gpt-4o-mini", 
                   instructions=INSPECTION_AGENT_PROMPT)

pfd_agent = Agent(name="pfd_reader_agent", 
                   model="gpt-4o-mini", 
                   instructions=PFD_AGENT_PROMPT + SYSTEM_PROMPT)

root_agent = Agent(name="root_agent", 
                   model="gpt-4o-mini", 
                   instructions=ROOT_AGENT_PROMPT + SYSTEM_PROMPT,
                #    handoffs=[classifier_agent, pfd_agent, inspection_agent],
                #    tools=[root_pipeline]
                   )