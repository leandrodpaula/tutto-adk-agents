from google.adk.agents import Agent
from .tools.customer_tool import get_customer_byid_tool, get_customer_instructions
import logging

from .tools.history_tool import save_history_context
from google.adk.sessions import DatabaseSessionService
# Example using a local SQLite file:
db_url = "sqlite:///./my_agent_data.db"
session_service = DatabaseSessionService(db_url=db_url)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Read Prompt of File
with open("./tutto/prompts/tutto.prompt", "r") as f:
    BASE_INSTRUCTION = f.read()

logger.info("Initializing Tutto agent")
root_agent = Agent(
    name="Tutto",
    model="gemini-2.0-flash",
    description="Tutto assistente de Agendamento e Organização",
    instruction=BASE_INSTRUCTION,
    tools=[
        get_customer_byid_tool,
        get_customer_instructions
    ],
    after_agent_callback=save_history_context,
    
)


