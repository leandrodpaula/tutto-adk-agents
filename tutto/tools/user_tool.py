import logging
from google.adk.tools import ToolContext
import requests
from typing import Optional
from ..config.settings import Settings

from .utils.database import MongoDatabase

logger = logging.getLogger(__name__)

def get_user_tool(id: str, tool_context: ToolContext) -> dict:
    logger.info(f"Getting user by id: {id}")
    user = MongoDatabase.find("users", query={"_id": id})
    if user:
        logger.info(f"Successfully fetched user data for id {id}")
        return user[0]
    else:
        logger.error(f"No user found with id {id}")
        return {}

def get_user_byphone_tool(phone: str, customer_id:str, tool_context: ToolContext) -> list[dict]:
    logger.info(f"Getting user by phone: {phone}, customer_id: {customer_id}")
    users = MongoDatabase.find("users", query={"phone": phone, "customer_id": customer_id})
    if users:
        logger.info(f"Successfully fetched user data for phone {phone}")
        return users
    else:
        logger.error(f"No users found with phone {phone}")
        return []

def create_user_tool(name: str, phone: str, customer_id: str, tool_context: ToolContext) -> dict:
    logger.info(f"Creating user with name: {name}, phone: {phone}, customer_id: {customer_id}")
    new_user = {"name": name, "phone": phone,  "customer_id": customer_id}

    user = get_user_byphone_tool(phone, customer_id, tool_context)
    if user:
        logger.warning(f"User with phone {phone} already exists for customer_id {customer_id}")
        return user[0]["_id"]

    result = MongoDatabase.insert_one("users", new_user)
    if result.acknowledged:
        logger.info(f"Successfully created user with id {result.inserted_id}")
        return {"_id": str(result.inserted_id), "name": name, "phone": phone, "customer_id": customer_id}
    else:
        logger.error("Failed to create user")
        return {}
    

def update_user_tool(id: str, name: Optional[str], phone: Optional[str], email: Optional[str], address: Optional[dict], customer_id: Optional[str], tool_context: ToolContext) -> dict:
    logger.info(f"Updating user with id: {id}")
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