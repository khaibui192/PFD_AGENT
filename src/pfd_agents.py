from agents import Agent
from pfd_system.src.prompts.fuel_cell_prompts import SYSTEM_PROMPT
from pfd_system.src.prompts.agent_prompts import ROOT_AGENT, INSPECTION_AGENT, PFD_AGENT

inspection_agent = Agent(name="Inspector agent", 
                   model="gpt-4o-mini", 
                   instructions=INSPECTION_AGENT)

pfd_reader_agent = Agent(name="PFD reader agent", 
                   model="gpt-4o-mini", 
                   instructions=PFD_AGENT)

root_agent = Agent(name="Root agent", 
                   model="gpt-4o-mini", 
                   instructions=ROOT_AGENT + SYSTEM_PROMPT,
                   handoffs=[inspection_agent, pfd_reader_agent])