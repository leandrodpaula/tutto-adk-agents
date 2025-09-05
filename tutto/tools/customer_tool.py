import logging
from google.adk.tools import ToolContext
import requests
from typing import Optional
from tutto.config.settings import Settings

from tutto.tools.utils.database import MongoDatabase

logger = logging.getLogger(__name__)

def get_customer_byid_tool(id: str, tool_context: ToolContext) -> dict:
    logger.info(f"Getting customer by id: {id}")
    customer = MongoDatabase.find("customers", query={"_id": id})
    if customer:
        logger.info(f"Successfully fetched customer data for id {id}")
        return customer[0]
    else:
        logger.error(f"No customer found with id {id}")
        return {}

def get_customer_byphone_tool(phone: str, tool_context: ToolContext) -> list[dict]:
    logger.info(f"Getting customer by phone: {phone}")
    customers = MongoDatabase.find("customers", query={"phone": phone})
    if customers:
        logger.info(f"Successfully fetched customer data for phone {phone}")
        return customers
    else:
        logger.error(f"No customers found with phone {phone}")
        return []

def create_customer_tool(name: str, phone: str, tool_context: ToolContext) -> dict:
    logger.info(f"Creating customer with name: {name}, phone: {phone}")
    new_customer = {"name": name, "phone": phone, "_id": phone}


    result = MongoDatabase.insert_one("customers", new_customer)
    if result.acknowledged:
        logger.info(f"Successfully created customer with id {result.inserted_id}")
        return {"_id": str(result.inserted_id), "name": name, "phone": phone}
    else:
        logger.error("Failed to create customer")
        return {}
    

def update_customer_tool(id: str, name: Optional[str], phone: Optional[str], email: Optional[str], address: Optional[dict], tool_context: ToolContext) -> dict:
    logger.info(f"Updating customer with id: {id}")
    update_fields = {}
    if name:
        update_fields["name"] = name
    if phone:
        update_fields["phone"] = phone
    if email:
        update_fields["email"] = email
    if address:
        update_fields["address"] = address

    if update_fields:
        result = MongoDatabase.update_one("customers", query={"_id": id}, update=update_fields)
        if result.modified_count > 0:
            logger.info(f"Successfully updated customer with id {id}")
            return {"_id": id, **update_fields}
        else:
            logger.error(f"Failed to update customer with id {id}")
            return {}
    else:
        logger.warning(f"No update fields provided for customer with id {id}")
        return {}