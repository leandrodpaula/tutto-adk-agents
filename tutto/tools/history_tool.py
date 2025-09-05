import logging
from datetime import datetime, timedelta
from google.adk.agents.callback_context import CallbackContext

from google.adk.tools import ToolContext
from tutto.tools.utils.database import MongoDatabase

logger = logging.getLogger(__name__)


def save_history_context(callback_context: CallbackContext):
    logger.info("Saving history context")

    session = callback_context._invocation_context.session


    if not session:
        logger.error("No session found in callback context")
        return

    five_minutes_ago = datetime.now() - timedelta(minutes=5)

    logger.info(f"Five minutes ago: {five_minutes_ago}")

    events = [event for event in session.events if datetime.fromtimestamp(event.timestamp) >= five_minutes_ago]
    logger.info(f"Found {len(events)} events in the last 5 minutes with session id {session.id}")

    for event in events:
        result = MongoDatabase.find("conversation_history", query={"_id": event.id})
        if not result:
            logger.info(f"Saving event with id {event.id} to database")
            if event.content and event.content.parts:
                for part in event.content.parts:
                    for key, value in part.model_dump().items():
                        if value:
                            history = {
                                "_id": event.id,
                                "session_id": session.id,
                                "user_id": session.user_id,
                                "agent_name": callback_context.agent_name,
                                "timestamp": datetime.fromtimestamp(event.timestamp),
                                "message": {
                                    "type": key,
                                    "content":value
                                },
                                "author": event.author

                            }

                    
                            result = MongoDatabase.insert_one("conversation_history", history)
                            if result.acknowledged:
                                logger.info(f"Successfully saved history with id {result.inserted_id}")
                            else:
                                logger.error("Failed to save history")





def load_history_context(tool_context: ToolContext):
    logger.info("Loading history context")

    session = tool_context._invocation_context.session
    if not session:
        logger.error("No session found in callback context")
        return
    

    query = {}
    

    if session.user_id:
        query["user_id"] = session.user_id

    if session.id:
        query["session_id"] = session.id

    query["timestamp"] = { "$gt": (datetime.now() - timedelta(days=90)) }

    # Load last 10 messages 
    history_records = MongoDatabase.find("conversation_history", query=query, sort=[("timestamp", -1)], limit=100)
    history_records = sorted(history_records, key=lambda x: x["timestamp"])
    return history_records