from datetime import datetime, timedelta
import logging
from google.adk.tools import ToolContext
import requests
from typing import Optional
from ..config.settings import Settings

from .utils.database import MongoDatabase

logger = logging.getLogger(__name__)




def get_calendars_within_date_range_tool(customer_id: str, start_date: str, end_date: str, tool_context: ToolContext) -> list[dict]:
    logger.info(f"Getting calendars for customer_id: {customer_id} between {start_date} and {end_date}")

    calendar = MongoDatabase.find("calendars", query={"customer_id": customer_id, "active": True, "start_date": {"$gte": datetime.fromisoformat(start_date)}, "end_date": {"$lte": datetime.fromisoformat(end_date)}})
    if calendar:
        logger.info(f"Successfully fetched calendar data for customer_id {customer_id} between {start_date} and {end_date}")
        return calendar
    else:
        logger.error(f"No calendars found with customer_id {customer_id} between {start_date} and {end_date}")
        return []



