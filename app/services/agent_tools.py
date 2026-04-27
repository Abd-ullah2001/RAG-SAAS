import json
import logging
from typing import List, Dict, Any
from app.services.google_sheets import GoogleSheetsService

logger = logging.getLogger(__name__)

# Define the tools available to the LLM
# NVIDIA NIM (Llama-3.1) supports OpenAI-compatible tool definitions

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_google_sheets",
            "description": "List all Google Sheets available in the user's connected Google Drive.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_google_sheet",
            "description": "Read data from a specific Google Sheet and range.",
            "parameters": {
                "type": "object",
                "properties": {
                    "spreadsheet_id": {
                        "type": "string",
                        "description": "The ID of the Google Spreadsheet"
                    },
                    "range_name": {
                        "type": "string",
                        "description": "The range to read, e.g., 'Sheet1!A1:D10' or just 'Sheet1'"
                    }
                },
                "required": ["spreadsheet_id", "range_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "append_row_to_sheet",
            "description": "Append a new row of data to a specific Google Sheet.",
            "parameters": {
                "type": "object",
                "properties": {
                    "spreadsheet_id": {
                        "type": "string",
                        "description": "The ID of the Google Spreadsheet"
                    },
                    "range_name": {
                        "type": "string",
                        "description": "The range or sheet name where the row should be appended, e.g., 'Sheet1'"
                    },
                    "values": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "An array of values representing the new row, e.g., ['Dinner', '50.00', 'Food']"
                    }
                },
                "required": ["spreadsheet_id", "range_name", "values"]
            }
        }
    }
]

async def execute_tool(user_id: str, tool_call: Dict[str, Any]) -> str:
    """Execute a specific tool call and return the result as a string."""
    function_name = tool_call["function"]["name"]
    arguments = json.loads(tool_call["function"]["arguments"])
    
    logger.info(f"Agent executing tool: {function_name} with args {arguments} for user {user_id}")
    
    try:
        sheets_service = GoogleSheetsService(user_id=user_id)
    except Exception as e:
        return f"Error initializing Google Sheets service: {e}. The user might need to connect their Google account."

    try:
        if function_name == "list_google_sheets":
            sheets = sheets_service.list_spreadsheets()
            if not sheets:
                return "No spreadsheets found in your Google Drive."
            return json.dumps([{"id": s["id"], "name": s["name"]} for s in sheets])
            
        elif function_name == "read_google_sheet":
            data = sheets_service.get_sheet_data(arguments["spreadsheet_id"], arguments["range_name"])
            if not data:
                return "The specified sheet range is empty or could not be read."
            return json.dumps(data)
            
        elif function_name == "append_row_to_sheet":
            success = sheets_service.append_row(arguments["spreadsheet_id"], arguments["range_name"], arguments["values"])
            if success:
                return f"Successfully appended row {arguments['values']} to sheet."
            else:
                return "Failed to append row. Ensure the sheet exists and the agent has edit permissions."
                
        else:
            return f"Error: Tool '{function_name}' is not recognized."
            
    except Exception as e:
        logger.error(f"Error executing tool {function_name}: {e}")
        return f"An error occurred while executing the tool: {str(e)}"
