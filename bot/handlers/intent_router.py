"""
Intent router for natural language queries.

Uses the LLM to interpret user messages and route to the appropriate tools.
This is the core of Task 3 - plain text intent routing.
"""

import httpx
from config import load_config
from services.lms_api import create_lms_client
from services.llm_client import create_llm_client, SYSTEM_PROMPT


# Fallback response for when LLM is unavailable
FALLBACK_MESSAGE = """I'm having trouble connecting to my AI assistant right now. 

Here's what I can help you with:
• List available labs: "what labs are available?"
• Show scores: "show me scores for lab 4"
• Compare pass rates: "which lab has the lowest pass rate?"
• Find top students: "who are the top 5 students in lab 4?"
• Check group performance: "which group is best in lab 3?"

You can also use commands: /help, /labs, /scores <lab>"""


def route_intent(message: str) -> str:
    """
    Route a natural language message through the LLM intent router.
    
    This function:
    1. Creates API clients for LMS and LLM
    2. Sends the message to the LLM with tool definitions
    3. LLM decides which tools to call
    4. Tools are executed and results fed back
    5. LLM produces a final answer
    
    Args:
        message: User's natural language message
        
    Returns:
        Response text from the LLM
    """
    config = load_config()
    
    # Check if LLM is configured
    if not config.llm_api_key or not config.llm_api_base_url or not config.llm_api_model:
        return FALLBACK_MESSAGE
    
    # Create clients
    api_client = create_lms_client(config.lms_api_url, config.lms_api_key)
    llm_client = create_llm_client(
        config.llm_api_key,
        config.llm_api_base_url,
        config.llm_api_model,
    )
    
    try:
        # Route through LLM tool-calling loop
        response = llm_client.route(message, api_client)
        return response
    except httpx.ConnectError as e:
        # LLM service unreachable
        return f"LLM service unavailable: {str(e)}\n\n{FALLBACK_MESSAGE}"
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            return "LLM authentication failed (401). The API token may have expired.\n\n" + FALLBACK_MESSAGE
        return f"LLM error: HTTP {e.response.status_code}\n\n{FALLBACK_MESSAGE}"
    except Exception as e:
        return f"LLM error: {str(e)}\n\n{FALLBACK_MESSAGE}"


def handle_natural_language(message: str) -> str:
    """
    Handle natural language input (alias for route_intent).
    
    This is the main entry point for non-command messages.
    """
    return route_intent(message)
