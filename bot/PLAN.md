# Bot Development Plan

## Overview

This document outlines the development plan for the LMS Telegram bot. The bot provides students with access to their learning management system data through Telegram, including lab status, scores, and backend health checks.

## Architecture

### Testable Handler Architecture (Separation of Concerns)

The core architectural decision is to separate handlers from the Telegram transport layer. Handlers are pure functions that take input and return text responses. They have no dependency on Telegram, which means:

1. **Test mode**: Handlers can be called directly via `--test` flag without connecting to Telegram
2. **Unit tests**: Handlers can be tested in isolation with pytest
3. **Telegram integration**: The same handler functions are called when Telegram receives a message

This pattern is called **separation of concerns** — business logic (handlers) is decoupled from infrastructure (Telegram client).

### Project Structure

```
bot/
├── bot.py              # Entry point: --test mode + Telegram startup
├── config.py           # Environment variable loading with pydantic-settings
├── handlers/
│   ├── __init__.py     # Handler exports
│   └── commands.py     # Command handler implementations
├── services/
│   ├── __init__.py     # Service exports
│   ├── api_client.py   # LMS API client (Task 2)
│   └── llm_client.py   # LLM client for intent routing (Task 3)
├── pyproject.toml      # Bot dependencies
└── PLAN.md             # This file
```

## Task Breakdown

### Task 1: Scaffold (Current)

- Create directory structure
- Implement `--test` mode
- Create placeholder handlers for `/start`, `/help`, `/health`, `/labs`, `/scores`
- Set up `pyproject.toml` with dependencies
- Create `.env.bot.secret` configuration

### Task 2: Backend Integration

- Implement `services/api_client.py` with Bearer token authentication
- Connect handlers to the LMS API
- `/health` returns actual backend status
- `/labs` returns real lab data from `GET /items/`
- `/scores` queries the backend for student scores
- Handle API errors gracefully (timeouts, 401, 500)

### Task 3: Intent Routing with LLM

- Implement `services/llm_client.py` for LLM API calls
- Create an intent router that uses the LLM to classify user messages
- Define tool descriptions for each handler (e.g., "Get lab status", "Check scores")
- The LLM reads tool descriptions and decides which to call based on user input
- Support natural language queries like "what labs are available" or "show my scores for lab 04"

**Key insight**: The LLM routing quality depends on tool description quality, not prompt engineering. Clear, specific tool descriptions help the LLM make correct decisions.

### Task 4: Docker Deployment

- Create `Dockerfile` for the bot
- Add bot service to `docker-compose.yml`
- Configure Docker networking (containers use service names, not `localhost`)
- Set up health checks and restart policies
- Deploy to VM and verify with autochecker

## Testing Strategy

1. **Test mode**: Manual testing via `uv run bot.py --test "/command"`
2. **Unit tests**: pytest tests for individual handlers
3. **Integration tests**: Test API client with mocked backend
4. **Telegram testing**: Manual testing in Telegram after deployment

## Deployment Checklist

- [ ] `.env.bot.secret` exists on VM with all required values
- [ ] Bot token is valid (from @BotFather)
- [ ] LMS_API_URL points to deployed backend (`http://localhost:42002`)
- [ ] LMS_API_KEY matches backend configuration
- [ ] LLM_API_KEY and LLM_API_BASE_URL are configured (for Task 3)
- [ ] Bot process is running (`ps aux | grep bot.py`)
- [ ] Bot responds to `/start` in Telegram

## Future Improvements

- Add conversation state management for multi-turn dialogs
- Implement caching for API responses to reduce latency
- Add logging and monitoring for production debugging
- Support inline queries for quick lookups
