"""
Command handler implementations.

Each handler is a pure function that returns a text response.
"""

import httpx
from config import load_config
from services.lms_api import create_lms_client


def handle_start() -> str:
    """Handle /start command."""
    config = load_config()
    return "Welcome! I'm your LMS assistant bot. Use /help to see available commands."


def handle_help() -> str:
    """Handle /help command."""
    return """Available commands:
/start - Start the bot
/help - Show this help message
/health - Check backend status
/labs - List available labs
/scores <lab> - View pass rates for a lab (e.g., /scores lab-04)"""


def handle_health() -> str:
    """Handle /health command."""
    config = load_config()
    client = create_lms_client(config.lms_api_url, config.lms_api_key)
    
    try:
        result = client.health_check()
        return f"Backend is healthy. {result['item_count']} items available."
    except httpx.ConnectError as e:
        return f"Backend error: connection refused ({config.lms_api_url}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        return f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
    except Exception as e:
        return f"Backend error: {str(e)}"


def handle_labs() -> str:
    """Handle /labs command."""
    config = load_config()
    client = create_lms_client(config.lms_api_url, config.lms_api_key)
    
    try:
        labs = client.get_labs()
        if not labs:
            return "No labs available."
        
        lines = ["Available labs:"]
        for lab in labs:
            title = lab.get("title", "Untitled")
            lines.append(f"- {title}")
        return "\n".join(lines)
    except httpx.ConnectError as e:
        return f"Backend error: connection refused ({config.lms_api_url}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        return f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
    except Exception as e:
        return f"Backend error: {str(e)}"


def handle_scores(arg: str) -> str:
    """Handle /scores command."""
    if not arg:
        return "Usage: /scores <lab> (e.g., /scores lab-04)"
    
    config = load_config()
    client = create_lms_client(config.lms_api_url, config.lms_api_key)
    
    try:
        pass_rates = client.get_pass_rates(arg)
        if not pass_rates:
            return f"No pass rate data found for '{arg}'."
        
        lines = [f"Pass rates for {arg}:"]
        for record in pass_rates:
            task_name = record.get("task", "Unknown task")
            avg_score = record.get("avg_score", 0)
            attempts = record.get("attempts", 0)
            lines.append(f"- {task_name}: {avg_score:.1f}% ({attempts} attempts)")
        return "\n".join(lines)
    except httpx.ConnectError as e:
        return f"Backend error: connection refused ({config.lms_api_url}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"No data found for lab '{arg}'. Check the lab ID (e.g., lab-04)."
        return f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
    except Exception as e:
        return f"Backend error: {str(e)}"
