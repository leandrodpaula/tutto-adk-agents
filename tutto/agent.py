from google.adk.agents import Agent
from .prompts.base_instruction import BASE_INSTRUCTION
from .tools.customer_tool import get_customer_byid_tool, get_customer_byphone_tool
import logging

from .tools.history_tool import save_history_context, load_history_context

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Initializing Tutto agent")
root_agent = Agent(
    name="Tutto",
    model="gemini-2.0-flash",
    description="Tutto assistente de Agendamento e Organização",
    instruction=BASE_INSTRUCTION,
    tools=[
        get_customer_byid_tool,
        get_customer_byphone_tool,
        load_history_context,
    ],
    after_agent_callback=save_history_context,
    
)

