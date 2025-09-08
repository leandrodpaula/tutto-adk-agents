import logging
from google.adk.tools import ToolContext
import requests
from typing import Optional
from ..config.settings import Settings

from  .utils.database import MongoDatabase

logger = logging.getLogger(__name__)

def get_customer_byid_tool(tool_context: ToolContext) -> dict:

    customer_id  = tool_context._invocation_context.session.state.get("customer_id", None)
    if customer_id:
        logger.info(f"Getting customer by id: {customer_id}")
        customer = MongoDatabase.find_one("customers", query={"_id": customer_id})
        if customer:
            logger.info(f"Successfully fetched customer data for id {customer_id}")
            return customer
        else:
            logger.error(f"No customer found with id {customer_id}")
            return {}
    return {}
    
def get_customer_instructions(tool_context: ToolContext) -> Optional[list[dict]]:
    customer_id  = tool_context._invocation_context.session.state.get("customer_id", None)
    if customer_id:
        logger.info(f"Getting customer instructions by id: {customer_id}")
        instructions = MongoDatabase.find("instructions", query={"customer_id": customer_id})
        if instructions and len(instructions) > 0:
            logger.info(f"Successfully fetched instructions for customer id {customer_id}")
            return instructions
        else:
            logger.warning(f"No instructions found for customer id {customer_id}")
            return []

    return None