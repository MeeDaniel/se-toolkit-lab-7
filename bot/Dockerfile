# Bot Dockerfile
# Uses uv for dependency management (not pip/requirements.txt)

FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy pyproject.toml and uv.lock for dependency installation
COPY pyproject.toml uv.lock ./

# Install dependencies using uv (creates .venv)
RUN uv sync --no-dev

# Copy bot source code (but not .venv - that's created by uv sync)
COPY bot.py ./
COPY handlers/ ./handlers/
COPY services/ ./services/
COPY config.py ./

# Set environment variables
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run the bot
CMD ["python", "bot.py"]
